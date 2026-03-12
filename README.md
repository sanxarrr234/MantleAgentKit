# MantleAgentKit

> 1 Human. 3 AIs. Zero VC. Built on Mantle.

A low-code launchpad for deploying autonomous AI agents on the Mantle chain. Input a wallet address, define a goal, and let the agent run 24/7 — no terminal, no smart contract knowledge required.

**Live Demo:** [mantle-agent-kit.vercel.app](https://mantle-agent-kit.vercel.app)  
**Built by:** [@SANXARR234](https://x.com/SANXARR234)  
**Network:** Mantle Testnet (Chain ID: 5003)  
**Status:** `DEMO — Read-Only Mode`

---

## What It Does

MantleAgentKit runs a persistent agent on the Mantle testnet that:

- Monitors any wallet address in realtime
- Reads balance and recent transaction history
- Displays live data via a web dashboard
- Runs autonomously 24/7 on Railway cloud

No private key required. No transaction signing. Pure read-only — safe by design for this demo phase.

---

## How It Works

```
User inputs wallet address on dashboard
        ↓
Dashboard (Vercel) fetches data from backend API
        ↓
Backend (Railway) polls Mantle Testnet RPC every 5 minutes
        ↓
Mantle Testnet returns balance + transaction data
        ↓
Dashboard displays live: balance, tx history, agent uptime
```

### AI Stack

| AI | Role |
|---|---|
| **Claude** | Compiled agent logic from natural language intent |
| **Gemini** | Research & verification of Mantle specs, RPC, and ecosystem |
| **Kilo.ai** | Blueprint for cloud agent deployment pattern |

---

## Stack

| Layer | Tech |
|---|---|
| Frontend | HTML + Vanilla JS |
| Backend | Python + FastAPI |
| Cloud | Railway (agent) + Vercel (dashboard) |
| Chain | Mantle Testnet (Chain ID: 5003) |
| RPC | https://rpc.sepolia.mantle.xyz |

---

## Project Structure

```
MantleAgentKit/
├── agent/
│   ├── __init__.py             # Package marker
│   ├── main.py                 # Agent loop — runs every 5 min
│   ├── mantle_rpc.py           # Mantle testnet RPC queries
│   ├── api.py                  # FastAPI REST endpoints
│   ├── storage.py              # In-memory + JSON data store
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment variable template
├── dashboard/
│   ├── index.html              # Main dashboard UI
│   ├── style.css               # Styling
│   └── app.js                  # Polling logic + UI updates
├── Procfile                    # Railway process definition
├── railway.json                # Railway config
├── requirements.txt            # Root-level requirements (Railway)
├── .gitignore                  # Excludes .env and credentials
└── README.md                   # This file
```

---

## Quick Start — Run Locally

### Prerequisites
- Python 3.10+
- Git

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/sanxarrr234/MantleAgentKit
cd MantleAgentKit

# 2. Install dependencies (run from root, not from agent/)
pip install -r requirements.txt

# 3. Configure environment
cp agent/.env.example agent/.env
# Edit agent/.env — add your Mantle testnet wallet address
```

Edit `agent/.env`:
```env
WALLET_ADDRESS=0xYourWalletAddressHere
MANTLE_RPC_URL=https://rpc.sepolia.mantle.xyz
POLL_INTERVAL=300
PORT=8000
```

```bash
# 4. Run the API server (from root directory)
uvicorn agent.api:app --host 0.0.0.0 --port 8000

# 5. Open dashboard
# Edit dashboard/app.js line 1:
# const API_BASE = "http://localhost:8000"
# Then open dashboard/index.html in browser
# Or serve locally:
cd dashboard && python -m http.server 8080
```

> **Important:** Always run commands from the **root** of the repo, not from inside `agent/`. The package imports depend on this.

### Termux (Android)

```bash
pkg install python git
git clone https://github.com/sanxarrr234/MantleAgentKit
cd MantleAgentKit
pip install -r requirements.txt
cp agent/.env.example agent/.env
# Edit agent/.env with your wallet address
uvicorn agent.api:app --host 0.0.0.0 --port 8000
```

---

## Deploy to Railway

1. Fork this repo
2. Create account at [railway.app](https://railway.app)
3. New Project → Deploy from GitHub → select this repo
4. Add environment variables in Railway dashboard → Variables:

| Variable | Value |
|---|---|
| `WALLET_ADDRESS` | Your Mantle testnet wallet address |
| `MANTLE_RPC_URL` | `https://rpc.sepolia.mantle.xyz` |
| `POLL_INTERVAL` | `300` |
| `PORT` | `8000` |

5. Railway auto-detects `Procfile` and deploys

Agent will be live and polling Mantle testnet within 2 minutes.

> **Note:** Railway uses the root `Procfile` which runs: `uvicorn agent.api:app --host 0.0.0.0 --port $PORT`

---

## API Endpoints

Once deployed, the backend exposes:

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check + agent info |
| `/agent/status` | GET | Agent uptime, loop count, last poll time |
| `/agent/latest` | GET | Latest wallet snapshot |
| `/agent/history` | GET | Full poll history (last 100 entries) |
| `/wallet/{address}` | GET | Balance + recent txs for any Mantle testnet address |

### Example Response

```json
// GET /wallet/0x1234...
{
  "address": "0x1234...",
  "balance_mnt": "112.000000",
  "recent_txs": [],
  "latest_block": 18500000,
  "network": "Mantle Testnet",
  "chain_id": 5003,
  "explorer": "https://explorer.sepolia.mantle.xyz/address/0x1234..."
}
```

---

## Roadmap

### Phase 1 — Concept & Blueprint ✅
*March 2026*
- Architecture designed from real Kilo.ai deployment experience
- Read-only demo agent live on Mantle testnet
- Dashboard live at mantle-agent-kit.vercel.app
- Public API serving live chain data

### Phase 2 — MVP *(Q2 2026 — if resourced)*
- Write capability: agent can execute simple on-chain actions
- User-defined agent goals via natural language input
- Claude API integration for real-time logic compilation
- Mantle testnet → mainnet migration
- Estimated cost: $60–110/month

### Phase 3 — Public Beta *(Q3–Q4 2026 — if funded)*
- Multi-agent support
- DeFi automation templates (Lendle, Merchant Moe)
- Agent marketplace
- Requires: Mantle ecosystem grant or external funding

---

## Honest Disclosure

This project is built by **1 developer + 3 AI models**. No team. No VC. No funding.

Current status: **Phase 1 complete.** The demo agent is real — it connects to Mantle testnet, reads live data, and serves it via API to the dashboard. Balance and transaction queries are fully functional and verifiable on-chain.

Write capability and production deployment depend on available resources. Win or lose the Mantle Squad Bounty — this gets built when the funds arrive.

---

## Contributing

PRs welcome. Especially:
- Bug fixes in `mantle_rpc.py`
- Additional API endpoints
- Dashboard UI improvements
- Documentation improvements

Please do **not** submit PRs that introduce private key handling or transaction signing without a full security review discussion first.

---

## Security

- **No private keys** are stored or required in this demo
- **No transaction signing** in current phase
- **Public RPC only** — read-only Mantle testnet queries
- All credentials via environment variables, never hardcoded
- `.env` is gitignored — never committed to repo

Found a security issue? DM [@SANXARR234](https://x.com/SANXARR234) before opening a public issue.

---

## License

MIT — fork it, build on it, ship it.

---

*Built for the Mantle "When AI Meets Mantle" Squad Bounty Program — March 2026*  
*[@SANXARR234](https://x.com/SANXARR234) · [mantle-agent-kit.vercel.app](https://mantle-agent-kit.vercel.app)*
