from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from app.extensions import db
from app.models import Incident


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    return jsonify(
        {
            "name": "ResolveAI",
            "status": "running",
            "message": "AI-powered software incident diagnosis platform",
        }
    )


@main_bp.get("/api/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "service": "ResolveAI",
        }
    )


@main_bp.post("/api/incidents")
def create_incident():
    data = request.get_json(silent=True)

    if not data:
        return (
            jsonify(
                {
                    "error": "Request body must contain valid JSON",
                }
            ),
            400,
        )

    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    logs = data.get("logs")

    errors = {}

    if not title:
        errors["title"] = "Title is required"

    if not description:
        errors["description"] = "Description is required"

    if errors:
        return (
            jsonify(
                {
                    "error": "Validation failed",
                    "details": errors,
                }
            ),
            400,
        )

    if logs is not None:
        logs = str(logs).strip()

    incident = Incident(
        title=title,
        description=description,
        logs=logs,
    )

    db.session.add(incident)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Incident created successfully",
                "incident": incident.to_dict(),
            }
        ),
        201,
    )


@main_bp.get("/api/incidents")

def get_incidents():
    search = request.args.get(
        "search",
        "",
    ).strip()

    status = request.args.get(
        "status",
        "",
    ).strip()

    query = Incident.query

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            or_(
                Incident.title.ilike(search_pattern),
                Incident.description.ilike(search_pattern),
            )
        )

    if status:
        query = query.filter(
            Incident.status == status
        )

    incidents = query.order_by(
        Incident.created_at.desc()
    ).all()

    return (
        jsonify(
            {
                "incidents": [
                    incident.to_dict()
                    for incident in incidents
                ],
                "count": len(incidents),
            }
        ),
        200,
    )

@main_bp.patch("/api/incidents/<string:incident_id>/status")
def update_incident_status(incident_id):
    incident = db.session.get(Incident, incident_id)

    if incident is None:
        return (
            jsonify(
                {
                    "error": "Incident not found",
                }
            ),
            404,
        )

    data = request.get_json(silent=True)

    if not data:
        return (
            jsonify(
                {
                    "error": "Request body must contain valid JSON",
                }
            ),
            400,
        )

    status = str(data.get("status", "")).strip()

    allowed_statuses = [
        "Open",
        "Investigating",
        "Resolved",
    ]

    if not status:
        return (
            jsonify(
                {
                    "error": "Validation failed",
                    "details": {
                        "status": "Status is required",
                    },
                }
            ),
            400,
        )

    if status not in allowed_statuses:
        return (
            jsonify(
                {
                    "error": "Validation failed",
                    "details": {
                        "status": (
                            "Status must be one of: "
                            "Open, Investigating, Resolved"
                        ),
                    },
                }
            ),
            400,
        )

    incident.status = status
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Incident status updated successfully",
                "incident": incident.to_dict(),
            }
        ),
        200,
    )

@main_bp.get("/api/incidents/<string:incident_id>")
def get_incident(incident_id):
    incident = db.session.get(Incident, incident_id)

    if incident is None:
        return (
            jsonify(
                {
                    "error": "Incident not found",
                }
            ),
            404,
        )

    return (
        jsonify(
            {
                "incident": incident.to_dict(),
            }
        ),
        200,
    )



