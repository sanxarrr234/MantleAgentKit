import os
import threading
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from agent.storage import Storage
from agent.mantle_rpc import MantleRPC
import agent.main as agent_main

load_dotenv()

app = FastAPI(
    title="MantleAgentKit API",
    description="Read-only AI agent monitoring Mantle testnet",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


shared_storage = Storage()
rpc = MantleRPC(os.getenv("MANTLE_RPC_URL", "https://rpc.sepolia.mantle.xyz"))


@app.get("/")
def root():
    return {
        "name": "MantleAgentKit",
        "version": "0.1.0",
        "mode": "DEMO — Read-Only",
        "network": "Mantle Testnet",
        "chain_id": 5003,
        "status": "running",
        "built_by": "@SANXARR234",
        "repo": "https://github.com/sanxarrr234/MantleAgentKit",
    }


@app.get("/agent/status")
def agent_status():
    return shared_storage.get_status()


@app.get("/agent/latest")
def agent_latest():
    latest = shared_storage.get_latest()
    if not latest:
        
        return {
            "wallet": os.getenv("WALLET_ADDRESS", ""),
            "balance_mnt": "0.000000",
            "recent_txs": [],
            "latest_block": 0,
            "timestamp": None,
            "loop": 0,
            "uptime_seconds": 0,
        }
    return latest


@app.get("/agent/history")
def agent_history():
    return {
        "count": len(shared_storage.get_history()),
        "history": shared_storage.get_history()
    }


@app.get("/wallet/{address}")
def wallet_info(address: str):
    if not address.startswith("0x") or len(address) != 42:
        raise HTTPException(status_code=400, detail="Invalid Mantle wallet address")

    balance = rpc.get_balance(address)
    txs = rpc.get_recent_transactions(address)
    block = rpc.get_latest_block()

    return {
        "address": address,
        "balance_mnt": balance,
        "recent_txs": txs,
        "latest_block": block,
        "network": "Mantle Testnet",
        "chain_id": 5003,
        "explorer": f"https://explorer.sepolia.mantle.xyz/address/{address}",
    }


def start_agent_thread():
    
    t = threading.Thread(
        target=agent_main.run_agent,
        args=(shared_storage,),
        daemon=True
    )
    t.start()


@app.on_event("startup")
def startup():
    start_agent_thread()
