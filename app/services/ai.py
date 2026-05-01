# app/services/ai.py
from openai import OpenAI
from app.core.config import settings

# Initialize OpenAI client using key from .env
client = OpenAI(api_key=settings.OPENAI_API_KEY)

SUMMARIZE_PROMPT = """You are a research assistant. Given the abstract of an academic paper, produce a concise 3-5 sentence plain-English summary. Focus on:
- What problem it solves
- Key method or approach
- Main findings or contributions

Abstract:
{abstract}

Summary:"""

def summarize_abstract(abstract: str) -> str:
    """
    Summarize a paper abstract using OpenAI GPT.
    Returns plain-English summary string.
    Raises ValueError if abstract is empty.
    """
    if not abstract or not abstract.strip():
        raise ValueError("Abstract is empty")

    prompt = SUMMARIZE_PROMPT.format(abstract=abstract)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.5
    )

    summary = response.choices[0].message.content.strip()
    return summary