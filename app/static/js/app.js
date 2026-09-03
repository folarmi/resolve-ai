const createModal = document.getElementById("incident-modal");

const detailsModal = document.getElementById("details-modal");

const openButton = document.getElementById("open-create-incident");

const closeButton = document.getElementById("close-create-incident");

const cancelButton = document.getElementById("cancel-create-incident");

const closeDetailsButton = document.getElementById("close-details");

const incidentForm = document.getElementById("incident-form");

const incidentList = document.getElementById("incident-list");

const searchInput = document.getElementById("incident-search");

const statusFilter = document.getElementById("status-filter");

const updateStatusButton = document.getElementById("update-status");

const runAnalysisButton = document.getElementById("run-analysis");

const helpfulButton = document.getElementById("feedback-helpful");

const notHelpfulButton = document.getElementById("feedback-not-helpful");

let selectedIncidentId = null;

function openCreateModal() {
  createModal.classList.remove("hidden");
}

function closeCreateModal() {
  createModal.classList.add("hidden");
}

function openDetailsModal() {
  detailsModal.classList.remove("hidden");
}

function closeDetailsModal() {
  detailsModal.classList.add("hidden");

  selectedIncidentId = null;
}

function escapeHtml(value) {
  const div = document.createElement("div");

  div.textContent = value ?? "";

  return div.innerHTML;
}

function getSeverityBadge(severity) {
  if (!severity) {
    return "";
  }

  return `
        <span class="badge">
            ${escapeHtml(severity)}
        </span>
    `;
}

function renderIncidents(incidents) {
  if (!incidents.length) {
    incidentList.innerHTML = `
            <div class="empty-state">
                <h4>No incidents found</h4>

                <p>
                    Create an incident or adjust your
                    search and filters.
                </p>
            </div>
        `;

    return;
  }

  incidentList.innerHTML = incidents
    .map(
      (incident) => `
                <article
                    class="incident-card"
                    data-incident-id="${escapeHtml(incident.id)}"
                >
                    <h4>
                        ${escapeHtml(incident.title)}
                    </h4>

                    <p>
                        ${escapeHtml(incident.description)}
                    </p>

                    <div class="incident-meta">
                        <span class="badge">
                            ${escapeHtml(incident.status)}
                        </span>

                        ${getSeverityBadge(incident.severity)}
                    </div>
                </article>
            `,
    )
    .join("");
}

async function loadAnalytics() {
  try {
    const response = await fetch("/api/analytics");

    if (!response.ok) {
      throw new Error("Unable to load analytics");
    }

    const data = await response.json();

    document.getElementById("total-incidents").textContent =
      data.total_incidents;

    document.getElementById("open-incidents").textContent =
      data.status_counts.Open;

    document.getElementById("investigating-incidents").textContent =
      data.status_counts.Investigating;

    document.getElementById("resolved-incidents").textContent =
      data.status_counts.Resolved;
  } catch (error) {
    console.error("Analytics error:", error);
  }
}

async function loadIncidents() {
  try {
    const search = searchInput.value.trim();

    const status = statusFilter.value;

    const params = new URLSearchParams();

    if (search) {
      params.set("search", search);
    }

    if (status) {
      params.set("status", status);
    }

    const queryString = params.toString();

    const url = queryString
      ? `/api/incidents?${queryString}`
      : "/api/incidents";

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error("Unable to load incidents");
    }

    const data = await response.json();

    renderIncidents(data.incidents || []);
  } catch (error) {
    console.error("Incident loading error:", error);
  }
}

async function createIncident(event) {
  event.preventDefault();

  const title = document.getElementById("incident-title").value.trim();

  const description = document
    .getElementById("incident-description")
    .value.trim();

  const logs = document.getElementById("incident-logs").value.trim();

  try {
    const response = await fetch("/api/incidents", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        title,
        description,
        logs: logs || null,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Unable to create incident");
    }

    incidentForm.reset();

    closeCreateModal();

    await Promise.all([loadIncidents(), loadAnalytics()]);
  } catch (error) {
    alert(error.message);
  }
}

function resetAnalysisView() {
  document.getElementById("analysis-empty").classList.remove("hidden");

  document.getElementById("analysis-content").classList.add("hidden");

  document.getElementById("details-message").textContent = "";

  document.getElementById("feedback-message").textContent = "";
}

function populateIncidentDetails(incident) {
  document.getElementById("details-title").textContent = incident.title;

  document.getElementById("details-description").textContent =
    incident.description;

  document.getElementById("details-logs").textContent =
    incident.logs || "No logs were provided.";

  document.getElementById("details-status").value = incident.status;

  document.getElementById("details-severity").textContent =
    incident.severity || "Unclassified";

  if (incident.ai_feedback_helpful === true) {
    document.getElementById("feedback-message").textContent =
      "You rated this diagnosis as helpful.";
  }

  if (incident.ai_feedback_helpful === false) {
    document.getElementById("feedback-message").textContent =
      "You rated this diagnosis as not helpful.";
  }
}

async function openIncidentDetails(incidentId) {
  selectedIncidentId = incidentId;

  resetAnalysisView();

  try {
    const response = await fetch(`/api/incidents/${incidentId}`);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Unable to load incident");
    }

    populateIncidentDetails(data.incident);

    openDetailsModal();
  } catch (error) {
    alert(error.message);
  }
}

async function updateIncidentStatus() {
  if (!selectedIncidentId) {
    return;
  }

  const status = document.getElementById("details-status").value;

  try {
    const response = await fetch(
      `/api/incidents/${selectedIncidentId}/status`,
      {
        method: "PATCH",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          status,
        }),
      },
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Unable to update status");
    }

    document.getElementById("details-message").textContent =
      "Incident status updated.";

    await Promise.all([loadIncidents(), loadAnalytics()]);
  } catch (error) {
    document.getElementById("details-message").textContent = error.message;
  }
}

function renderList(elementId, values) {
  const element = document.getElementById(elementId);

  element.innerHTML = "";

  (values || []).forEach((value) => {
    const item = document.createElement("li");

    item.textContent = value;

    element.appendChild(item);
  });
}

function renderSources(sources) {
  const container = document.getElementById("analysis-sources");

  container.innerHTML = "";

  if (!sources || !sources.length) {
    container.textContent = "No runbook sources returned.";

    return;
  }

  sources.forEach((source) => {
    const chip = document.createElement("span");

    chip.className = "source-chip";

    chip.textContent = source;

    container.appendChild(chip);
  });
}

function renderAnalysis(analysis) {
  document.getElementById("analysis-empty").classList.add("hidden");

  document.getElementById("analysis-content").classList.remove("hidden");

  document.getElementById("analysis-severity").textContent =
    analysis.severity || "Unclassified";

  document.getElementById("analysis-category").textContent =
    analysis.category || "Unknown";

  document.getElementById("analysis-summary").textContent =
    analysis.summary || "";

  renderList("analysis-causes", analysis.probable_causes);

  renderList("analysis-investigation", analysis.investigation_steps);

  renderList("analysis-resolution", analysis.suggested_resolution);

  renderSources(analysis.sources);

  document.getElementById("details-severity").textContent =
    analysis.severity || "Unclassified";
}

async function runIncidentAnalysis() {
  if (!selectedIncidentId) {
    return;
  }

  const originalText = runAnalysisButton.textContent;

  runAnalysisButton.disabled = true;

  runAnalysisButton.textContent = "Analyzing...";

  document.getElementById("details-message").textContent =
    "ResolveAI is analyzing the incident...";

  try {
    const response = await fetch(
      `/api/incidents/${selectedIncidentId}/analyze`,
      {
        method: "POST",
      },
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Unable to analyze incident");
    }

    renderAnalysis(data.analysis);

    document.getElementById("details-message").textContent =
      "AI diagnosis completed.";

    await Promise.all([loadIncidents(), loadAnalytics()]);
  } catch (error) {
    document.getElementById("details-message").textContent = error.message;
  } finally {
    runAnalysisButton.disabled = false;

    runAnalysisButton.textContent = originalText;
  }
}

async function submitFeedback(helpful) {
  if (!selectedIncidentId) {
    return;
  }

  try {
    const response = await fetch(
      `/api/incidents/${selectedIncidentId}/feedback`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          helpful,
        }),
      },
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Unable to save feedback");
    }

    document.getElementById("feedback-message").textContent = helpful
      ? "Thanks. You rated this diagnosis as helpful."
      : "Thanks. You rated this diagnosis as not helpful.";
  } catch (error) {
    document.getElementById("feedback-message").textContent = error.message;
  }
}

openButton.addEventListener("click", openCreateModal);

closeButton.addEventListener("click", closeCreateModal);

cancelButton.addEventListener("click", closeCreateModal);

closeDetailsButton.addEventListener("click", closeDetailsModal);

createModal
  .querySelector(".modal-backdrop")
  .addEventListener("click", closeCreateModal);

detailsModal
  .querySelector(".modal-backdrop")
  .addEventListener("click", closeDetailsModal);

incidentForm.addEventListener("submit", createIncident);

incidentList.addEventListener("click", (event) => {
  const card = event.target.closest(".incident-card");

  if (!card) {
    return;
  }

  openIncidentDetails(card.dataset.incidentId);
});

updateStatusButton.addEventListener("click", updateIncidentStatus);

runAnalysisButton.addEventListener("click", runIncidentAnalysis);

helpfulButton.addEventListener("click", () => {
  submitFeedback(true);
});

notHelpfulButton.addEventListener("click", () => {
  submitFeedback(false);
});

let searchTimer;

searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);

  searchTimer = setTimeout(loadIncidents, 300);
});

statusFilter.addEventListener("change", loadIncidents);

async function initializeDashboard() {
  await Promise.all([loadAnalytics(), loadIncidents()]);
}

initializeDashboard();
