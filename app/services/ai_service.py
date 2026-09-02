import json
import os

from groq import Groq

from app.services.prompts import (
    INCIDENT_ANALYSIS_SYSTEM_PROMPT,
    build_incident_analysis_prompt,
)
from app.services.runbook_service import RunbookService


class AIService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is not configured"
            )

        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b",
        )

        self.client = Groq(
            api_key=api_key,
        )

        self.runbook_service = RunbookService()

    def generate(
        self,
        prompt,
        system_prompt=None,
    ):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        system_prompt
                        or (
                            "You are ResolveAI, an AI assistant "
                            "that helps software engineers diagnose "
                            "software incidents."
                        )
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content

    def build_incident_query(self, incident):
        parts = [
            incident.title,
            incident.description,
        ]

        if incident.logs:
            parts.append(incident.logs)

        return "\n".join(parts)

    def analyze_incident(self, incident):
        query = self.build_incident_query(
            incident
        )

        runbook_matches = (
            self.runbook_service.search_runbooks(
                query,
                limit=3,
            )
        )

        prompt = build_incident_analysis_prompt(
            incident,
            runbook_matches=runbook_matches,
        )

        response = self.generate(
            prompt=prompt,
            system_prompt=INCIDENT_ANALYSIS_SYSTEM_PROMPT,
        )

        try:
            analysis = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "AI returned an invalid incident analysis response"
            ) from exc

        return analysis