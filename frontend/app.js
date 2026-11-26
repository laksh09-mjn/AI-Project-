/* ─── GovWatch AI — Frontend Application Logic ───
   Public Scheme Expenditure Anomaly & Fraud Screening
   Laksh Mahajan (12512521) & Sankalp Jeet Singh (12512484)
*/

const API = "/api";

// ─── State ───────────────────────────────────────
let currentPage = 1;
const PER_PAGE = 20;
let lastSummary = null;
let lastRecordsList = [];
let lastFlaggedList = [];
let riskChart = null;
let schemeChart = null;
let stateChart = null;

// ─── Theme Management (Dark / Light Mode) ────────
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("govwatch_theme", theme);
  const icon = document.getElementById("themeIcon");
  const label = document.getElementById("themeLabel");
  if (theme === "dark") {
    icon.textContent = "☀️";
    label.textContent = "Light";
  } else {
    icon.textContent = "🌙";
    label.textContent = "Dark";
  }
  if (lastSummary) renderCharts(lastSummary);
}

document.getElementById("themeToggle")?.addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  applyTheme(current === "dark" ? "light" : "dark");
});

// ─── Tab Navigation ───────────────────────────────
document.querySelectorAll(".nav-item").forEach(link => {
  link.addEventListener("click", e => {
    e.preventDefault();
    activateTab(link.dataset.tab, link);
    document.getElementById("sidebar").classList.remove("open");
  });
});

function activateTab(tab, linkEl) {
  document.querySelectorAll(".nav-item").forEach(l => l.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
  if (linkEl) linkEl.classList.add("active");
  else document.querySelector(`[data-tab="${tab}"]`)?.classList.add("active");

  document.getElementById(`tab-${tab}`).classList.add("active");
  const meta = {
    dashboard: ["Dashboard", "Real-time public scheme expenditure screening"],
    records:   ["All Records", "Browse, search, and export screened expenditure entries"],
    flagged:   ["Flagged Alerts", "High & Critical risk records prioritised for audit"],
    analyze:   ["Live Screener", "Test any custom expenditure record against the AI engine"],
    about:     ["Methodology", "Statistical detection pipeline & project documentation"]
  }[tab] || [tab, ""];

  document.getElementById("pageTitle").textContent = meta[0];
  document.getElementById("pageSubtitle").textContent = meta[1];

  if (tab === "dashboard") loadDashboard();
  if (tab === "records")   loadRecords(1);
  if (tab === "flagged")   loadFlagged();
  if (tab === "analyze")   loadSchemeStateDropdowns();
}

document.getElementById("menuBtn").addEventListener("click", () => {
  document.getElementById("sidebar").classList.toggle("open");
});

// ─── Dashboard ────────────────────────────────────
async function loadDashboard() {
  try {
    const data = await apiFetch("/summary");
    lastSummary = data;
    document.getElementById("navFlagCount").textContent = data.total_flagged;

    document.getElementById("statsGrid").innerHTML = `
      <div class="stat-card info clickable" onclick="activateTab('records')">
        <div class="stat-top">
          <div class="stat-label">Total Records</div>
          <div class="stat-icon">📊</div>
        </div>
        <div class="stat-value">${data.total_records}</div>
        <div class="stat-sub">Expenditure entries screened</div>
      </div>
      <div class="stat-card danger clickable" onclick="activateTab('flagged')">
        <div class="stat-top">
          <div class="stat-label">Flagged Alerts</div>
          <div class="stat-icon">🚨</div>
        </div>
        <div class="stat-value">${data.total_flagged}</div>
        <div class="stat-sub">${data.flag_rate_pct}% high/critical flag rate</div>
      </div>
      <div class="stat-card success">
        <div class="stat-top">
          <div class="stat-label">Total Spend</div>
          <div class="stat-icon">💰</div>
        </div>
        <div class="stat-value">₹${data.total_spend_cr}Cr</div>
        <div class="stat-sub">Across 10 schemes &amp; 15 states</div>
      </div>
      <div class="stat-card warn clickable" onclick="activateTab('flagged')">
        <div class="stat-top">
          <div class="stat-label">Flagged Spend</div>
          <div class="stat-icon">⚠️</div>
        </div>
        <div class="stat-value">₹${data.flagged_spend_cr}Cr</div>
        <div class="stat-sub">Under HIGH / CRITICAL risk</div>
      </div>
    `;

    renderCharts(data);
  } catch (e) {
    showError("statsGrid", "Could not load dashboard. Is the backend server running?");
  }
}

function renderCharts(data) {
  const isDark = (document.documentElement.getAttribute("data-theme") || "dark") === "dark";
  const textColor = isDark ? "#cbd5e1" : "#475569";
  const gridColor = isDark ? "rgba(148, 163, 184, 0.12)" : "rgba(15, 23, 42, 0.08)";
  const borderColor = isDark ? "#131c31" : "#ffffff";

  const riskColors = {
    LOW: "#10b981", MEDIUM: "#f59e0b", HIGH: "#f97316", CRITICAL: "#ef4444"
  };
  const rd = data.risk_distribution;
  if (riskChart) riskChart.destroy();
  riskChart = new Chart(document.getElementById("riskChart"), {
    type: "doughnut",
    data: {
      labels: Object.keys(rd),
      datasets: [{
        data: Object.values(rd),
        backgroundColor: Object.keys(rd).map(k => riskColors[k]),
        borderWidth: 3,
        borderColor: borderColor
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: "66%",
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: textColor, font: { size: 11, weight: "600" }, padding: 14 }
        }
      }
    }
  });

  const schemeLabels = Object.keys(data.by_scheme);
  const schemeFlagged = schemeLabels.map(s => data.by_scheme[s].flagged);
  if (schemeChart) schemeChart.destroy();
  schemeChart = new Chart(document.getElementById("schemeChart"), {
    type: "bar",
    data: {
      labels: schemeLabels.map(s => s.length > 16 ? s.slice(0, 14) + "…" : s),
      datasets: [{
        label: "Flagged",
        data: schemeFlagged,
        backgroundColor: "rgba(249, 115, 22, 0.72)",
        borderColor: "#f97316",
        borderWidth: 1.5, borderRadius: 6
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: textColor, font: { size: 10 } }, grid: { display: false } },
        y: { beginAtZero: true, ticks: { color: textColor, stepSize: 1 }, grid: { color: gridColor } }
      }
    }
  });

  const stateEntries = Object.entries(data.by_state)
    .sort((a, b) => b[1].flagged - a[1].flagged)
    .slice(0, 10);
  if (stateChart) stateChart.destroy();
  stateChart = new Chart(document.getElementById("stateChart"), {
    type: "bar",
    data: {
      labels: stateEntries.map(e => e[0]),
      datasets: [{
        label: "Flagged Records",
        data: stateEntries.map(e => e[1].flagged),
        backgroundColor: "rgba(59, 130, 246, 0.72)",
        borderColor: "#3b82f6",
        borderWidth: 1.5, borderRadius: 6
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true, ticks: { color: textColor, stepSize: 1 }, grid: { color: gridColor } },
        y: { ticks: { color: textColor, font: { size: 11 } }, grid: { display: false } }
      }
    }
  });
}

// ─── Records ─────────────────────────────────────
async function loadRecords(page = 1) {
  currentPage = page;
  const scheme = document.getElementById("filterScheme")?.value || "";
  const state  = document.getElementById("filterState")?.value || "";
  const risk   = document.getElementById("filterRisk")?.value || "";
  const query  = (document.getElementById("searchInput")?.value || "").trim().toLowerCase();
  const tbody  = document.getElementById("recordsTbody");
  tbody.innerHTML = `<tr><td colspan="10" class="loading-row"><div class="spinner" style="margin:0 auto"></div></td></tr>`;

  await loadSchemeStateSideFilters();

  try {
    const data = await apiFetch(
      `/records?page=${page}&per_page=${PER_PAGE}&scheme=${encodeURIComponent(scheme)}&state=${encodeURIComponent(state)}&risk=${encodeURIComponent(risk)}`
    );
    let rows = data.records;
    if (query) {
      rows = rows.filter(r =>
        r.voucher_id.toLowerCase().includes(query) ||
        r.scheme.toLowerCase().includes(query) ||
        r.state.toLowerCase().includes(query) ||
        r.department.toLowerCase().includes(query) ||
        r.officer.toLowerCase().includes(query)
      );
    }
    lastRecordsList = rows;
    document.getElementById("recordCount").textContent = `${query ? rows.length : data.total} records`;

    tbody.innerHTML = rows.map(r => {
      const a = r.analysis;
      return `<tr>
        <td>${r.id}</td>
        <td><span class="code-chip">${r.voucher_id}</span></td>
        <td><b>${r.scheme}</b></td>
        <td>${r.state}</td>
        <td style="color:var(--text-secondary)">${r.department}</td>
        <td>${r.date}</td>
        <td style="font-weight:700">₹${fmt(r.amount)}</td>
        <td style="font-weight:600;color:${scoreColor(a.risk_score)}">${a.risk_score}</td>
        <td><span class="risk-badge risk-${a.risk_level}">${a.risk_level}</span></td>
        <td><button class="btn btn-sm" onclick="showDetail(${r.id})">Inspect</button></td>
      </tr>`;
    }).join("") || `<tr><td colspan="10" style="text-align:center;padding:32px;color:var(--text-muted)">No matching records found</td></tr>`;

    renderPagination(data.total, page, PER_PAGE);
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="10" class="loading-row" style="color:#ef4444">Error loading records. Backend offline?</td></tr>`;
  }
}

function renderPagination(total, page, perPage) {
  const pages = Math.ceil(total / perPage);
  const el = document.getElementById("pagination");
  if (pages <= 1) { el.innerHTML = ""; return; }
  let html = "";
  for (let i = 1; i <= Math.min(pages, 10); i++) {
    html += `<button class="page-btn${i === page ? " active" : ""}" onclick="loadRecords(${i})">${i}</button>`;
  }
  if (pages > 10) html += `<span style="color:var(--text-muted);font-size:.8rem">… ${pages} pages</span>`;
  el.innerHTML = html;
}

document.getElementById("applyFilters")?.addEventListener("click", () => loadRecords(1));
document.getElementById("searchInput")?.addEventListener("input", () => loadRecords(currentPage));

let _sideFiltersLoaded = false;
async function loadSchemeStateSideFilters() {
  if (_sideFiltersLoaded) return;
  _sideFiltersLoaded = true;
  try {
    const [schemes, states] = await Promise.all([apiFetch("/schemes"), apiFetch("/states")]);
    const fScheme = document.getElementById("filterScheme");
    const fState = document.getElementById("filterState");
    schemes.schemes.forEach(s => {
      const o = document.createElement("option"); o.value = s; o.textContent = s; fScheme.appendChild(o);
    });
    states.states.forEach(s => {
      const o = document.createElement("option"); o.value = s; o.textContent = s; fState.appendChild(o);
    });
  } catch (e) {}
}

// ─── Flagged Records ──────────────────────────────
async function loadFlagged() {
  const tbody = document.getElementById("flaggedTbody");
  tbody.innerHTML = `<tr><td colspan="9" class="loading-row"><div class="spinner" style="margin:0 auto"></div></td></tr>`;
  try {
    const data = await apiFetch("/flagged");
    lastFlaggedList = data.records;
    document.getElementById("navFlagCount").textContent = data.total_flagged;
    document.getElementById("flaggedBanner").textContent =
      `${data.total_flagged} record(s) flagged as HIGH/CRITICAL risk — Total flagged spend: ₹${data.flagged_spend_cr} Crore.`;
    tbody.innerHTML = data.records.map(r => {
      const a = r.analysis;
      const flagsHtml = a.flags.length
        ? a.flags.map(f => `<span class="risk-badge risk-HIGH" style="font-size:.68rem;margin:1px">${f.type}</span>`).join(" ")
        : "<span style='color:var(--text-muted)'>—</span>";
      return `<tr>
        <td>${r.id}</td>
        <td><span class="code-chip">${r.voucher_id}</span></td>
        <td><b>${r.scheme}</b></td>
        <td>${r.state}</td>
        <td style="font-weight:700">₹${fmt(r.amount)}</td>
        <td>
          <div style="display:flex;align-items:center;gap:7px">
            <div style="width:54px;height:6px;background:var(--border);border-radius:3px;overflow:hidden">
              <div style="width:${a.risk_score}%;height:100%;background:${scoreColor(a.risk_score)};border-radius:3px"></div>
            </div>
            <span style="font-size:.8rem;font-weight:700">${a.risk_score}</span>
          </div>
        </td>
        <td><span class="risk-badge risk-${a.risk_level}">${a.risk_level}</span></td>
        <td>${flagsHtml}</td>
        <td><button class="btn btn-sm" onclick="showDetail(${r.id})">Inspect</button></td>
      </tr>`;
    }).join("") || `<tr><td colspan="9" style="text-align:center;padding:30px;color:var(--text-muted)">No flagged records</td></tr>`;
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="9" class="loading-row" style="color:#ef4444">Error loading. Backend offline?</td></tr>`;
  }
}

// ─── Analyze Custom Record ────────────────────────
let _analyzeDropdownsLoaded = false;
async function loadSchemeStateDropdowns() {
  if (_analyzeDropdownsLoaded) return;
  _analyzeDropdownsLoaded = true;
  try {
    const [schemes, states] = await Promise.all([apiFetch("/schemes"), apiFetch("/states")]);
    const aScheme = document.getElementById("aScheme");
    const aState = document.getElementById("aState");
    aScheme.innerHTML = "";
    aState.innerHTML = "";
    schemes.schemes.forEach(s => {
      const o = document.createElement("option"); o.value = s; o.textContent = s; aScheme.appendChild(o);
    });
    states.states.forEach(s => {
      const o = document.createElement("option"); o.value = s; o.textContent = s; aState.appendChild(o);
    });
    document.getElementById("aDate").value = new Date().toISOString().slice(0, 10);
  } catch (e) {}
}

async function fillPreset(type) {
  await loadSchemeStateDropdowns();
  document.getElementById("aScheme").selectedIndex = 0;
  document.getElementById("aState").selectedIndex = 0;
  document.getElementById("aDept").value = "Rural Development";
  document.getElementById("aOfficer").value = "Officer-412";
  document.getElementById("aDate").value = "2024-08-15";

  if (type === "normal") {
    document.getElementById("aAmount").value = "22000000";
    document.getElementById("aVoucher").value = "VCH-20410";
  } else if (type === "spike") {
    document.getElementById("aAmount").value = "480000000";
    document.getElementById("aVoucher").value = "VCH-99812";
  } else if (type === "zero") {
    document.getElementById("aAmount").value = "12000";
    document.getElementById("aVoucher").value = "VCH-00109";
  }
  showToast(`Loaded "${type}" preset — click Run AI Risk Screening`);
}

document.getElementById("analyzeBtn")?.addEventListener("click", async () => {
  const btn = document.getElementById("analyzeBtn");
  const scheme = document.getElementById("aScheme").value;
  const state  = document.getElementById("aState").value;
  const amount = document.getElementById("aAmount").value;
  const date   = document.getElementById("aDate").value;
  if (!scheme || !state || !amount || !date) {
    showToast("Please fill in all required fields (*)");
    return;
  }
  btn.textContent = "Screening…"; btn.disabled = true;
  try {
    const result = await apiPost("/analyze/custom", {
      scheme, state,
      department: document.getElementById("aDept").value,
      amount: parseFloat(amount),
      date,
      officer: document.getElementById("aOfficer").value,
      voucher_id: document.getElementById("aVoucher").value
    });
    renderAnalysisResult(result);
    showToast(`Screening complete — ${result.analysis.risk_level} risk`);
  } catch (e) {
    showToast("Analysis failed. Check backend connection.");
  } finally {
    btn.textContent = "Run AI Risk Screening"; btn.disabled = false;
  }
});

function renderAnalysisResult(r) {
  const a = r.analysis;
  document.getElementById("resultEmpty").style.display = "none";
  document.getElementById("resultContent").style.display = "block";

  const header = document.getElementById("resultHeader");
  header.className = `result-header ${a.risk_level}`;
  header.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap">
      <div style="display:flex;align-items:center;gap:16px">
        <div>
          <div class="result-score" style="color:${scoreColor(a.risk_score)}">${a.risk_score}</div>
          <div class="result-label">Risk Score / 100</div>
        </div>
        <div>
          <span class="risk-badge risk-${a.risk_level}" style="font-size:.86rem;padding:5px 14px">${a.risk_level} RISK</span>
          <div style="font-size:.76rem;color:var(--text-secondary);margin-top:5px">Baseline Confidence: <b>${a.confidence}</b></div>
        </div>
      </div>
    </div>
  `;

  document.getElementById("resultBody").innerHTML = `
    <div class="result-section">
      <h4>📊 Statistical Signals</h4>
      <div class="metric-row"><span class="metric-label">Z-Score</span><span class="metric-value">${a.z_score}</span></div>
      <div class="metric-row"><span class="metric-label">IQR Deviation</span><span class="metric-value">${a.iqr_deviation}</span></div>
      <div class="metric-row"><span class="metric-label">Expected Group Spend</span><span class="metric-value">₹${fmt(a.expected_amount)}</span></div>
      <div class="metric-row"><span class="metric-label">Deviation from Mean</span><span class="metric-value" style="color:${a.deviation_percent > 0 ? '#ef4444' : '#10b981'}">${a.deviation_percent > 0 ? '+' : ''}${a.deviation_percent}%</span></div>
    </div>

    ${a.flags.length ? `
    <div class="result-section">
      <h4>⚑ Triggered Rules (${a.flags.length})</h4>
      <ul class="flags-list">
        ${a.flags.map(f => `<li><span class="flag-type">${f.type}</span><span>${f.detail}</span></li>`).join("")}
      </ul>
    </div>` : ""}

    <div class="result-section">
      <h4>🧠 AI Explanation</h4>
      <p>${a.explanation}</p>
    </div>

    <div class="result-section">
      <h4>📋 Audit Recommendation</h4>
      <p style="background:var(--surface-muted);padding:12px 14px;border-radius:10px;border:1px solid var(--border)">${a.recommendation}</p>
    </div>
  `;
}

// ─── Detail Modal ─────────────────────────────────
async function showDetail(id) {
  const overlay = document.getElementById("modalOverlay");
  const body = document.getElementById("modalBody");
  document.getElementById("modalTitle").textContent = `Record #${id} — Audit Inspection`;
  body.innerHTML = `<div style="text-align:center;padding:40px"><div class="spinner" style="margin:0 auto"></div></div>`;
  overlay.classList.add("open");

  try {
    const r = await apiFetch(`/analyze/${id}`);
    const a = r.analysis;
    body.innerHTML = `
      <div style="margin-bottom:16px">
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px">
          <span class="risk-badge risk-${a.risk_level}" style="font-size:.82rem">${a.risk_level} RISK — Score: ${a.risk_score}/100</span>
          <span class="code-chip">Confidence: ${a.confidence}</span>
        </div>
        <div class="metric-row"><span class="metric-label">Scheme</span><span class="metric-value">${r.scheme}</span></div>
        <div class="metric-row"><span class="metric-label">State</span><span class="metric-value">${r.state}</span></div>
        <div class="metric-row"><span class="metric-label">Department</span><span class="metric-value">${r.department}</span></div>
        <div class="metric-row"><span class="metric-label">Reported Amount</span><span class="metric-value" style="font-size:1.05rem">₹${fmt(r.amount)}</span></div>
        <div class="metric-row"><span class="metric-label">Expected Spend</span><span class="metric-value">₹${fmt(a.expected_amount)}</span></div>
        <div class="metric-row"><span class="metric-label">Deviation</span><span class="metric-value" style="color:${a.deviation_percent > 50 ? '#ef4444' : 'var(--text-primary)'}">${a.deviation_percent > 0 ? '+' : ''}${a.deviation_percent}%</span></div>
        <div class="metric-row"><span class="metric-label">Z-Score / IQR</span><span class="metric-value">${a.z_score} / ${a.iqr_deviation}</span></div>
        <div class="metric-row"><span class="metric-label">Date</span><span class="metric-value">${r.date} (${r.quarter})</span></div>
        <div class="metric-row"><span class="metric-label">Officer / Voucher</span><span class="metric-value">${r.officer} &bull; <span class="code-chip">${r.voucher_id}</span></span></div>
      </div>

      ${a.flags.length ? `
        <div style="margin-bottom:16px">
          <h4 style="font-size:.76rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">⚑ Anomaly Flags</h4>
          <ul class="flags-list">
            ${a.flags.map(f => `<li><span class="flag-type">${f.type}</span><span>${f.detail}</span></li>`).join("")}
          </ul>
        </div>
      ` : ""}

      <div style="background:var(--surface-muted);border:1px solid var(--border);border-radius:12px;padding:14px;margin-bottom:12px">
        <h4 style="font-size:.76rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px">🧠 AI Explanation</h4>
        <p style="font-size:.84rem;color:var(--text-primary);line-height:1.65">${a.explanation}</p>
      </div>

      <div style="background:rgba(245, 158, 11, 0.12);border:1px solid rgba(245, 158, 11, 0.3);border-radius:12px;padding:14px">
        <h4 style="font-size:.76rem;font-weight:700;color:#f59e0b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px">📋 Recommendation</h4>
        <p style="font-size:.84rem;color:var(--text-primary);line-height:1.65">${a.recommendation}</p>
      </div>
    `;
  } catch (e) {
    body.innerHTML = `<p style="color:#ef4444">Failed to load record details.</p>`;
  }
}

document.getElementById("modalClose").addEventListener("click", () => {
  document.getElementById("modalOverlay").classList.remove("open");
});
document.getElementById("modalOverlay").addEventListener("click", e => {
  if (e.target === e.currentTarget)
    document.getElementById("modalOverlay").classList.remove("open");
});

// ─── CSV Export ───────────────────────────────────
function downloadCSV(rows, filename) {
  if (!rows || !rows.length) { showToast("No records to export"); return; }
  const headers = ["ID", "Voucher", "Scheme", "State", "Department", "Date", "Amount", "RiskScore", "RiskLevel"];
  const lines = [headers.join(",")];
  rows.forEach(r => {
    lines.push([
      r.id, r.voucher_id, `"${r.scheme}"`, `"${r.state}"`, `"${r.department}"`,
      r.date, r.amount, r.analysis.risk_score, r.analysis.risk_level
    ].join(","));
  });
  const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  showToast(`Exported ${rows.length} rows to ${filename}`);
}

document.getElementById("exportRecordsBtn")?.addEventListener("click", () => downloadCSV(lastRecordsList, "govwatch_records.csv"));
document.getElementById("exportFlaggedBtn")?.addEventListener("click", () => downloadCSV(lastFlaggedList, "govwatch_flagged_alerts.csv"));

// ─── Helpers ──────────────────────────────────────
async function apiFetch(path) {
  const res = await fetch(API + path);
  if (!res.ok) throw new Error(res.status);
  return res.json();
}
async function apiPost(path, body) {
  const res = await fetch(API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error(res.status);
  return res.json();
}

function fmt(n) {
  if (n >= 1e7) return (n / 1e7).toFixed(2) + " Cr";
  if (n >= 1e5) return (n / 1e5).toFixed(1) + " L";
  return new Intl.NumberFormat("en-IN").format(Math.round(n));
}

function scoreColor(score) {
  if (score >= 70) return "#ef4444";
  if (score >= 50) return "#f97316";
  if (score >= 25) return "#f59e0b";
  return "#10b981";
}

function showToast(msg) {
  const box = document.getElementById("toastContainer");
  const el = document.createElement("div");
  el.className = "toast";
  el.textContent = msg;
  box.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

function showError(id, msg) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = `<div style="color:#ef4444;padding:20px">${msg}</div>`;
}

// ─── Init ─────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("govwatch_theme") || "dark";
  applyTheme(savedTheme);
  loadDashboard();
});
