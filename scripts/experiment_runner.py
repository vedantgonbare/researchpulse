# scripts/experiment_runner.py
"""
Runs the research comparison: for each question in eval_questions.json,
calls both the baseline (no-retrieval) arm and the RAG arm, and logs
results side by side in long format (one row per question+arm pair) to
eval_results.csv.

Run from project root: python scripts/experiment_runner.py
"""
import sys
import os
import csv
import json
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models import User, Paper
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


def run_arm(arm_name: str, question_id: str, question: str, fn) -> dict:
    """Times a single arm's call and builds one CSV row as a dict."""
    start = time.monotonic()
    result = fn()
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

    db = SessionLocal()
    try:
        # Hardcoded for now: testuser2 (id 3), the account holding the Day 9 eval papers.
        owner_id = db.query(User).filter(User.email == "testuser2@gmail.com").first().id
    finally:
        db.close()

    rows = []
    for item in questions:
        qid, question = item["id"], item["question"]
        print(f"Running {qid}: {question}")

        rows.append(run_arm(
            "baseline", qid, question,
            lambda: answer_question_baseline(question),
        ))

        db = SessionLocal()
        try:
            rows.append(run_arm(
                "rag", qid, question,
                lambda: answer_question(db, owner_id, question),
            ))
        finally:
            db.close()

    with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. {len(rows)} rows written to {RESULTS_FILE}")


if __name__ == "__main__":
    main()