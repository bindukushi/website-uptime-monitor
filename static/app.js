// Fetches /api/status and draws the dashboard.
const AUTO_REFRESH_MS = 30000;

const els = {
  total: document.getElementById("total"),
  up: document.getElementById("up"),
  down: document.getElementById("down"),
  rows: document.getElementById("rows"),
  lastChecked: document.getElementById("last-checked"),
  button: document.getElementById("refresh-btn"),
  message: document.getElementById("message"),
};

function speedClass(ms) {
  if (ms === null) return "";
  if (ms < 500) return "fast";
  if (ms < 1500) return "medium";
  return "slow";
}

function cell(text) {
  const td = document.createElement("td");
  td.textContent = text; // textContent (not innerHTML) prevents HTML injection
  return td;
}

function buildRow(site) {
  const tr = document.createElement("tr");

  const nameTd = document.createElement("td");
  const link = document.createElement("a");
  link.href = site.url;
  link.textContent = site.name;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  nameTd.appendChild(link);
  tr.appendChild(nameTd);

  const statusTd = document.createElement("td");
  const badge = document.createElement("span");
  badge.className = "badge " + site.status.toLowerCase();
  badge.textContent = site.status;
  statusTd.appendChild(badge);
  tr.appendChild(statusTd);

  tr.appendChild(cell(site.status_code ?? "-"));

  const rtTd = document.createElement("td");
  if (site.response_time_ms === null) {
    rtTd.textContent = "-";
  } else {
    const wrap = document.createElement("div");
    wrap.className = "rt " + speedClass(site.response_time_ms);
    const bar = document.createElement("div");
    bar.className = "bar";
    const fill = document.createElement("span");
    fill.style.width = Math.min(100, site.response_time_ms / 20) + "%";
    bar.appendChild(fill);
    const label = document.createElement("span");
    label.textContent = site.response_time_ms + " ms";
    wrap.append(bar, label);
    rtTd.appendChild(wrap);
  }
  tr.appendChild(rtTd);

  tr.appendChild(cell(site.error ?? "OK"));
  return tr;
}

async function refresh() {
  els.button.disabled = true;
  els.button.textContent = "Checking...";
  try {
    const res = await fetch("/api/status");
    if (!res.ok) throw new Error("Server returned " + res.status);
    const data = await res.json();

    els.total.textContent = data.summary.total;
    els.up.textContent = data.summary.up;
    els.down.textContent = data.summary.down;
    els.lastChecked.textContent = new Date(data.checked_at).toLocaleString();
    els.rows.replaceChildren(...data.websites.map(buildRow));
    els.message.hidden = true;
  } catch (err) {
    els.message.textContent = "Could not load results: " + err.message;
    els.message.hidden = false;
  } finally {
    els.button.disabled = false;
    els.button.textContent = "Refresh";
  }
}

els.button.addEventListener("click", refresh);
refresh();
setInterval(refresh, AUTO_REFRESH_MS);
