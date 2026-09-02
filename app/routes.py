from flask import Blueprint, jsonify

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