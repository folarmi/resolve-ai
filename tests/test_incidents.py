import pytest

from app import create_app
from app.extensions import db
from unittest.mock import patch

from app.models import Incident
from app.services.ai_service import AIService


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


def test_ai_analyze_incident_returns_structured_result(client, app):
    create_response = client.post(
        "/api/incidents",
        json={
            "title": "Production API returning 502 errors",
            "description": "Users are receiving 502 errors after deployment.",
            "logs": "upstream connect error: connection refused",
        },
    )

    incident_id = create_response.get_json()["incident"]["id"]

    mock_analysis = {
        "summary": "The API gateway cannot reach the upstream service.",
        "severity": "High",
        "category": "API Gateway / Reverse Proxy",
        "probable_causes": [
            "Upstream service is unavailable",
            "Incorrect upstream configuration",
        ],
        "investigation_steps": [
            "Verify the upstream service is running",
            "Check gateway configuration",
        ],
        "suggested_resolution": [
            "Restart the upstream service",
            "Correct the gateway configuration",
        ],
    }

    with patch(
        "app.services.ai_service.AIService.analyze_incident",
        return_value=mock_analysis,
    ):
        with app.app_context():
            incident = db.session.get(
                Incident,
                incident_id,
            )

            ai_service = AIService()
            result = ai_service.analyze_incident(incident)

    assert result["summary"] == (
        "The API gateway cannot reach the upstream service."
    )
    assert result["severity"] == "High"
    assert result["category"] == "API Gateway / Reverse Proxy"
    assert len(result["probable_causes"]) == 2
    assert len(result["investigation_steps"]) == 2
    assert len(result["suggested_resolution"]) == 2


def test_ai_analysis_contains_required_fields(client, app):
    create_response = client.post(
        "/api/incidents",
        json={
            "title": "Database unavailable",
            "description": "The application cannot reach PostgreSQL.",
            "logs": "connection refused",
        },
    )

    incident_id = create_response.get_json()["incident"]["id"]

    mock_analysis = {
        "summary": "Database connectivity failure.",
        "severity": "High",
        "category": "Database",
        "probable_causes": [
            "Database service is unavailable",
        ],
        "investigation_steps": [
            "Check database service health",
        ],
        "suggested_resolution": [
            "Restart or restore the database service",
        ],
    }

    with patch(
        "app.services.ai_service.AIService.analyze_incident",
        return_value=mock_analysis,
    ):
        with app.app_context():
            incident = db.session.get(
                Incident,
                incident_id,
            )

            ai_service = AIService()
            result = ai_service.analyze_incident(incident)

    required_fields = {
        "summary",
        "severity",
        "category",
        "probable_causes",
        "investigation_steps",
        "suggested_resolution",
    }

    assert required_fields.issubset(result.keys())


def test_ai_analysis_handles_invalid_json(app):
    with patch(
        "app.services.ai_service.AIService.generate",
        return_value="This is not valid JSON",
    ):
        with app.app_context():
            incident = Incident(
                title="API failure",
                description="The API is failing.",
                logs="500 internal server error",
            )

            ai_service = AIService()

            with pytest.raises(
                ValueError,
                match="AI returned an invalid incident analysis response",
            ):
                ai_service.analyze_incident(incident)

def test_runbook_service_loads_documents():
    from app.services.runbook_service import RunbookService

    service = RunbookService()
    documents = service.load_runbooks()

    assert len(documents) == 8

    sources = {
        document["source"]
        for document in documents
    }

    assert "api-errors.md" in sources
    assert "authentication.md" in sources
    assert "database.md" in sources
    assert "deployment.md" in sources
    assert "docker.md" in sources
    assert "networking.md" in sources
    assert "performance.md" in sources
    assert "websocket.md" in sources


def test_runbook_service_chunks_documents():
    from app.services.runbook_service import RunbookService

    service = RunbookService()
    chunks = service.chunk_runbooks()

    assert len(chunks) > 0

    first_chunk = chunks[0]

    assert "id" in first_chunk
    assert "source" in first_chunk
    assert "content" in first_chunk


def test_runbook_semantic_retrieval():
    from app.services.runbook_service import RunbookService

    service = RunbookService()
    service.ingest_runbooks()

    results = service.search_runbooks(
        (
            "Users receive 401 Unauthorized errors "
            "because JWT access tokens have expired"
        ),
        limit=3,
    )

    assert len(results) > 0
    assert results[0]["source"] == "authentication.md"

    for result in results:
        assert "source" in result
        assert "content" in result
        assert "distance" in result


def test_ai_analysis_includes_runbook_sources():
    incident = Incident(
        title="Production API returning 502 errors",
        description=(
            "Gateway cannot connect to the upstream service."
        ),
        logs=(
            "502 Bad Gateway - Connection refused "
            "while connecting to upstream"
        ),
    )

    mock_analysis = {
        "summary": "The upstream service is unavailable.",
        "severity": "High",
        "category": "API Gateway",
        "probable_causes": [
            "Upstream service is down",
        ],
        "investigation_steps": [
            "Check upstream service health",
        ],
        "suggested_resolution": [
            "Restore the upstream service",
        ],
    }

    mock_runbooks = [
        {
            "source": "api-errors.md",
            "content": "502 errors may occur when an upstream service is unavailable.",
            "distance": 0.4,
        },
        {
            "source": "api-errors.md",
            "content": "Check proxy and upstream connectivity.",
            "distance": 0.5,
        },
        {
            "source": "networking.md",
            "content": "Verify network connectivity.",
            "distance": 0.6,
        },
    ]

    with patch.object(
        AIService,
        "generate",
        return_value=__import__("json").dumps(mock_analysis),
    ):
        with patch(
            "app.services.runbook_service.RunbookService.search_runbooks",
            return_value=mock_runbooks,
        ):
            service = AIService()
            result = service.analyze_incident(incident)

    assert result["sources"] == [
        "api-errors.md",
        "networking.md",
    ]

def test_search_incidents_by_title(client, app):
    with app.app_context():
        incident_one = Incident(
            title="Production API returning 502 errors",
            description="Gateway cannot connect to upstream service.",
            status="Open",
        )

        incident_two = Incident(
            title="Database connection timeout",
            description="Application cannot reach PostgreSQL.",
            status="Open",
        )

        db.session.add_all([
            incident_one,
            incident_two,
        ])
        db.session.commit()

    response = client.get(
        "/api/incidents?search=502"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["count"] == 1
    assert len(data["incidents"]) == 1
    assert (
        data["incidents"][0]["title"]
        == "Production API returning 502 errors"
    )


def test_search_incidents_by_description(client, app):
    with app.app_context():
        incident_one = Incident(
            title="API failure",
            description=(
                "Gateway cannot connect to upstream service."
            ),
            status="Open",
        )

        incident_two = Incident(
            title="Database failure",
            description="PostgreSQL connection timeout.",
            status="Open",
        )

        db.session.add_all([
            incident_one,
            incident_two,
        ])
        db.session.commit()

    response = client.get(
        "/api/incidents?search=upstream"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["count"] == 1
    assert (
        data["incidents"][0]["title"]
        == "API failure"
    )


def test_filter_incidents_by_status(client, app):
    with app.app_context():
        db.session.add_all(
            [
                Incident(
                    title="Open incident",
                    description="Still open",
                    status="Open",
                ),
                Incident(
                    title="Investigating incident",
                    description="Currently being investigated",
                    status="Investigating",
                ),
                Incident(
                    title="Resolved incident",
                    description="Already fixed",
                    status="Resolved",
                ),
            ]
        )

        db.session.commit()

    response = client.get(
        "/api/incidents?status=Investigating"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["count"] == 1
    assert (
        data["incidents"][0]["status"]
        == "Investigating"
    )


def test_search_and_status_filter_together(client, app):
    with app.app_context():
        db.session.add_all(
            [
                Incident(
                    title="Production API 502",
                    description="Upstream connection refused.",
                    status="Investigating",
                ),
                Incident(
                    title="Production API 502 resolved",
                    description="Upstream service restored.",
                    status="Resolved",
                ),
                Incident(
                    title="Database timeout",
                    description="Database connection failed.",
                    status="Investigating",
                ),
            ]
        )

        db.session.commit()

    response = client.get(
        "/api/incidents"
        "?search=502"
        "&status=Investigating"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["count"] == 1
    assert (
        data["incidents"][0]["title"]
        == "Production API 502"
    )
    assert (
        data["incidents"][0]["status"]
        == "Investigating"
    )


def test_search_with_no_matches_returns_empty_list(
    client,
    app,
):
    with app.app_context():
        incident = Incident(
            title="Database timeout",
            description="PostgreSQL is unavailable.",
            status="Open",
        )

        db.session.add(incident)
        db.session.commit()

    response = client.get(
        "/api/incidents?search=doesnotexist"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["count"] == 0
    assert data["incidents"] == []

def test_incident_analytics_returns_zero_counts_when_empty(client):
    response = client.get("/api/analytics")

    assert response.status_code == 200

    data = response.get_json()

    assert data["total_incidents"] == 0

    assert data["status_counts"] == {
        "Open": 0,
        "Investigating": 0,
        "Resolved": 0,
    }

    assert data["severity_counts"] == {
        "Low": 0,
        "Medium": 0,
        "High": 0,
        "Critical": 0,
        "Unclassified": 0,
    }


def test_incident_analytics_counts_statuses(client, app):
    with app.app_context():
        db.session.add_all(
            [
                Incident(
                    title="Incident 1",
                    description="Open incident",
                    status="Open",
                ),
                Incident(
                    title="Incident 2",
                    description="Investigating incident",
                    status="Investigating",
                ),
                Incident(
                    title="Incident 3",
                    description="Resolved incident",
                    status="Resolved",
                ),
                Incident(
                    title="Incident 4",
                    description="Another open incident",
                    status="Open",
                ),
            ]
        )

        db.session.commit()

    response = client.get("/api/analytics")

    assert response.status_code == 200

    data = response.get_json()

    assert data["total_incidents"] == 4
    assert data["status_counts"]["Open"] == 2
    assert data["status_counts"]["Investigating"] == 1
    assert data["status_counts"]["Resolved"] == 1


def test_incident_analytics_counts_severities(client, app):
    with app.app_context():
        db.session.add_all(
            [
                Incident(
                    title="Low severity incident",
                    description="Minor issue",
                    severity="Low",
                ),
                Incident(
                    title="Medium severity incident",
                    description="Moderate issue",
                    severity="Medium",
                ),
                Incident(
                    title="High severity incident",
                    description="Major issue",
                    severity="High",
                ),
                Incident(
                    title="Critical severity incident",
                    description="Production outage",
                    severity="Critical",
                ),
                Incident(
                    title="Unclassified incident",
                    description="Not yet analyzed",
                ),
            ]
        )

        db.session.commit()

    response = client.get("/api/analytics")

    assert response.status_code == 200

    data = response.get_json()

    assert data["severity_counts"]["Low"] == 1
    assert data["severity_counts"]["Medium"] == 1
    assert data["severity_counts"]["High"] == 1
    assert data["severity_counts"]["Critical"] == 1
    assert data["severity_counts"]["Unclassified"] == 1


def test_incident_analytics_total_matches_created_incidents(
    client,
    app,
):
    with app.app_context():
        db.session.add_all(
            [
                Incident(
                    title="Incident A",
                    description="First incident",
                ),
                Incident(
                    title="Incident B",
                    description="Second incident",
                ),
                Incident(
                    title="Incident C",
                    description="Third incident",
                ),
            ]
        )

        db.session.commit()

    response = client.get("/api/analytics")

    assert response.status_code == 200

    data = response.get_json()

    assert data["total_incidents"] == 3