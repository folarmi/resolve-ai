from datetime import datetime, timezone
import uuid

from app.extensions import db


class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    title = db.Column(
        db.String(200),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    logs = db.Column(
        db.Text,
        nullable=True,
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Open",
    )

    severity = db.Column(
        db.String(20),
        nullable=True,
    )

    ai_feedback_helpful = db.Column(
        db.Boolean,
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "logs": self.logs,
            "status": self.status,
            "severity": self.severity,
            "ai_feedback_helpful": self.ai_feedback_helpful,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }