import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app()

    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# =========================================================
# Incident Creation Tests
# =========================================================


def test_create_incident_successfully(client):
    response = client.post(
        "/api/incidents",
        json={
            "title": "Production API returning 502 errors",
            "description": "Users are receiving 502 errors.",
            "logs": "upstream connection refused",
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Incident created successfully"
    assert data["incident"]["title"] == "Production API returning 502 errors"
    assert data["incident"]["description"] == "Users are receiving 502 errors."
    assert data["incident"]["logs"] == "upstream connection refused"
    assert data["incident"]["status"] == "Open"
    assert data["incident"]["id"]


def test_create_incident_without_title_returns_400(client):
    response = client.post(
        "/api/incidents",
        json={
            "description": "Database connection is failing.",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation failed"
    assert data["details"]["title"] == "Title is required"


def test_create_incident_without_description_returns_400(client):
    response = client.post(
        "/api/incidents",
        json={
            "title": "Database connection failure",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation failed"
    assert data["details"]["description"] == "Description is required"


def test_create_incident_without_json_returns_400(client):
    response = client.post(
        "/api/incidents",
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Request body must contain valid JSON"


# =========================================================
# Incident Retrieval Tests
# =========================================================


def test_get_incidents_returns_incident_history(client):
    create_response = client.post(
        "/api/incidents",
        json={
            "title": "API timeout",
            "description": "Requests are timing out in production.",
            "logs": "request timeout after 30 seconds",
        },
    )

    assert create_response.status_code == 201

    response = client.get("/api/incidents")

    assert response.status_code == 200

    data = response.get_json()

    assert data["count"] == 1
    assert len(data["incidents"]) == 1
    assert data["incidents"][0]["title"] == "API timeout"
    assert data["incidents"][0]["status"] == "Open"


def test_get_incident_by_id(client):
    create_response = client.post(
        "/api/incidents",
        json={
            "title": "Database connection failure",
            "description": "Application cannot connect to the database.",
            "logs": "connection refused",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.get_json()["incident"]["id"]

    response = client.get(
        f"/api/incidents/{incident_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["incident"]["id"] == incident_id
    assert data["incident"]["title"] == "Database connection failure"
    assert data["incident"]["description"] == (
        "Application cannot connect to the database."
    )


def test_get_nonexistent_incident_returns_404(client):
    response = client.get(
        "/api/incidents/nonexistent-incident-id"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Incident not found"


# =========================================================
# Incident Status Update Tests
# =========================================================


def test_update_incident_status_successfully(client):
    create_response = client.post(
        "/api/incidents",
        json={
            "title": "API instability",
            "description": "The production API is intermittently failing.",
            "logs": "502 bad gateway",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.get_json()["incident"]["id"]

    response = client.patch(
        f"/api/incidents/{incident_id}/status",
        json={
            "status": "Investigating",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Incident status updated successfully"
    assert data["incident"]["status"] == "Investigating"


def test_update_incident_status_is_persisted(client):
    create_response = client.post(
        "/api/incidents",
        json={
            "title": "Database outage",
            "description": "Database connections are failing.",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.get_json()["incident"]["id"]

    update_response = client.patch(
        f"/api/incidents/{incident_id}/status",
        json={
            "status": "Resolved",
        },
    )

    assert update_response.status_code == 200

    response = client.get(
        f"/api/incidents/{incident_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["incident"]["status"] == "Resolved"


def test_update_incident_with_invalid_status_returns_400(client):
    create_response = client.post(
        "/api/incidents",
        json={
            "title": "Deployment failure",
            "description": "The latest deployment failed.",
        },
    )

    assert create_response.status_code == 201

    incident_id = create_response.get_json()["incident"]["id"]

    response = client.patch(
        f"/api/incidents/{incident_id}/status",
        json={
            "status": "Pending",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Validation failed"
    assert (
        data["details"]["status"]
        == "Status must be one of: Open, Investigating, Resolved"
    )


def test_update_nonexistent_incident_returns_404(client):
    response = client.patch(
        "/api/incidents/nonexistent-incident-id/status",
        json={
            "status": "Resolved",
        },
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Incident not found"