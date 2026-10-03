# scripts/backfill_embeddings.py
"""
One-off / periodic tool: find papers with no embedding and generate one.
Run manually: python scripts/backfill_embeddings.py
"""
import sys
import os
import time

# Allow running this script directly without installing the app as a package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.paper import Paper
from app.models.user import User
from app.services.embeddings import embed_text

BATCH_SLEEP_SECONDS = 1  # stay well under Gemini's free-tier 100 req/min cap


def backfill():
    db = SessionLocal()
    try:
        papers = db.query(Paper).filter(Paper.embedding.is_(None)).all()
        total = len(papers)
        print(f"Found {total} paper(s) missing an embedding.")

        if total == 0:
            print("Nothing to do.")
            return

        succeeded, failed = 0, 0
        for i, paper in enumerate(papers, start=1):
            print(f"[{i}/{total}] Embedding paper id={paper.id} ({paper.arxiv_id})...")
            try:
                paper.embedding = embed_text(paper.abstract, task_type="RETRIEVAL_DOCUMENT")
                db.commit()
                succeeded += 1
            except Exception as e:
                db.rollback()
                print(f"  FAILED: {e}")
                failed += 1
            time.sleep(BATCH_SLEEP_SECONDS)

        print(f"\nDone. {succeeded} succeeded, {failed} failed.")
    finally:
        db.close()


if __name__ == "__main__":
    backfill()