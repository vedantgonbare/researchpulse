# app/services/ai.py
from google import genai
from app.core.config import settings

# New Google GenAI client
client = genai.Client(api_key=settings.OPENAI_API_KEY)

GENERATION_MODEL = "gemini-flash-latest"

SUMMARIZE_PROMPT = """You are a research assistant. Given the abstract of an academic paper, produce a concise 3-5 sentence plain-English summary. Focus on:
- What problem it solves
- Key method or approach
- Main findings or contributions

Abstract:
{abstract}

Summary:"""


def summarize_abstract(abstract: str) -> str:
    if not abstract or not abstract.strip():
        raise ValueError("Abstract is empty")

    prompt = SUMMARIZE_PROMPT.format(abstract=abstract)
    return generate_answer(prompt)


def generate_answer(prompt: str) -> str:
    """
    Call Gemini to generate a free-text answer from a fully-constructed prompt.
    Used by rag.py's answer_question() — kept separate from summarize_abstract()
    so RAG generation and paper summarization remain independently testable.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt is empty")

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )
    return response.text