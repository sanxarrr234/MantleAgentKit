# MantleAgentKit

**1 Human. 3 AIs. Zero VC. Built on Mantle.**

A read-only autonomous AI agent that monitors a Mantle mainnet wallet in real-time — built for the Mantle Squad Bounty by [@SANXARR234](https://twitter.com/SANXARR234).

---

## Live Demo

| Resource | URL |
|---|---|
| Dashboard | https://mantle-agent-kit.vercel.app |
| API | https://web-production-d94fcd.up.railway.app |

---

## What It Does

- Polls Mantle mainnet every 5 minutes autonomously
- Reads wallet balance + recent transactions via RPC
- Exposes live data through a REST API
- Displays everything on a real-time dashboard

**Read-only. No private keys. No transactions.**

---

## Stack

| Layer | Tech |
|---|---|
| Agent | Python + FastAPI |
| Chain | Mantle Mainnet (Chain ID: 5000) |
| RPC | https://rpc.mantle.xyz |
| Explorer | https://explorer.mantle.xyz |
| Backend deploy | Railway |
| Frontend deploy | Vercel |

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Health check |
| `GET /agent/status` | Uptime, loop count, last poll |
| `GET /agent/latest` | Latest wallet snapshot |
| `GET /agent/history` | Last 100 poll history |
| `GET /wallet/{address}` | Query any Mantle mainnet address |

---

## Run Locally

```bash
# Clone
git clone https://github.com/sanxarrr234/MantleAgentKit
cd MantleAgentKit

# Install deps
pip install -r requirements.txt

# Set env vars
cp agent/.env.example .env
# Edit .env: set WALLET_ADDRESS

# Run
uvicorn agent.api:app --host 0.0.0.0 --port 8000
```

### Run on Termux (Android)

```bash
pkg install python
pip install -r requirements.txt
uvicorn agent.api:app --host 0.0.0.0 --port 8000
```

---

## Environment Variables

| Variable | Value |
|---|---|
| `WALLET_ADDRESS` | Your Mantle mainnet wallet address |
| `MANTLE_RPC_URL` | `https://rpc.mantle.xyz` |
| `POLL_INTERVAL` | `300` (seconds) |

---

## Project Structure

```
MantleAgentKit/
├── agent/
│   ├── api.py          # FastAPI endpoints
│   ├── main.py         # Agent loop
│   ├── mantle_rpc.py   # Mantle RPC + Explorer
│   ├── storage.py      # In-memory data store
│   └── .env.example
├── dashboard/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── Procfile
├── railway.json
└── README.md
```

---

*Built by [@SANXARR234](https://twitter.com/SANXARR234) — Mantle Squad Bounty 2026*
