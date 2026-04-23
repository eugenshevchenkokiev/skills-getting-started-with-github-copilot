"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

# Create test client
client = TestClient(app)


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirect(self):
        """Test that root redirects to static/index.html"""
        # Arrange
        expected_location = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestGetActivities:
    """Test the get activities endpoint"""
    
    def test_get_activities_success(self):
        """Test retrieving all activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check that expected activities exist
        for activity in expected_activities:
            assert activity in data
            
        # Verify activity structure
        activity = data["Chess Club"]
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for field in required_fields:
            assert field in activity
        assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Test the signup endpoint"""
    
    def test_signup_success(self):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "test@student.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        # Arrange
        invalid_activity = "Nonexistent Club"
        email = "test@student.edu"
        expected_error = "Activity not found"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert expected_error in response.json()["detail"]
    
    def test_signup_already_registered(self):
        """Test signup when student is already registered"""
        # Arrange
        activity_name = "Chess Club"
        email = "duplicate@student.edu"
        expected_error = "already signed up"
        
        # Act - First signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Try duplicate signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert expected_error in response.json()["detail"]


class TestUnregisterEndpoint:
    """Test the unregister endpoint"""
    
    def test_unregister_success(self):
        """Test successful unregister from an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Pre-existing participant
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
    
    def test_unregister_activity_not_found(self):
        """Test unregister from non-existent activity"""
        # Arrange
        invalid_activity = "Nonexistent Club"
        email = "test@student.edu"
        expected_error = "Activity not found"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert expected_error in response.json()["detail"]
    
    def test_unregister_not_signed_up(self):
        """Test unregister when student is not signed up"""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@student.edu"
        expected_error = "not signed up"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert expected_error in response.json()["detail"]
