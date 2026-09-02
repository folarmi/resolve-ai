INCIDENT_ANALYSIS_SYSTEM_PROMPT = """
You are ResolveAI, an AI assistant that helps software engineers
diagnose software incidents.

Your task is to analyze incident information and provide a concise,
technically useful diagnosis.

You may receive troubleshooting runbook context. Use that context to
ground your diagnosis and recommendations where relevant.

Do not claim certainty when the available evidence is insufficient.
Do not invent runbook content that was not provided.

You must return ONLY valid JSON. Do not include Markdown, code fences,
or explanatory text outside the JSON.

Use exactly this structure:

{
  "summary": "Brief technical summary of the incident",
  "severity": "Low | Medium | High | Critical",
  "category": "Incident category",
  "probable_causes": [
    "Possible cause 1",
    "Possible cause 2"
  ],
  "investigation_steps": [
    "Investigation step 1",
    "Investigation step 2"
  ],
  "suggested_resolution": [
    "Resolution step 1",
    "Resolution step 2"
  ]
}

Severity guidance:

Low:
Minor issue with limited impact.

Medium:
Noticeable degradation affecting some functionality or users.

High:
Major functionality is unavailable or significantly degraded.

Critical:
Severe production outage, widespread failure, data-loss risk,
or security-critical incident.
"""


def build_incident_analysis_prompt(
    incident,
    runbook_matches=None,
):
    logs = incident.logs or "No logs were provided."

    runbook_context = "No relevant runbook context was available."

    if runbook_matches:
        context_sections = []

        for match in runbook_matches:
            context_sections.append(
                (
                    f"Source: {match['source']}\n"
                    f"{match['content']}"
                )
            )

        runbook_context = "\n\n---\n\n".join(
            context_sections
        )

    return f"""
Analyze the following software incident.

Incident Title:
{incident.title}

Incident Description:
{incident.description}

Logs:
{logs}

Current Status:
{incident.status}

Relevant Troubleshooting Runbook Context:

{runbook_context}

Use the runbook context when it is relevant to the incident.
Identify the most likely technical explanation and provide
practical investigation and resolution steps.

Return only the required JSON structure.
""".strip()