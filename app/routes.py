from flask import Blueprint, jsonify, render_template, request
from sqlalchemy import or_

from app.extensions import db
from app.models import Incident
from app.services.ai_service import AIService


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
@main_bp.get("/")
def home():
    return render_template("index.html")


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

    title = str(
        data.get("title", "")
    ).strip()

    description = str(
        data.get("description", "")
    ).strip()

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


@main_bp.get("/api/incidents/<string:incident_id>")
def get_incident(incident_id):
    incident = db.session.get(
        Incident,
        incident_id,
    )

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


@main_bp.patch(
    "/api/incidents/<string:incident_id>/status"
)
def update_incident_status(incident_id):
    incident = db.session.get(
        Incident,
        incident_id,
    )

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
                    "error": (
                        "Request body must contain valid JSON"
                    ),
                }
            ),
            400,
        )

    status = str(
        data.get("status", "")
    ).strip()

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
                "message": (
                    "Incident status updated successfully"
                ),
                "incident": incident.to_dict(),
            }
        ),
        200,
    )


@main_bp.post(
    "/api/incidents/<string:incident_id>/analyze"
)
def analyze_incident(incident_id):
    incident = db.session.get(
        Incident,
        incident_id,
    )

    if incident is None:
        return (
            jsonify(
                {
                    "error": "Incident not found",
                }
            ),
            404,
        )

    try:
        service = AIService()

        analysis = service.analyze_incident(
            incident
        )

        return (
            jsonify(
                {
                    "incident_id": incident.id,
                    "analysis": analysis,
                }
            ),
            200,
        )

    except ValueError as exc:
        return (
            jsonify(
                {
                    "error": str(exc),
                }
            ),
            500,
        )

    except Exception:
        return (
            jsonify(
                {
                    "error": (
                        "Unable to analyze incident"
                    ),
                }
            ),
            500,
        )


@main_bp.post(
    "/api/incidents/<string:incident_id>/feedback"
)
def submit_incident_feedback(incident_id):
    incident = db.session.get(
        Incident,
        incident_id,
    )

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
                    "error": (
                        "Request body must contain valid JSON"
                    ),
                }
            ),
            400,
        )

    helpful = data.get("helpful")

    if not isinstance(helpful, bool):
        return (
            jsonify(
                {
                    "error": "Validation failed",
                    "details": {
                        "helpful": (
                            "Helpful must be true or false"
                        ),
                    },
                }
            ),
            400,
        )

    incident.ai_feedback_helpful = helpful
    db.session.commit()

    return (
        jsonify(
            {
                "message": (
                    "AI diagnosis feedback saved"
                ),
                "incident_id": incident.id,
                "helpful": (
                    incident.ai_feedback_helpful
                ),
            }
        ),
        200,
    )

@main_bp.get("/api/analytics")
def get_incident_analytics():
    total_incidents = Incident.query.count()

    status_counts = {
        "Open": Incident.query.filter_by(
            status="Open"
        ).count(),
        "Investigating": Incident.query.filter_by(
            status="Investigating"
        ).count(),
        "Resolved": Incident.query.filter_by(
            status="Resolved"
        ).count(),
    }

    severity_counts = {
        "Low": Incident.query.filter_by(
            severity="Low"
        ).count(),
        "Medium": Incident.query.filter_by(
            severity="Medium"
        ).count(),
        "High": Incident.query.filter_by(
            severity="High"
        ).count(),
        "Critical": Incident.query.filter_by(
            severity="Critical"
        ).count(),
        "Unclassified": Incident.query.filter(
            Incident.severity.is_(None)
        ).count(),
    }

    return (
        jsonify(
            {
                "total_incidents": total_incidents,
                "status_counts": status_counts,
                "severity_counts": severity_counts,
            }
        ),
        200,
    )




