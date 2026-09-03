# Sprint Reviews

## Sprint 1 — Incident Management Foundation

### Sprint Goal

Build the core incident management functionality required for users to create, view, and manage software incidents.

### Completed User Stories

- US-001 — Create an incident
- US-002 — View incident history
- US-003 — Update incident status

### Completed Features

- Flask application foundation
- SQLite database integration
- Incident data model
- Incident creation API
- Incident input validation
- Incident history API
- Individual incident retrieval
- Incident status updates
- Status validation
- Automated API tests

### Testing

Sprint 1 concluded with 11 automated tests covering:

- Incident creation
- Input validation
- Incident retrieval
- Incident-not-found handling
- Status updates
- Status persistence
- Invalid status handling

All 11 tests passed.

### Sprint Outcome

The Sprint 1 goal was achieved. ResolveAI now has a tested incident management foundation that can be extended with AI-powered incident diagnosis in Sprint 2.

---

## Sprint 2 — AI Diagnosis and Runbook Retrieval

### Sprint Goal

Enable ResolveAI to analyze software incidents using AI and ground its recommendations in relevant troubleshooting runbooks.

### Completed User Stories

- US-004 — Analyze an incident with AI
- US-005 — Retrieve troubleshooting runbooks

### Completed Features

- Groq-powered AI incident analysis
- Structured incident diagnosis
- Incident severity classification
- Incident category classification
- Probable cause identification
- Investigation step generation
- Suggested resolution generation
- Troubleshooting runbook knowledge base
- Runbook document ingestion and chunking
- FastEmbed-based text embeddings
- ChromaDB vector storage
- Semantic runbook retrieval
- Retrieval-augmented generation (RAG)
- Runbook context integration with AI diagnosis
- Runbook source attribution

### Testing

Sprint 2 concluded with automated tests covering:

- Structured AI incident analysis
- Required AI response fields
- Invalid AI response handling
- Runbook document loading
- Runbook document chunking
- Semantic runbook retrieval
- Runbook source attribution

All automated tests passed.

### Sprint Outcome

The Sprint 2 goal was achieved. ResolveAI can now analyze software incidents using AI while retrieving relevant troubleshooting guidance from its runbook knowledge base. The retrieved runbook context is incorporated into the AI diagnosis, and the runbook sources used are included in the analysis result for traceability.

ResolveAI now has a functional retrieval-augmented generation pipeline that combines semantic search with AI-powered incident diagnosis.

---

## Sprint 3 — Incident Management Features and AI Feedback

### Sprint Goal

Complete the core incident management experience by adding incident discovery, operational analytics, and user feedback for AI-generated diagnoses.

### Completed User Stories

- US-006 — Search and filter incidents
- US-007 — View incident analytics
- US-008 — Rate AI diagnosis

### Completed Features

- Incident search by title and description
- Incident filtering by status
- Combined incident search and filtering
- Incident analytics endpoint
- Total incident metrics
- Incident status summary metrics
- AI-generated severity persistence
- Incident severity summary metrics
- AI diagnosis feedback endpoint
- Helpful and not-helpful AI diagnosis ratings
- AI feedback persistence
- AI feedback input validation
- AI analysis endpoint integration
- Automated tests for search, filtering, analytics, and AI feedback

### Testing

Sprint 3 concluded with additional automated tests covering:

- Incident search
- Incident status filtering
- Combined search and filtering
- Empty analytics results
- Total incident counts
- Incident status metrics
- Incident severity metrics
- Helpful AI feedback submission
- Not-helpful AI feedback submission
- AI feedback persistence
- Invalid AI feedback
- Missing feedback request data
- Feedback for nonexistent incidents

At the completion of Sprint 3, the full ResolveAI automated test suite contained **32 passing tests**.

### Sprint Outcome

The Sprint 3 goal was achieved. ResolveAI now provides the core functionality required to manage incidents throughout their lifecycle, locate incidents using search and filtering, monitor incident trends through analytics, and collect user feedback on AI-generated diagnoses.

The incident analytics functionality provides visibility into total incidents, incident status distribution, and AI-classified severity distribution. AI diagnosis feedback is persisted with each incident, providing a foundation for evaluating the usefulness of ResolveAI's AI-generated recommendations.

With Sprint 3 complete, all planned core user stories for the ResolveAI capstone have been implemented and tested.
