# app/services/rag.py
from sqlalchemy.orm import Session
from app.models.paper import Paper
from app.services.embeddings import embed_text
from app.services.ai import generate_answer


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


def build_prompt(question: str, retrieved: list[tuple[Paper, float]]) -> str:
    """
    Construct a grounded prompt: instructs the model to answer ONLY from the
    given abstracts, and to say so explicitly if the answer isn't in them.
    This is what separates "RAG" from "an LLM that happened to see some text" —
    the instruction to stay grounded is doing real work, not just formatting.
    """
    if not retrieved:
        context = "No saved papers were found in the user's library."
    else:
        context = "\n\n".join(
            f"[Paper {i+1}] \"{paper.title}\"\n{paper.abstract}"
            for i, (paper, _distance) in enumerate(retrieved)
        )

    return f"""You are a research assistant answering questions using ONLY the paper abstracts provided below, from the user's own saved library.

Rules:
- Base your answer strictly on the content of these abstracts.
- If the abstracts don't contain enough information to answer, say so clearly instead of guessing.
- When you reference a specific claim, mention which paper it came from (e.g. "Paper 1").

Saved papers:
{context}

Question: {question}

Answer:"""


def answer_question(db: Session, owner_id: int, question: str, top_k: int = 5) -> dict:
    """
    Full RAG flow: embed the question, retrieve relevant papers, build a
    grounded prompt, and generate an answer.

    Returns a dict with the answer text plus the source papers used, so the
    caller (the /chat endpoint, eventually) can show citations.
    """
    query_embedding = embed_text(question, task_type="RETRIEVAL_QUERY")
    retrieved = retrieve_relevant_papers(db, owner_id, query_embedding, top_k=top_k)
    prompt = build_prompt(question, retrieved)
    answer = generate_answer(prompt)

    return {
        "answer": answer,
        "sources": [
            {"paper_id": paper.id, "title": paper.title, "distance": distance}
            for paper, distance in retrieved
        ],
    }