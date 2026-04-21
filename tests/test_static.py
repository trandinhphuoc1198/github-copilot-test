"""Tests for static file serving of the High School Management System API."""


class TestStaticFileServing:
    """Test suite for GET / endpoint and static file serving."""
    
    def test_root_redirect_to_static_index(self, client):
        """Verify that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
    
    def test_root_redirect_follows_to_static(self, client):
        """Verify that following the redirect from / reaches the static file."""
        response = client.get("/", follow_redirects=True)
        
        assert response.status_code == 200
        # The response should contain HTML content from index.html
        assert "<!DOCTYPE html>" in response.text or "<html" in response.text
