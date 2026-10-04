# app/services/rag.py
from sqlalchemy.orm import Session
from app.models.paper import Paper


def retrieve_relevant_papers(
    db: Session,
    owner_id: int,
    query_embedding: list[float],
    top_k: int = 5,
):
    """
    Find the top_k papers belonging to owner_id whose abstract embedding is most
    semantically similar to query_embedding, using cosine distance (pgvector's <=>).

    Returns a list of (Paper, distance) pairs, most similar first.
    distance is cosine distance: 0 = identical direction (most similar),
    2 = opposite direction (least similar) — lower is better.

    Papers with embedding = NULL (failed/pending embed) are excluded, since
    cosine_distance against NULL is undefined and would corrupt the ordering.
    """
    results = (
        db.query(Paper, Paper.embedding.cosine_distance(query_embedding).label("distance"))
        .filter(Paper.owner_id == owner_id)
        .filter(Paper.embedding.isnot(None))
        .order_by("distance")
        .limit(top_k)
        .all()
    )
    return results