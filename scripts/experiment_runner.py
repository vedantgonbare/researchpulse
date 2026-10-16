# scripts/experiment_runner.py
"""
Runs the research comparison: for each question in eval_questions.json,
calls both the baseline (no-retrieval) arm and the RAG arm, and logs
results side by side in long format (one row per question+arm pair) to
eval_results.csv.

Writes each row as it's produced (not all at once at the end), and skips
any (question_id, arm) pair already present in eval_results.csv — so a
run interrupted by a Gemini 503/429 can simply be re-run and will pick up
where it left off instead of losing earlier progress or duplicating rows.

Run from project root: python scripts/experiment_runner.py
"""
import sys
import os
import csv
import json
import time
from datetime import datetime, timezone

from google.genai.errors import ServerError, ClientError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models import User
from app.services.baseline import answer_question_baseline
from app.services.rag import answer_question

QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "eval_questions.json")
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "eval_results.csv")

FIELDNAMES = [
    "question_id",
    "question",
    "arm",
    "answer",
    "sources",
    "num_sources",
    "response_time_seconds",
    "timestamp",
]


def load_completed_pairs() -> set[tuple[str, str]]:
    """Reads eval_results.csv if it exists and returns the (question_id, arm)
    pairs already recorded, so a resumed run doesn't repeat completed work."""
    if not os.path.exists(RESULTS_FILE):
        return set()
    with open(RESULTS_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {(row["question_id"], row["arm"]) for row in reader}


def append_row(row: dict, write_header: bool) -> None:
    """Appends one row to eval_results.csv immediately, so progress survives
    a crash or interrupt partway through the run."""
    with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def run_arm(arm_name: str, question_id: str, question: str, fn) -> dict | None:
    """
    Times a single arm's call and builds one CSV row as a dict.
    Returns None (and prints a warning) instead of raising if Gemini fails
    after retries, so one bad call doesn't abort the whole run.
    """
    start = time.monotonic()
    try:
        result = fn()
    except (ServerError, ClientError) as e:
        print(f"  [{arm_name}] FAILED for {question_id}: {e}")
        return None
    elapsed = round(time.monotonic() - start, 2)

    sources = result.get("sources", [])
    source_titles = "; ".join(s["title"] for s in sources)

    return {
        "question_id": question_id,
        "question": question,
        "arm": arm_name,
        "answer": result["answer"],
        "sources": source_titles,
        "num_sources": len(sources),
        "response_time_seconds": elapsed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    completed = load_completed_pairs()
    write_header = not os.path.exists(RESULTS_FILE)

    db = SessionLocal()
    try:
        # Hardcoded for now: testuser2 (id 3), the account holding the eval papers.
        owner_id = db.query(User).filter(User.email == "testuser2@gmail.com").first().id
    finally:
        db.close()
    
    print(f"DEBUG: loaded {len(questions)} questions, {len(completed)} already completed")
    written = 0
    for item in questions:
        qid, question = item["id"], item["question"]

        if (qid, "baseline") not in completed:
            print(f"Running {qid} [baseline]: {question}")
            row = run_arm("baseline", qid, question, lambda: answer_question_baseline(question))
            if row:
                append_row(row, write_header)
                write_header = False
                written += 1
        else:
            print(f"Skipping {qid} [baseline] (already done)")

        if (qid, "rag") not in completed:
            print(f"Running {qid} [rag]: {question}")
            db = SessionLocal()
            try:
                row = run_arm("rag", qid, question, lambda: answer_question(db, owner_id, question))
            finally:
                db.close()
            if row:
                append_row(row, write_header)
                write_header = False
                written += 1
        else:
            print(f"Skipping {qid} [rag] (already done)")

    print(f"\nDone. {written} new rows written to {RESULTS_FILE}")

if __name__ == "__main__":
    main()