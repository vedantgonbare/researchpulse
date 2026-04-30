# app/services/ai.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SUMMARIZE_PROMPT = """You are a research assistant. Given the abstract of an academic paper, 
produce a concise 3-5 sentence plain-English summary. Focus on:
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
        raise ValueError("Abstract cannot be empty")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": SUMMARIZE_PROMPT.format(abstract=abstract.strip()),
            }
        ],
        temperature=0.3,
        max_tokens=300,
    )

    summary = response.choices[0].message.content
    return summary.strip() if summary else ""