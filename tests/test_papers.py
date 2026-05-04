# tests/test_papers.py

def test_get_papers_authenticated(client, auth_headers):
    """Authenticated user can get their papers list."""
    response = client.get("/papers/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_papers_unauthenticated(client):
    """Unauthenticated request returns 401."""
    response = client.get("/papers/")
    assert response.status_code == 401

def test_search_papers(client):
    """Search endpoint returns results."""
    response = client.get("/papers/search?q=machine+learning")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0

def test_get_digest_authenticated(client, auth_headers):
    """Authenticated user can get digest."""
    response = client.get("/papers/digest", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_unread" in data
    assert "papers" in data

def test_update_nonexistent_paper(client, auth_headers):
    """Updating non-existent paper returns 404."""
    response = client.patch(
        "/papers/99999",
        json={"tags": "test"},
        headers=auth_headers
    )
    assert response.status_code == 404

def test_delete_nonexistent_paper(client, auth_headers):
    """Deleting non-existent paper returns 404."""
    response = client.delete("/papers/99999", headers=auth_headers)
    assert response.status_code == 404

def test_root_endpoint(client):
    """Root endpoint returns running message."""
    response = client.get("/")
    assert response.status_code == 200
    assert "ResearchPulse" in response.json()["message"]