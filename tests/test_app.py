import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))

def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]


def test_signup_adds_participant():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    response = client.post(url)

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    response = client.post(url)

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_nonexistent_activity_returns_404():
    url = f"/activities/{quote('Nonexistent Club')}/signup?email={quote('student@example.com')}"

    response = client.post(url)

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    response = client.delete(url)

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_not_signed_up_returns_404():
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    response = client.delete(url)

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not signed up"
