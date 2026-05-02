# app/services/ai.py
from google import genai
from app.core.config import settings

# New Google GenAI client
client = genai.Client(api_key=settings.OPENAI_API_KEY)

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
    # TODO: Replace with real AI when quota available
    return f"AI Summary: This paper explores {abstract[:100]}... [Full AI summary pending API quota]"
