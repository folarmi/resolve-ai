import json
import os

from groq import Groq

from app.services.prompts import (
    INCIDENT_ANALYSIS_SYSTEM_PROMPT,
    build_incident_analysis_prompt,
)


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

    def generate(self, prompt, system_prompt=None):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                    or (
                        "You are ResolveAI, an AI assistant that helps "
                        "software engineers diagnose software incidents."
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

    def analyze_incident(self, incident):
        prompt = build_incident_analysis_prompt(incident)

        response = self.generate(
            prompt=prompt,
            system_prompt=INCIDENT_ANALYSIS_SYSTEM_PROMPT,
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "AI returned an invalid incident analysis response"
            ) from exc




      