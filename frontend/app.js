const apiBase = "";
const state = { campaigns: [], current: null };

const els = {
  campaigns: document.getElementById("campaign-list"),
  refresh: document.getElementById("refresh"),
  campaignForm: document.getElementById("campaign-form"),
  playerForm: document.getElementById("player-form"),
  dmForm: document.getElementById("dm-form"),
  diceForm: document.getElementById("dice-form"),
  details: document.getElementById("campaign-details"),
  title: document.getElementById("campaign-title"),
  meta: document.getElementById("campaign-meta"),
  summary: document.getElementById("campaign-summary"),
  players: document.getElementById("player-list"),
  log: document.getElementById("log"),
  dmReply: document.getElementById("dm-reply"),
  dmGuidance: document.getElementById("dm-guidance"),
  dmResponse: document.getElementById("dm-response"),
  diceResult: document.getElementById("dice-result"),
  refreshLog: document.getElementById("refresh-log"),
  clearLog: document.getElementById("clear-log"),
  deleteCampaign: document.getElementById("delete-campaign"),
  downloadLog: document.getElementById("download-log"),
};

async function request(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    const message = detail.detail || res.statusText;
    throw new Error(message);
  }
  return res.json();
}

async function loadCampaigns() {
  state.campaigns = await request(`${apiBase}/api/campaigns`);
  els.campaigns.innerHTML = "";
  state.campaigns.forEach((c) => {
    const li = document.createElement("li");
    li.textContent = `${c.title}`;
    li.title = c.summary || "No summary provided";
    if (state.current && state.current.id === c.id) li.classList.add("active");
    li.addEventListener("click", () => selectCampaign(c.id));
    els.campaigns.appendChild(li);
  });
}

async function selectCampaign(id) {
  state.current = await request(`${apiBase}/api/campaigns/${id}`);
  renderCampaign(state.current);
  await loadLog();
  els.details.hidden = false;
  els.deleteCampaign.disabled = false;
}

function renderCampaign(campaign) {
  els.title.textContent = campaign.title;
  els.meta.textContent = `${campaign.setting} • ${campaign.tone}`;
  els.summary.textContent = campaign.summary || "No summary yet.";
  els.players.innerHTML = "";
  campaign.players.forEach((p) => {
    const li = document.createElement("li");
    li.innerHTML = `<span><strong>${p.character_name}</strong> (${p.character_class} ${p.level})</span><span class="muted">${p.name}</span>`;
    const removeBtn = document.createElement("button");
    removeBtn.textContent = "Remove";
    removeBtn.className = "secondary";
    removeBtn.addEventListener("click", async (event) => {
      event.stopPropagation();
      await removePlayer(p.id);
    });
    li.appendChild(removeBtn);
    els.players.appendChild(li);
  });
}

async function loadLog() {
  if (!state.current) return;
  const log = await request(`${apiBase}/api/campaigns/${state.current.id}/log`);
  els.log.innerHTML = "";
  log.forEach((entry) => {
    const div = document.createElement("div");
    const ts = new Date(entry.timestamp).toLocaleString();
    div.className = "log-entry";
    div.innerHTML = `<div class="meta">${entry.author} • ${ts}</div><div>${entry.text}</div>`;
    els.log.appendChild(div);
  });
  els.log.scrollTop = els.log.scrollHeight;
}

els.campaignForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    const created = await request(`${apiBase}/api/campaigns`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    form.reset();
    await loadCampaigns();
    await selectCampaign(created.id);
  } catch (err) {
    alert(`Could not create campaign: ${err.message}`);
  }
});

els.playerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.current) return alert("Select a campaign first.");
  const form = event.target;
  const payload = Object.fromEntries(new FormData(form).entries());
  payload.level = parseInt(payload.level || "1", 10);
  try {
    const campaign = await request(`${apiBase}/api/campaigns/${state.current.id}/players`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.current = campaign;
    renderCampaign(campaign);
    form.reset();
  } catch (err) {
    alert(`Could not add player: ${err.message}`);
  }
});

els.dmForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.current) return alert("Select a campaign first.");
  const form = event.target;
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    const response = await request(`${apiBase}/api/campaigns/${state.current.id}/dm`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    els.dmReply.textContent = response.reply;
    els.dmGuidance.textContent = response.guidance;
    els.dmResponse.hidden = false;
    form.reset();
    await loadLog();
  } catch (err) {
    alert(`DM could not respond: ${err.message}`);
  }
});

els.diceForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(event.target).entries());
  try {
    const result = await request(`${apiBase}/api/rolls`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    els.diceResult.innerHTML = `<strong>${result.expression}</strong> = [${result.rolls.join(", ")}] ${result.modifier >= 0 ? "+" : ""}${result.modifier} → <strong>${result.total}</strong>`;
    els.diceResult.hidden = false;
  } catch (err) {
    alert(`Dice roll failed: ${err.message}`);
  }
});

els.refresh.addEventListener("click", loadCampaigns);
els.refreshLog.addEventListener("click", loadLog);
els.clearLog.addEventListener("click", async () => {
  if (!state.current) return alert("Select a campaign first.");
  await request(`${apiBase}/api/campaigns/${state.current.id}/log`, { method: "DELETE" });
  await loadLog();
});
els.deleteCampaign.addEventListener("click", async () => {
  if (!state.current) return;
  if (!confirm(`Delete campaign "${state.current.title}"? This cannot be undone.`)) return;
  await request(`${apiBase}/api/campaigns/${state.current.id}`, { method: "DELETE" });
  state.current = null;
  els.details.hidden = true;
  els.deleteCampaign.disabled = true;
  await loadCampaigns();
});
els.downloadLog.addEventListener("click", () => {
  if (!state.current || !els.log.children.length) return alert("No log to download.");
  const text = Array.from(els.log.children)
    .map((node) => node.textContent)
    .join("\n\n");
  const blob = new Blob([text], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${state.current.title.replace(/\\s+/g, \"_\")}_log.txt`;
  anchor.click();
  URL.revokeObjectURL(url);
});

async function removePlayer(playerId) {
  if (!state.current) return alert("Select a campaign first.");
  await request(`${apiBase}/api/campaigns/${state.current.id}/players/${playerId}`, {
    method: "DELETE",
  });
  const updated = await request(`${apiBase}/api/campaigns/${state.current.id}`);
  state.current = updated;
  renderCampaign(updated);
}

loadCampaigns().catch((err) => console.error(err));
