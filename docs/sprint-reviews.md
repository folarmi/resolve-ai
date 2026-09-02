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
