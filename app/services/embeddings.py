# app/services/embeddings.py
from google.genai.types import EmbedContentConfig
from app.services.ai import client

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768


def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """
    Generate a 768-dimension embedding for the given text using Gemini.

    task_type matters: use "RETRIEVAL_DOCUMENT" when embedding content to be
    stored and searched later (e.g. a paper's abstract), and
    "RETRIEVAL_QUERY" when embedding a user's question at search time.
    Mixing these up degrades retrieval quality even though both still
    return a valid vector.
    """
    if not text or not text.strip():
        raise ValueError("Text is empty")

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[text],
        config=EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )
    return result.embeddings[0].values