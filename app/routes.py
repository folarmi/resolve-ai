from flask import Blueprint, jsonify, request

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