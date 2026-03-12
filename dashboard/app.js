// MantleAgentKit Dashboard
// Fetches live data from Railway backend

const API_BASE = "https://mantleagentkit-production.up.railway.app";
const REFRESH_INTERVAL = 30000; // 30 seconds

// ── UTILS ──

function formatUptime(seconds) {
  if (!seconds) return "—";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

function formatTime(isoStr) {
  if (!isoStr) return "—";
  try {
    const d = new Date(isoStr);
    const diff = Math.floor((Date.now() - d.getTime()) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return `${Math.floor(diff / 3600)}h ago`;
  } catch {
    return isoStr;
  }
}

function shortenHash(hash) {
  if (!hash || hash.length < 12) return hash;
  return hash.slice(0, 8) + "..." + hash.slice(-6);
}

function setNetStatus(online) {
  const dot = document.getElementById("netDot");
  const label = document.getElementById("netLabel");
  if (online) {
    dot.className = "net-dot online";
    label.textContent = "Mantle Testnet";
  } else {
    dot.className = "net-dot offline";
    label.textContent = "Disconnected";
  }
}

// ── FETCH AGENT STATUS ──

async function fetchAgentStatus() {
  try {
    const res = await fetch(`${API_BASE}/agent/status`, { signal: AbortSignal.timeout(8000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    document.getElementById("agentStatus").textContent = "RUNNING";
    document.getElementById("agentStatus").style.color = "var(--green)";
    document.getElementById("agentUptime").textContent = formatUptime(data.uptime_seconds);
    document.getElementById("loopCount").textContent = data.loop_count || "0";
    document.getElementById("lastPoll").textContent = formatTime(data.last_poll);

    setNetStatus(true);
    return true;
  } catch (e) {
    document.getElementById("agentStatus").textContent = "OFFLINE";
    document.getElementById("agentStatus").style.color = "var(--red)";
    setNetStatus(false);
    return false;
  }
}

// ── FETCH LATEST SNAPSHOT ──

async function fetchLatest() {
  try {
    const res = await fetch(`${API_BASE}/agent/latest`, { signal: AbortSignal.timeout(8000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    document.getElementById("latestBlock").textContent = data.latest_block?.toLocaleString() || "—";

    // Monitor wallet display
    const monitorEl = document.getElementById("monitorData");
    monitorEl.innerHTML = `
      <div class="monitor-grid">
        <div class="mg-item">
          <div class="mg-label">Wallet Address</div>
          <div class="mg-val" style="font-size:11px">${data.wallet || "—"}</div>
        </div>
        <div class="mg-item">
          <div class="mg-label">Balance</div>
          <div class="mg-val big">${data.balance_mnt || "0"} <span style="font-size:14px;color:var(--muted2)">MNT</span></div>
        </div>
        <div class="mg-item">
          <div class="mg-label">Last Checked</div>
          <div class="mg-val">${formatTime(data.timestamp)}</div>
        </div>
        <div class="mg-item">
          <div class="mg-label">Network</div>
          <div class="mg-val" style="color:var(--green)">Mantle Testnet</div>
        </div>
      </div>
    `;

    // TX list
    renderTxList(data.recent_txs || []);

  } catch (e) {
    document.getElementById("monitorData").innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">⏳</div>
        Agent initializing — first data will appear after first poll (up to 5 min)
      </div>
    `;
  }
}

// ── RENDER TX LIST ──

function renderTxList(txs) {
  const el = document.getElementById("txList");

  if (!txs || txs.length === 0) {
    el.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📭</div>
        No recent transactions found for this wallet
      </div>
    `;
    return;
  }

  el.innerHTML = txs.map(tx => `
    <div class="tx-item">
      <div class="tx-status ${tx.status}"></div>
      <div class="tx-info">
        <a class="tx-hash"
           href="https://explorer.sepolia.mantle.xyz/tx/${tx.hash}"
           target="_blank"
           rel="noopener">
          ${shortenHash(tx.hash)}
        </a>
        <div class="tx-meta">
          ${tx.from ? shortenHash(tx.from) : "?"} → ${tx.to ? shortenHash(tx.to) : "?"}
          · ${formatTime(tx.timestamp ? new Date(parseInt(tx.timestamp) * 1000).toISOString() : null)}
        </div>
      </div>
      <div class="tx-value">${parseFloat(tx.value_mnt || 0).toFixed(4)} MNT</div>
    </div>
  `).join("");
}

// ── FETCH HISTORY ──

async function fetchHistory() {
  try {
    const res = await fetch(`${API_BASE}/agent/history`, { signal: AbortSignal.timeout(8000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const el = document.getElementById("historyList");
    const history = (data.history || []).slice(-10).reverse();

    if (history.length === 0) {
      el.innerHTML = `<div class="empty-state"><div class="empty-icon">📋</div>No history yet</div>`;
      return;
    }

    el.innerHTML = history.map(h => `
      <div class="history-item">
        <div class="hi-loop">#${h.loop}</div>
        <div class="hi-balance">${h.balance_mnt} MNT</div>
        <div class="hi-block">Block ${h.latest_block?.toLocaleString()}</div>
        <div class="hi-time">${formatTime(h.timestamp)}</div>
      </div>
    `).join("");

  } catch (e) {
    document.getElementById("historyList").innerHTML = `
      <div class="empty-state">No history available yet</div>
    `;
  }
}

// ── QUERY WALLET ──

async function queryWallet() {
  const input = document.getElementById("walletInput").value.trim();
  const resultEl = document.getElementById("walletResult");
  const btn = document.getElementById("queryBtn");
  const btnText = document.getElementById("queryBtnText");

  if (!input.startsWith("0x") || input.length !== 42) {
    resultEl.className = "wallet-result";
    resultEl.innerHTML = `<div class="error-state">Invalid address — must be a valid 0x... Mantle address (42 chars)</div>`;
    return;
  }

  btn.disabled = true;
  btnText.textContent = "Querying...";
  resultEl.className = "wallet-result";
  resultEl.innerHTML = `<div class="loading-line"></div><div class="loading-line short"></div>`;

  try {
    const res = await fetch(`${API_BASE}/wallet/${input}`, { signal: AbortSignal.timeout(10000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    resultEl.innerHTML = `
      <div class="wr-address">${data.address}</div>
      <div class="wr-balance">${parseFloat(data.balance_mnt).toFixed(6)}</div>
      <div class="wr-network">MNT · Mantle Testnet · Chain ID ${data.chain_id}</div>
      <a class="wr-explorer" href="${data.explorer}" target="_blank" rel="noopener">
        View on Mantle Explorer ↗
      </a>
      ${data.recent_txs?.length > 0 ? `
        <div style="margin-top:16px">
          ${data.recent_txs.map(tx => `
            <div class="tx-item">
              <div class="tx-status ${tx.status}"></div>
              <div class="tx-info">
                <a class="tx-hash" href="https://explorer.sepolia.mantle.xyz/tx/${tx.hash}" target="_blank">${shortenHash(tx.hash)}</a>
                <div class="tx-meta">${shortenHash(tx.from)} → ${shortenHash(tx.to)}</div>
              </div>
              <div class="tx-value">${parseFloat(tx.value_mnt || 0).toFixed(4)} MNT</div>
            </div>
          `).join("")}
        </div>
      ` : `<div style="margin-top:12px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--muted)">No recent transactions found</div>`}
    `;

  } catch (e) {
    resultEl.innerHTML = `<div class="error-state">Failed to query wallet: ${e.message}</div>`;
  } finally {
    btn.disabled = false;
    btnText.textContent = "Query Agent";
  }
}

// Allow Enter key on input
document.getElementById("walletInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter") queryWallet();
});

// ── INIT & REFRESH LOOP ──

async function refresh() {
  await fetchAgentStatus();
  await fetchLatest();
  await fetchHistory();
}

refresh();
setInterval(refresh, REFRESH_INTERVAL);
