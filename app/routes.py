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
    data = request.get_json(silent=True) or {}

    incident = Incident(
        title=data.get("title"),
        description=data.get("description"),
        logs=data.get("logs"),
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