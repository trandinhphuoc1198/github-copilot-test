"""Tests for activity endpoints of the High School Management System API."""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Verify that GET /activities returns all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities = response.json()
        
        # Verify all 9 activities are present
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert "Basketball Team" in activities
        assert "Soccer Club" in activities
        assert "Art Club" in activities
        assert "Drama Club" in activities
        assert "Debate Club" in activities
        assert "Science Club" in activities
    
    def test_get_activities_returns_correct_structure(self, client):
        """Verify that each activity has the expected structure."""
        response = client.get("/activities")
        activities = response.json()
        
        # Check a specific activity for structure
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_shows_initial_participants(self, client):
        """Verify that initial participants are returned correctly."""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have 2 initial participants
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
        
        # Basketball Team should start empty
        assert len(activities["Basketball Team"]["participants"]) == 0


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_for_activity_success(self, client):
        """Verify successful signup for an available activity."""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "alice@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up alice@mergington.edu for Basketball Team"
    
    def test_signup_appears_in_activity_list(self, client):
        """Verify that a signup appears in the activities list."""
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": "alice@mergington.edu"}
        )
        
        response = client.get("/activities")
        activities = response.json()
        
        assert "alice@mergington.edu" in activities["Basketball Team"]["participants"]
        assert len(activities["Basketball Team"]["participants"]) == 1
    
    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Verify 404 error when signing up for non-existent activity."""
        response = client.post(
            "/activities/NonExistent Club/signup",
            params={"email": "alice@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_student_returns_400(self, client):
        """Verify 400 error when student tries to sign up twice."""
        student_email = "michael@mergington.edu"
        
        # Michael is already in Chess Club, try to sign up again
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": student_email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up"
    
    def test_multiple_students_can_signup(self, client):
        """Verify that multiple different students can sign up for the same activity."""
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": "alice@mergington.edu"}
        )
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": "bob@mergington.edu"}
        )
        
        response = client.get("/activities")
        activities = response.json()
        
        assert len(activities["Basketball Team"]["participants"]) == 2
        assert "alice@mergington.edu" in activities["Basketball Team"]["participants"]
        assert "bob@mergington.edu" in activities["Basketball Team"]["participants"]


class TestUnregisterFromActivity:
    """Test suite for DELETE /activities/{activity_name}/signup endpoint."""
    
    def test_unregister_from_activity_success(self, client):
        """Verify successful unregistration from an activity."""
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Unregistered michael@mergington.edu from Chess Club"
    
    def test_unregister_removes_from_activity_list(self, client):
        """Verify that unregistration removes student from activity."""
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        response = client.get("/activities")
        activities = response.json()
        
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 1
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Verify 404 error when unregistering from non-existent activity."""
        response = client.delete(
            "/activities/NonExistent Club/signup",
            params={"email": "alice@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_student_not_signed_up_returns_400(self, client):
        """Verify 400 error when trying to unregister a student who is not signed up."""
        response = client.delete(
            "/activities/Basketball Team/signup",
            params={"email": "alice@mergington.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student not signed up for this activity"
    
    def test_signup_then_unregister_works(self, client):
        """Verify that a student can sign up and then unregister."""
        student_email = "new@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": student_email}
        )
        
        # Verify signup
        response = client.get("/activities")
        assert student_email in response.json()["Basketball Team"]["participants"]
        
        # Unregister
        client.delete(
            "/activities/Basketball Team/signup",
            params={"email": student_email}
        )
        
        # Verify unregistration
        response = client.get("/activities")
        assert student_email not in response.json()["Basketball Team"]["participants"]
