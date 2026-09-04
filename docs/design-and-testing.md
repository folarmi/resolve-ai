# ResolveAI — Design and Testing Documentation

## 1. System Overview

ResolveAI is an AI-powered software incident diagnosis and management platform designed to help software developers investigate and manage software incidents more efficiently.

The system combines traditional incident management functionality with AI-assisted diagnosis and retrieval-augmented generation (RAG). Users can create and track incidents, search incident history, update incident status, view operational analytics, request AI-generated diagnoses, and provide feedback on the usefulness of AI recommendations.

Rather than relying solely on a large language model's existing knowledge, ResolveAI retrieves relevant information from a curated collection of software troubleshooting runbooks. The retrieved runbook content is supplied as context during AI analysis, and the sources used during retrieval are displayed to the user.

### 1.1 Core Capabilities

ResolveAI provides the following capabilities:

- Create and view software incidents.
- Update incident status through Open, Investigating, and Resolved states.
- Search incidents by title and description.
- Filter incidents by status.
- Generate structured AI-assisted incident diagnoses.
- Classify incident severity and category.
- Suggest probable causes, investigation steps, and resolutions.
- Retrieve relevant troubleshooting information using semantic search.
- Display runbook sources associated with an AI diagnosis.
- Provide incident analytics by status and severity.
- Record whether users found an AI diagnosis helpful.

---

## 2. System Architecture

ResolveAI uses a layered web application architecture in which the Flask application coordinates incident management, persistence, AI analysis, and runbook retrieval.

The high-level architecture is:

```text
Browser
   |
   v
Flask Web Application / REST API
   |
   +---------------------+
   |                     |
   v                     v
Incident Management  AI Analysis Service
   |                     |
   v                     +--------------------+
SQLite Database           |                    |
                          v                    v
                     RAG Service          Groq LLM API
                          |
                          v
                  FastEmbed Embeddings
                          |
                          v
                       ChromaDB
                          |
                          v
                 Troubleshooting Runbooks
```

### 2.1 Presentation Layer

The user interface is implemented using server-served HTML, CSS, and vanilla JavaScript.

The interface provides:

- an incident dashboard;
- incident analytics;
- incident creation;
- incident search and filtering;
- incident detail views;
- status management;
- AI diagnosis controls;
- structured diagnosis results;
- runbook source attribution; and
- AI diagnosis feedback.

Using a lightweight frontend avoided introducing a separate frontend framework and build pipeline while still providing an interactive web application suitable for demonstrating the complete ResolveAI workflow.

### 2.2 Application and API Layer

Flask provides the primary web application and REST API.

The API handles operations including:

- incident creation;
- incident retrieval;
- incident status updates;
- search and filtering;
- analytics;
- AI analysis requests; and
- AI diagnosis feedback.

Flask-SQLAlchemy provides the persistence abstraction between the application and the database.

### 2.3 Persistence Layer

SQLite is used to persist incident information.

Each incident stores information including:

- unique identifier;
- title;
- description;
- logs;
- status;
- AI-classified severity;
- AI feedback; and
- creation and update timestamps.

SQLite was selected because ResolveAI is a capstone prototype with a controlled scope and does not require the operational complexity of a production-scale database server.

### 2.4 AI Analysis Layer

ResolveAI uses the Groq API to perform AI-assisted incident analysis.

The AI service receives incident information and relevant runbook context and returns a structured diagnosis containing:

- summary;
- severity;
- category;
- probable causes;
- investigation steps; and
- suggested resolution.

The application requests structured JSON output so that diagnosis information can be validated and displayed consistently by the user interface.

### 2.5 Retrieval-Augmented Generation Layer

ResolveAI uses retrieval-augmented generation to provide troubleshooting context to the AI model.

Troubleshooting runbooks are stored as Markdown documents. During ingestion:

1. Runbooks are loaded from the knowledge base.
2. Documents are divided into overlapping text chunks.
3. FastEmbed generates vector embeddings using the `BAAI/bge-small-en-v1.5` embedding model.
4. Embeddings and source metadata are stored in ChromaDB.

When an incident is analyzed:

1. The incident title, description, and available logs are combined into a retrieval query.
2. ResolveAI creates an embedding for the query.
3. ChromaDB performs semantic similarity search.
4. The most relevant runbook chunks are retrieved.
5. Retrieved content is included in the AI analysis prompt.
6. Source filenames are returned with the diagnosis and displayed in the interface.

The application also detects an empty ChromaDB collection and automatically ingests the runbooks. This allows a fresh Docker or hosted environment to initialize the RAG knowledge base without requiring a pre-generated local vector database.

---

## 3. Technology Selection

### 3.1 Python

Python was selected as the primary programming language because of its mature ecosystem for web development, AI integration, automated testing, vector databases, and machine learning tooling.

### 3.2 Flask

Flask provides the web application and API framework. Its lightweight architecture was appropriate for ResolveAI because the project required a relatively small API surface and did not require the additional complexity of a larger web framework.

### 3.3 Flask-SQLAlchemy and SQLite

Flask-SQLAlchemy provides database integration and object-relational mapping. SQLite provides lightweight persistence without requiring a separately managed database service.

### 3.4 Groq

Groq provides access to the large language model used for incident diagnosis. ResolveAI uses the configured `openai/gpt-oss-20b` model for structured incident analysis.

### 3.5 FastEmbed

FastEmbed generates embeddings for troubleshooting runbooks and incident retrieval queries. It was selected as a lightweight embedding solution suitable for the resource constraints of the application and its deployment environment.

### 3.6 ChromaDB

ChromaDB provides persistent vector storage and semantic similarity search for the RAG pipeline. It stores runbook chunks, embeddings, and source metadata.

### 3.7 Pytest

Pytest is used for automated testing of ResolveAI's API, incident management functionality, analytics, AI integration behavior, RAG retrieval, and feedback functionality.

### 3.8 Docker

Docker packages the application and its dependencies into a reproducible deployment environment. The same containerized application was verified locally before being deployed to the hosting environment.

### 3.9 GitHub Actions

GitHub Actions provides continuous integration. Pushes and pull requests targeting the main branch automatically install the project's dependencies and execute the automated test suite.

### 3.10 Render

Render hosts the deployed ResolveAI web application. The application is deployed from its Docker configuration and runs using Gunicorn as the production WSGI server.

---

## 4. Software Design Decisions and Patterns

ResolveAI was designed with separation of concerns in mind. Incident management, AI analysis, runbook retrieval, persistence, and presentation responsibilities are separated so that each part of the application can evolve and be tested with limited impact on the others.

### 4.1 Application Factory Pattern

The Flask application uses an application factory through the `create_app()` function.

Rather than configuring the Flask application entirely at module import time, application creation and configuration are encapsulated within a function. This allows the application to be initialized with its extensions, routes, database configuration, and environment-specific settings in a consistent manner.

This approach also supports automated testing because test instances can use an isolated in-memory SQLite database instead of the normal application database.

### 4.2 Blueprint Pattern

ResolveAI's HTTP routes are registered through a Flask Blueprint.

Using a Blueprint separates route definitions from application initialization and provides a structure that can be extended if the API grows. It also prevents the application factory from becoming responsible for individual endpoint implementations.

### 4.3 Service Layer

AI and retrieval functionality are encapsulated in dedicated service classes.

`AIService` is responsible for:

- communicating with the configured large language model;
- constructing incident analysis requests;
- combining incident data with retrieved runbook context;
- validating structured AI responses;
- attaching runbook source attribution; and
- persisting valid AI-generated severity classifications.

`RunbookService` is responsible for:

- loading troubleshooting documents;
- chunking runbook content;
- generating embeddings;
- managing the ChromaDB collection;
- ingesting runbooks; and
- performing semantic retrieval.

Separating these responsibilities from Flask route handlers keeps the HTTP layer focused on request validation and response handling.

### 4.4 Repository and Persistence Abstraction

ResolveAI uses SQLAlchemy's ORM capabilities rather than embedding raw SQL throughout the application.

The `Incident` model represents persisted incident state, while Flask-SQLAlchemy manages database sessions and queries. This reduces coupling between application logic and the underlying SQLite implementation and provides a clearer path to adopting another relational database in a larger deployment.

### 4.5 Retrieval-Augmented Generation

A key architectural decision was to use retrieval-augmented generation rather than sending incident information directly to the language model without supporting context.

The RAG approach allows ResolveAI to retrieve troubleshooting knowledge from its own runbook collection before requesting a diagnosis. This provides two important capabilities:

1. AI analysis can incorporate project-controlled troubleshooting information.
2. ResolveAI can expose the runbook sources associated with the retrieved context.

Source attribution improves transparency by allowing users to see which troubleshooting documents contributed context to the AI analysis.

### 4.6 Structured AI Output

The AI analysis prompt requests a defined JSON structure instead of unrestricted natural-language output.

The expected structure contains:

- summary;
- severity;
- category;
- probable causes;
- investigation steps; and
- suggested resolution.

This design makes AI responses easier for the application to validate, process, test, and render consistently in the interface.

### 4.7 Defensive AI Integration

ResolveAI treats the external AI service as a dependency that may return invalid or unexpected output.

The application therefore parses the model response as JSON and raises an application-level error when the response cannot be decoded into the expected structure.

Severity values are also restricted to the supported classifications:

- Low
- Medium
- High
- Critical

This prevents arbitrary model-generated severity values from being persisted as valid classifications.

### 4.8 Automatic Knowledge Base Initialization

The ChromaDB vector store is not committed as a pre-generated application artifact.

Instead, ResolveAI checks whether its runbook collection is empty before retrieval. If necessary, the application loads the Markdown runbooks, generates embeddings, and populates ChromaDB automatically.

This decision makes fresh Docker and hosted deployments reproducible without depending on a developer's local vector database.

### 4.9 Configuration Through Environment Variables

Environment-specific and sensitive configuration is kept outside the source code.

ResolveAI uses environment variables for settings such as:

```text
GROQ_API_KEY
GROQ_MODEL
DATABASE_URL
```

The real `.env` file is excluded from version control, while `.env.example` documents the required configuration.

This avoids committing credentials to the repository and allows local, test, and hosted environments to provide different configuration values.

### 4.10 Containerization and Reproducibility

ResolveAI is packaged as a Docker container.

The container defines the Python runtime, system dependencies, Python packages, application code, and production startup command. This reduces differences between the local development environment and the hosted environment.

Gunicorn is used as the production WSGI server with a single worker and an extended timeout for AI and RAG operations:

```text
--workers 1
--timeout 180
```

The timeout was increased after deployment testing identified that first-time embedding model initialization could exceed Gunicorn's default worker timeout on a resource-constrained free hosting instance.

### 4.11 Continuous Integration

ResolveAI uses GitHub Actions as its continuous integration mechanism.

For pushes and pull requests targeting the main branch, the CI workflow:

1. checks out the repository;
2. configures the Python environment;
3. installs project dependencies; and
4. executes the automated Pytest suite.

This provides automated regression detection and ensures that changes can be validated consistently outside the developer's local machine.

---

## 5. Testing Strategy and Results

Testing was incorporated throughout the development of ResolveAI rather than being deferred until the end of the project. Automated tests were added during each sprint as new functionality was implemented.

Pytest was used as the primary automated testing framework. Flask's test client was used to exercise HTTP endpoints without requiring a separately running web server.

At the completion of the three development sprints, the ResolveAI automated test suite contained **32 passing tests**.

### 5.1 Test Environment

Automated tests use a dedicated Flask application configured for testing.

An in-memory SQLite database is used:

```text
sqlite:///:memory:
```

The database is created for the test environment and removed after testing. This isolates automated tests from development and production data and allows tests to run consistently in both local development and continuous integration environments.

External AI behavior is mocked where appropriate so that automated tests do not depend on live LLM API responses.

### 5.2 Incident Creation and Validation Testing

Tests were implemented for the incident creation workflow.

These tests verify that:

- valid incidents can be created;
- required fields are validated;
- invalid requests are rejected; and
- successfully created incidents can subsequently be retrieved.

Testing input validation was important because incident data enters the system through HTTP requests and should not be persisted when required information is missing.

### 5.3 Incident Retrieval Testing

Incident retrieval tests verify that:

- incident history can be retrieved;
- individual incidents can be retrieved using their identifiers; and
- requests for nonexistent incidents return the appropriate not-found response.

These tests validate both successful retrieval and expected failure behavior.

### 5.4 Incident Status Testing

Status-management tests verify that incidents can progress through the supported lifecycle states:

- Open
- Investigating
- Resolved

Tests also verify that unsupported status values are rejected and that valid status changes are persisted.

### 5.5 Search and Filtering Testing

Automated tests cover incident discovery functionality, including:

- searching incident titles;
- searching incident descriptions;
- filtering incidents by status; and
- combining search and status filtering.

These tests ensure that the incident list behaves correctly as the amount of stored incident data increases.

### 5.6 AI Analysis Testing

AI-related tests focus on the behavior controlled by ResolveAI rather than attempting to test the external language model itself.

Tests verify behavior including:

- processing structured AI analysis responses;
- handling expected diagnosis fields;
- associating retrieved runbook sources with an analysis; and
- persisting supported severity classifications for database-backed incidents.

AI responses are mocked where appropriate. This makes the automated suite deterministic and avoids introducing network availability, model variability, API quotas, or external service latency into normal test execution.

### 5.7 Runbook Retrieval Testing

The RAG functionality was tested to verify that troubleshooting runbooks can be retrieved and associated with incident analysis.

Testing covers the application's retrieval behavior and source attribution. Manual integration testing was additionally performed using realistic incidents to verify that semantic retrieval returned relevant troubleshooting documents.

For example, a production API incident containing a `502 Bad Gateway` error successfully retrieved relevant API troubleshooting material and displayed the associated runbook filenames in the diagnosis interface.

### 5.8 Analytics Testing

Analytics tests verify:

- behavior when no incidents exist;
- total incident counts;
- status distribution metrics; and
- severity distribution metrics.

Severity analytics include the supported AI classifications as well as incidents that have not yet received an AI severity classification.

### 5.9 AI Feedback Testing

Tests were implemented for the AI diagnosis feedback functionality.

They verify:

- submission of a helpful rating;
- submission of a not-helpful rating;
- persistence of feedback;
- rejection of non-Boolean feedback values;
- handling of missing request data; and
- handling feedback requests for nonexistent incidents.

This ensures that feedback data used to evaluate AI usefulness is stored consistently.

### 5.10 Regression Testing

The complete automated test suite was executed after implementation changes rather than running only tests for the feature currently being developed.

This regression-testing approach helped identify unintended effects between features.

One example occurred when severity persistence was introduced into the AI analysis service. A unit test created a transient `Incident` object outside a Flask application context. Attempting an unconditional database commit caused the test to fail.

The implementation was updated to inspect the SQLAlchemy state of the incident and commit severity only when the object is persistent. This preserved production persistence while keeping isolated AI analysis behavior testable.

### 5.11 Continuous Integration Testing

The test suite is executed automatically through GitHub Actions for pushes and pull requests targeting the `main` branch.

The CI environment:

1. checks out the repository;
2. configures Python;
3. installs dependencies from `requirements.txt`;
4. provides isolated test environment configuration; and
5. runs:

```bash
python -m pytest -v
```

The final CI workflow successfully completed the ResolveAI automated test suite with **32 passing tests**.

Running the tests in GitHub Actions provides evidence that the test suite succeeds outside the developer's local environment and provides automated regression checking for repository changes.

### 5.12 Container and Deployment Testing

Automated testing was supplemented with integration and deployment testing.

The Docker image was built locally and the containerized application was tested to verify:

- application startup;
- dashboard access;
- incident creation;
- incident retrieval;
- AI diagnosis;
- RAG retrieval; and
- runbook source attribution.

The containerized application was subsequently deployed to Render and tested through the public web interface.

Production verification covered the end-to-end workflow of:

1. creating an incident;
2. opening the incident;
3. updating its status;
4. requesting an AI diagnosis;
5. receiving structured diagnostic information;
6. retrieving and displaying relevant runbook sources; and
7. recording AI diagnosis feedback.

### 5.13 Deployment Defect Identified Through Testing

Production testing identified a deployment-specific performance issue that was not present during local execution.

On the first AI diagnosis request, the FastEmbed model needed to initialize and download required model artifacts. On the resource-constrained hosting environment, this operation exceeded Gunicorn's default worker timeout.

The production logs reported a worker timeout and termination.

The Gunicorn configuration was therefore changed to use:

```text
--workers 1
--timeout 180
```

The single-worker configuration limits unnecessary memory duplication, while the extended timeout allows first-time AI/RAG initialization to complete.

After redeployment, the production AI diagnosis successfully completed and returned both structured analysis and relevant runbook sources.

This demonstrated the importance of testing the application in its actual deployment environment rather than relying exclusively on local and automated tests.

### 5.14 Testing Outcome

At the completion of implementation and deployment:

- **32 automated tests were passing;**
- the GitHub Actions CI workflow was passing;
- the Dockerized application was successfully tested locally;
- the application was successfully deployed to Render; and
- the deployed AI and RAG workflow was verified end-to-end.

Together, automated, integration, regression, container, and deployment testing provided coverage across both the individual application components and the complete user workflow.

---

## 6. Deployment Options and Cost Analysis

Several deployment approaches were considered for ResolveAI. The primary requirements were support for Python and Flask, Docker compatibility, environment-variable management, outbound access to the Groq API, and sufficient resources to operate the FastEmbed and ChromaDB components.

### 6.1 Render

Render was selected for the capstone deployment.

The Docker image built from the project's `Dockerfile` is deployed as a Render Web Service. Sensitive configuration, including the Groq API key, is supplied through environment variables rather than stored in the repository.

Render was appropriate for the capstone because it provides:

- GitHub repository integration;
- Docker-based deployment;
- environment-variable management;
- deployment logs;
- automatic deployment following repository changes;
- a publicly accessible HTTPS endpoint; and
- a free-tier option suitable for demonstration and evaluation.

The capstone deployment uses the available free-tier service, resulting in a hosting cost of **$0 for the project demonstration**.

The free deployment does introduce limitations. The service may spin down after inactivity, resulting in increased latency on the first request after a period of inactivity. The limited compute resources also affected the initial FastEmbed model initialization during production testing.

For a production system with regular traffic, a paid service tier with additional CPU, memory, persistent storage, and reduced cold-start behavior would be more appropriate.

### 6.2 Alternative Platform-as-a-Service Deployment

An alternative approach would be to deploy ResolveAI to another container-capable platform-as-a-service provider.

This approach could provide similar capabilities, including managed application deployment, environment configuration, HTTPS, application logs, and scaling.

The cost would depend on the selected provider, compute resources, persistent storage requirements, and traffic volume. Entry-level paid application hosting commonly uses monthly resource-based pricing rather than requiring the organization to manage a complete virtual server.

This approach would remain operationally simpler than managing the underlying server infrastructure directly.

### 6.3 Virtual Private Server or Cloud Virtual Machine

ResolveAI could also be deployed to a virtual private server or cloud virtual machine.

In this model, the Docker container could run behind a reverse proxy such as Nginx, with HTTPS certificates and process management configured on the server.

This approach would provide greater control over:

- CPU and memory allocation;
- persistent application storage;
- networking;
- operating-system configuration;
- container lifecycle; and
- scaling strategy.

However, it would also require additional operational responsibilities, including server patching, security configuration, backups, monitoring, TLS configuration, and availability management.

The total cost would depend on the selected infrastructure provider and server specification. A small application could begin on a low-cost virtual machine, but production costs would increase as redundancy, backups, monitoring, and additional resources are introduced.

### 6.4 Database Considerations

SQLite is appropriate for the current prototype because the application has a controlled scope and low expected concurrency.

However, the current SQLite database is stored within the application's runtime filesystem. This is not an ideal long-term production architecture for a horizontally scalable web service.

A production deployment would preferably use a managed relational database such as PostgreSQL.

Moving to a managed database would provide:

- durable external persistence;
- improved concurrent access;
- database backups;
- easier scaling;
- separation between application containers and persistent data.

Because ResolveAI uses SQLAlchemy, migrating from SQLite to PostgreSQL would require substantially less application-level change than an implementation tightly coupled to SQLite-specific queries.

### 6.5 Vector Store Considerations

The current deployment uses ChromaDB as a local persistent vector store.

For the capstone, the runbook collection is small enough to be rebuilt automatically when necessary. ResolveAI detects an empty collection and generates the required embeddings from the Markdown runbooks.

This avoids requiring a separately managed vector database for the prototype.

For a larger production system containing substantially more documents, rebuilding embeddings during application initialization would become inefficient. A production architecture could instead use persistent storage for ChromaDB or adopt a managed vector database.

Such an architecture would introduce additional infrastructure cost but would provide stronger persistence, scalability, and availability for a larger knowledge base.

### 6.6 AI Service Cost

ResolveAI uses the Groq API for AI-assisted incident diagnosis.

AI service cost is separate from web application hosting and depends on factors such as:

- selected model;
- number of diagnosis requests;
- input token volume;
- retrieved runbook context size; and
- generated response length.

For the capstone, usage is limited to development, testing, and demonstration workloads.

In a production environment, AI API consumption should be monitored independently from infrastructure hosting costs. Controls such as request limits, token limits, caching, and usage monitoring could be introduced to prevent unexpected expenditure.

### 6.7 Current Capstone Deployment Cost

The current ResolveAI deployment is designed to minimize infrastructure cost while still demonstrating a complete deployed software system.

The principal infrastructure arrangement is:

| Component               | Current Approach             | Capstone Cost                                     |
| ----------------------- | ---------------------------- | ------------------------------------------------- |
| Web application hosting | Render free-tier Web Service | $0                                                |
| Application runtime     | Docker + Gunicorn            | No separate cost                                  |
| Relational database     | SQLite                       | No separate cost                                  |
| Vector database         | Local ChromaDB               | No separate cost                                  |
| Embedding model         | FastEmbed                    | No separate hosted service cost                   |
| CI                      | GitHub Actions               | No additional project cost within available usage |
| AI inference            | Groq API                     | Usage-dependent                                   |

Therefore, the core application infrastructure can be demonstrated without a dedicated paid hosting service. AI inference remains usage-dependent and would need to be included in operating-cost projections for a production deployment.

### 6.8 Recommended Production Architecture

If ResolveAI were developed beyond the capstone prototype, the recommended deployment architecture would include:

1. a paid container hosting environment with sufficient CPU and memory;
2. PostgreSQL or another managed relational database;
3. durable vector-store persistence or a managed vector database;
4. centralized application logging and monitoring;
5. secrets management for API credentials;
6. automated database migrations;
7. regular backups;
8. health checks and availability monitoring; and
9. resource and AI-usage monitoring.

The capstone architecture intentionally avoids these additional infrastructure components where they are not necessary to demonstrate the system's core software engineering and AI capabilities.

---

## 7. Software Engineering Methodology and Agile Delivery

ResolveAI was developed using an iterative Agile approach based on Scrum principles. Although the capstone was completed individually, Scrum practices were used to organize requirements, plan development increments, track implementation tasks, and review progress.

GitHub Issues and GitHub Projects were used as the primary project-management tools.

### 7.1 Product Backlog

The project began with a product backlog containing eight core user stories:

- US-001 — Create an incident
- US-002 — View incident history
- US-003 — Update incident status
- US-004 — Analyze an incident with AI
- US-005 — Retrieve troubleshooting runbooks
- US-006 — Search and filter incidents
- US-007 — View incident analytics
- US-008 — Rate AI diagnosis

Each user story represented functionality that provided a distinct capability to the user.

Larger user stories were decomposed into implementation and testing tasks using GitHub sub-issues. This provided traceability between high-level requirements and the technical work required to implement them.

### 7.2 Scrum Board

A GitHub Project named **ResolveAI Capstone Board** was used to track development.

The board contained the following workflow states:

```text
Product Backlog
Sprint 1
Sprint 2
Sprint 3
In Progress
Testing
Done
```

Items selected for a sprint were moved from the Product Backlog into the corresponding sprint column. During implementation, work progressed through `In Progress`, `Testing`, and finally `Done`.

This workflow provided a visible representation of both sprint commitments and implementation status.

### 7.3 Individual Scrum Adaptation

ResolveAI was developed as an individual capstone project rather than by a multi-person Scrum team.

Consequently, Scrum responsibilities were performed by the same developer:

- **Product Owner responsibilities:** defining the product scope, prioritizing user stories, and determining acceptance expectations.
- **Scrum Master responsibilities:** maintaining the workflow, identifying blockers, and ensuring the development process continued through the planned sprints.
- **Developer responsibilities:** designing, implementing, testing, documenting, and deploying the software.

This was an adaptation of Scrum practices for an individual project rather than an attempt to simulate separate team members.

### 7.4 Sprint 1 — Incident Management Foundation

The Sprint 1 goal was to establish the core incident-management functionality required before introducing AI capabilities.

The sprint contained:

- US-001 — Create an incident
- US-002 — View incident history
- US-003 — Update incident status

Major work completed during the sprint included:

- Flask application foundation;
- SQLite integration;
- Incident data model;
- incident creation API;
- request validation;
- incident history retrieval;
- individual incident retrieval;
- incident status updates;
- status validation; and
- automated API tests.

The sprint concluded with **11 passing automated tests**.

The sprint goal was achieved because ResolveAI had a tested incident-management foundation upon which the AI functionality could be built.

### 7.5 Sprint 2 — AI Diagnosis and Runbook Retrieval

The Sprint 2 goal was to enable ResolveAI to analyze software incidents using AI while grounding recommendations in troubleshooting runbooks.

The sprint contained:

- US-004 — Analyze an incident with AI
- US-005 — Retrieve troubleshooting runbooks

Major work completed during the sprint included:

- Groq API integration;
- structured AI incident analysis;
- severity and category classification;
- probable-cause generation;
- investigation recommendations;
- suggested resolutions;
- troubleshooting runbook knowledge base;
- runbook document ingestion;
- FastEmbed integration;
- ChromaDB vector storage;
- semantic runbook retrieval;
- RAG integration; and
- runbook source attribution.

The sprint established the principal AI capability of ResolveAI: combining incident information with retrieved troubleshooting knowledge before generating a structured diagnosis.

### 7.6 Sprint 3 — Incident Discovery, Analytics, and AI Feedback

The Sprint 3 goal was to complete the core incident-management experience by adding incident discovery, operational analytics, and user feedback for AI-generated diagnoses.

The sprint contained:

- US-006 — Search and filter incidents
- US-007 — View incident analytics
- US-008 — Rate AI diagnosis

Major work completed during the sprint included:

- incident search by title and description;
- incident filtering by status;
- combined search and filtering;
- total incident metrics;
- status distribution analytics;
- severity persistence;
- severity distribution analytics;
- AI diagnosis feedback;
- feedback persistence; and
- additional automated tests.

At the completion of Sprint 3, the full automated test suite contained **32 passing tests**.

All eight planned core user stories had therefore been implemented by the end of the three development sprints.

### 7.7 Sprint Reviews

Sprint reviews were recorded in:

```text
docs/sprint-reviews.md
```

Each review documents:

- the sprint goal;
- completed user stories;
- completed functionality;
- testing performed; and
- the sprint outcome.

Maintaining sprint reviews provided a record of incremental progress rather than documenting the development process only after implementation was complete.

### 7.8 Post-Sprint Engineering Work

After the three feature-development sprints were completed, additional engineering work was tracked through GitHub Issues.

This work included:

- #38 — Build ResolveAI web interface
- #39 — Containerize ResolveAI for deployment
- #40 — Add GitHub Actions CI pipeline
- #41 — Deploy ResolveAI to Render
- #42 — Create design and testing documentation

Separating this work from the three core feature sprints preserved the sprint history while allowing production-readiness, deployment, and capstone documentation activities to remain visible on the project board.

### 7.9 Version Control

Git and GitHub were used for source control.

Changes were committed incrementally as functionality was completed. Commit messages were associated with relevant GitHub issue numbers where appropriate, creating traceability between project-management tasks and repository changes.

Sensitive configuration such as the real `.env` file and generated local database/vector-store artifacts were excluded from version control.

### 7.10 Continuous Integration

GitHub Actions was introduced as part of the project's engineering workflow.

The CI pipeline automatically runs the automated test suite for pushes and pull requests targeting the `main` branch.

During CI implementation, the pipeline identified an application-context issue in an AI analysis test that had to be corrected before the workflow could pass. After the fix, the GitHub Actions test job completed successfully.

This demonstrates that CI was used as an active quality-control mechanism rather than being included only as a project artifact.

### 7.11 Continuous Deployment Workflow

ResolveAI's deployment process connects the GitHub repository, Docker configuration, and Render hosting environment.

The workflow is:

```text
Developer Change
      |
      v
Git Commit / Push
      |
      v
GitHub Repository
      |
      +--------------------+
      |                    |
      v                    v
GitHub Actions          Render
      |                    |
      v                    v
Automated Tests       Docker Build
                           |
                           v
                     Web Deployment
```

GitHub Actions provides automated test validation, while Render builds and deploys the Dockerized application from the repository.

Production deployment testing subsequently identified the Gunicorn timeout issue during first-time RAG initialization. The deployment configuration was adjusted and redeployed, after which the complete AI and RAG workflow succeeded.

### 7.12 Methodology Outcome

The Agile process divided ResolveAI into manageable increments:

1. establish reliable incident management;
2. introduce AI diagnosis and retrieval;
3. complete operational features and feedback;
4. add the user interface and production engineering;
5. verify the system through CI and deployment testing; and
6. document the completed architecture, methodology, and testing evidence.

The three planned development sprints were completed, all eight core user stories were delivered, and the resulting application progressed from a basic Flask API to a tested, containerized, continuously tested, publicly deployed AI-powered web application.

---

## 8. Limitations and Future Improvements

ResolveAI satisfies the scope defined for the capstone, but several limitations remain because the project was intentionally designed as a focused prototype rather than a production-scale incident management platform.

### 8.1 SQLite Persistence

The current application uses SQLite. This is sufficient for the capstone workload but is not ideal for high concurrency, horizontal scaling, or durable cloud persistence.

A production version should migrate to a managed relational database such as PostgreSQL and introduce formal database migrations.

### 8.2 Ephemeral Hosting Storage

The current Render deployment relies on the application's local filesystem. Data stored in SQLite or the local ChromaDB vector store should therefore not be treated as permanently durable production data.

A production architecture should use external persistent storage for incident data and durable storage or a managed service for vector data.

### 8.3 Cold-Start Performance

The free hosting environment may spin down during inactivity. In addition, FastEmbed model initialization can increase the latency of the first AI diagnosis after a fresh deployment or restart.

This behavior was observed during deployment testing and required an increased Gunicorn timeout.

Future improvements could include:

- a hosting tier with additional memory and CPU;
- persistent model caching;
- application warm-up;
- pre-building the runbook index during deployment; or
- using a dedicated embedding service.

### 8.4 Limited Knowledge Base

The current RAG knowledge base contains a small curated set of troubleshooting runbooks covering areas such as API errors, authentication, databases, deployment, Docker, networking, performance, and WebSockets.

This is sufficient to demonstrate semantic retrieval and grounded AI diagnosis, but a production platform would require a significantly larger and continuously maintained knowledge base.

Future versions could support runbook upload, versioning, re-indexing, document management, and organization-specific knowledge bases.

### 8.5 AI Reliability

AI-generated diagnoses are recommendations rather than guaranteed root-cause determinations.

Although retrieval-augmented generation provides relevant troubleshooting context and source attribution, the language model may still produce incomplete or incorrect conclusions.

ResolveAI therefore should support human engineering judgment rather than automatically executing remediation actions.

Future evaluation could introduce a benchmark dataset of known incidents and expected diagnoses to measure classification accuracy, retrieval quality, and recommendation usefulness systematically.

### 8.6 Authentication and Authorization

Authentication and role-based access control were intentionally excluded from the capstone scope.

A production incident-management system should authenticate users and restrict actions based on organizational roles and permissions.

### 8.7 External Engineering Integrations

ResolveAI currently requires incidents to be created directly through its interface or API.

A future version could integrate with systems such as:

- monitoring and observability platforms;
- source-control platforms;
- issue trackers;
- deployment systems;
- communication platforms; and
- cloud infrastructure providers.

These integrations could allow incidents and supporting diagnostic information to be created automatically from real operational events.

### 8.8 Automated Remediation

ResolveAI provides investigation and resolution recommendations but does not automatically execute infrastructure or application changes.

This limitation is intentional. Automated remediation would introduce significant security, authorization, auditability, and reliability requirements.

A future system could introduce carefully controlled remediation workflows with explicit human approval and complete audit logging.

### 8.9 AI Feedback Analysis

ResolveAI currently stores whether a user considered a diagnosis helpful or not helpful.

A future version could aggregate this information into AI quality metrics and use feedback to identify:

- poorly performing incident categories;
- weak runbook coverage;
- retrieval failures; and
- opportunities to improve prompts or knowledge-base content.

---

## 9. Conclusion

ResolveAI demonstrates the design, implementation, testing, and deployment of an AI-enabled software engineering system for incident diagnosis and management.

The project combines conventional software engineering capabilities—including REST APIs, relational persistence, validation, automated testing, containerization, continuous integration, and cloud deployment—with AI engineering techniques including structured LLM output, vector embeddings, semantic retrieval, retrieval-augmented generation, and source attribution.

Development was organized across three Agile sprints containing eight core user stories. The sprint process established the incident-management foundation first, introduced AI diagnosis and RAG second, and completed search, analytics, and AI feedback functionality third.

The completed system was supplemented with a web interface, Docker deployment configuration, GitHub Actions continuous integration, and a public Render deployment.

Testing was performed at multiple levels. The final automated suite contained **32 passing tests**, the GitHub Actions CI pipeline completed successfully, the Dockerized application was verified locally, and the deployed application was tested through its complete incident-to-diagnosis workflow.

Deployment testing also identified a production-specific worker timeout during initial embedding-model initialization. Resolving this issue demonstrated the value of testing under actual hosting constraints in addition to local and automated testing.

The resulting capstone demonstrates an end-to-end software engineering lifecycle: requirements and backlog definition, iterative Agile implementation, architecture and design decisions, AI integration, automated testing, continuous integration, containerization, cloud deployment, production debugging, and technical documentation.

ResolveAI therefore provides both a functional AI-assisted incident management application and evidence of the engineering practices used to design, validate, and deliver it.
