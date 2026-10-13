# app/services/baseline.py
from app.services.ai import generate_answer


def answer_question_baseline(question: str) -> dict:
    """
    The no-retrieval baseline arm for the research comparison: asks Gemini
    the raw question directly, with no paper context and no grounding
    instructions — representing what a user gets from a plain LLM call
    with no RAG system in front of it.

    Returns the same shape as rag.answer_question() so the experiment
    runner can treat both arms identically: sources is always empty here
    since there's nothing to cite.
    """
    answer = generate_answer(question)
    return {
        "answer": answer,
        "sources": [],
    }