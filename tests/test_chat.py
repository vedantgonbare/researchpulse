# tests/test_chat.py
from unittest.mock import patch

from tests.conftest import TestingSessionLocal
from app.models import User, Paper

FAKE_EMBEDDING = [0.1] * 768


def _get_user_id(email: str) -> int:
    """Look up a user's id directly from the test DB by email."""
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        return user.id
    finally:
        db.close()


def _insert_paper_with_embedding(owner_id: int) -> Paper:
    """Insert a paper that already has an embedding, bypassing embed_text()."""
    db = TestingSessionLocal()
    try:
        paper = Paper(
            arxiv_id="9999.99999",
            title="A Test Paper About Transformers",
            authors="Test Author",
            abstract="This paper discusses the attention mechanism in transformers.",
            url="https://arxiv.org/abs/9999.99999",
            owner_id=owner_id,
            embedding=FAKE_EMBEDDING,
        )
        db.add(paper)
        db.commit()
        db.refresh(paper)
        return paper
    finally:
        db.close()


def test_chat_requires_auth(client):
    """No Authorization header -> 401."""
    response = client.post("/chat/", json={"question": "What is attention?"})
    assert response.status_code == 401


def test_chat_empty_question(client, auth_headers):
    """Blank/whitespace question -> 400, per the explicit check in the route."""
    response = client.post("/chat/", json={"question": "   "}, headers=auth_headers)
    assert response.status_code == 400


@patch("app.services.rag.generate_answer")
@patch("app.services.rag.embed_text")
def test_chat_no_papers(mock_embed_text, mock_generate_answer, client):
    """
    A user with zero saved papers gets a graceful answer, not a crash.
    A dedicated user is registered here (instead of reusing auth_headers) so
    this test's result never depends on what other test files have already
    saved for the shared test user.
    """
    mock_embed_text.return_value = FAKE_EMBEDDING
    mock_generate_answer.return_value = "I don't have enough information to answer that."

    client.post(
        "/auth/register",
        json={
            "email": "no_papers_user@researchpulse.com",
            "username": "nopapersuser",
            "password": "testpass123",
        },
    )
    login = client.post(
        "/auth/login",
        json={"email": "no_papers_user@researchpulse.com", "password": "testpass123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.post(
        "/chat/", json={"question": "What is attention?"}, headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sources"] == []
    assert "answer" in data


@patch("app.services.rag.generate_answer")
@patch("app.services.rag.embed_text")
def test_chat_happy_path(mock_embed_text, mock_generate_answer, client, auth_headers):
    """
    With a real embedded paper in the DB and both Gemini calls mocked,
    /chat/ should return a grounded answer citing that paper as a source.
    """
    mock_embed_text.return_value = FAKE_EMBEDDING
    mock_generate_answer.return_value = "The paper discusses the attention mechanism. [Paper 1]"

    owner_id = _get_user_id("test@researchpulse.com")
    _insert_paper_with_embedding(owner_id)

    response = client.post(
        "/chat/",
        json={"question": "What does the paper say about attention?"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == mock_generate_answer.return_value
    assert len(data["sources"]) == 1
    assert data["sources"][0]["title"] == "A Test Paper About Transformers"

    mock_embed_text.assert_called_once()
    mock_generate_answer.assert_called_once()