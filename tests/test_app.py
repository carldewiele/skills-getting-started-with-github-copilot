import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app, follow_redirects=False)

# Sample data for testing
sample_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    from src.app import activities
    activities.clear()
    activities.update(copy.deepcopy(sample_activities))

def test_get_activities():
    """Test GET /activities returns all activities"""
    # Arrange
    # (Activities are reset by fixture)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 2
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]

def test_signup_success():
    """Test successful signup for an activity"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email.lower()} for {activity}" in data["message"]

    # Verify participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email.lower() in activities[activity]["participants"]

def test_signup_duplicate():
    """Test signup fails when student is already signed up"""
    # Arrange
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_signup_activity_full():
    """Test signup fails when activity is at capacity"""
    # Arrange
    from src.app import activities
    activities["Chess Club"]["max_participants"] = 2  # Already has 2 participants
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Activity is full" in data["detail"]

def test_signup_invalid_activity():
    """Test signup fails for non-existent activity"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "NonExistent Activity"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    """Test successful unregister from an activity"""
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Unregistered {email.lower()} from {activity}" in data["message"]

    # Verify participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert email.lower() not in activities[activity]["participants"]

def test_unregister_not_signed_up():
    """Test unregister fails when student is not signed up"""
    # Arrange
    email = "notsignedup@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]

def test_unregister_invalid_activity():
    """Test unregister fails for non-existent activity"""
    # Arrange
    email = "michael@mergington.edu"
    activity = "NonExistent Activity"

    # Act
    response = client.post(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_root_redirect():
    """Test root endpoint redirects to static index"""
    # Arrange
    # (No special setup needed)

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"