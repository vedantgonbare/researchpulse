# app/services/arxiv.py
import httpx
import xml.etree.ElementTree as ET
from typing import Optional

# arXiv API base URL — free, no API key needed
ARXIV_BASE_URL = "http://export.arxiv.org/api/query"

# XML namespace used by arXiv response
NAMESPACE = "{http://www.w3.org/2005/Atom}"

async def fetch_paper_by_id(arxiv_id: str) -> Optional[dict]:
    """
    Fetch a single paper from arXiv using its ID.
    Example arxiv_id: "2301.07041" or "cs/0501030"
    """
    params = {
        "id_list": arxiv_id,
        "max_results": 1
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(ARXIV_BASE_URL, params=params)

    if response.status_code != 200:
        return None

    return parse_arxiv_response(response.text)


async def search_papers(query: str, max_results: int = 5) -> list[dict]:
    """
    Search arXiv papers by keyword.
    Example query: "machine learning transformer"
    """
    params = {
        "search_query": f"all:{query}",
        "max_results": max_results,
        "sortBy": "relevance"
    }

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(ARXIV_BASE_URL, params=params)

    if response.status_code != 200:
        return []

    return parse_arxiv_list_response(response.text)


def parse_arxiv_response(xml_text: str) -> Optional[dict]:
    """Parse single paper from arXiv XML response"""
    results = parse_arxiv_list_response(xml_text)
    return results[0] if results else None


def parse_arxiv_list_response(xml_text: str) -> list[dict]:
    """
    arXiv returns XML — we parse it into clean Python dicts.
    Each entry = one paper.
    """
    root = ET.fromstring(xml_text)
    papers = []

    for entry in root.findall(f"{NAMESPACE}entry"):
        # Extract arxiv ID from full URL
        # Full ID looks like: http://arxiv.org/abs/2301.07041v1
        full_id = entry.find(f"{NAMESPACE}id").text
        arxiv_id = full_id.split("/abs/")[-1].split("v")[0]  # clean ID only

        title = entry.find(f"{NAMESPACE}title").text.strip().replace("\n", " ")
        abstract = entry.find(f"{NAMESPACE}summary").text.strip().replace("\n", " ")

        # Authors — could be multiple
        authors = entry.findall(f"{NAMESPACE}author")
        author_names = [
            a.find(f"{NAMESPACE}name").text
            for a in authors
        ]
        authors_str = ", ".join(author_names)

        # Paper URL
        url = f"https://arxiv.org/abs/{arxiv_id}"

        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors_str,
            "abstract": abstract,
            "url": url
        })

    return papers