import time
import logging
import os
import threading
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify
from agent.mantle_rpc import MantleRPC
from agent.storage import Storage

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [AGENT] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__)

WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "300"))
MANTLE_RPC_URL = os.getenv("MANTLE_RPC_URL", "https://rpc.mantle.xyz")

rpc = MantleRPC(MANTLE_RPC_URL)
storage = Storage()
app = Flask(__name__)

def run_agent():
    log.info("=" * 50)
    log.info("MantleAgentKit — Starting Agent")
    log.info(f"Wallet : {WALLET_ADDRESS or 'NOT SET'}")
    log.info(f"Network : Mantle Mainnet")
    log.info(f"Interval: {POLL_INTERVAL}s")
    log.info("=" * 50)
    
    if not WALLET_ADDRESS:
        log.error("WALLET_ADDRESS not set — agent cannot start.")
        return
    
    loop_count = 0
    start_time = datetime.utcnow()
    
    while True:
        loop_count += 1
        log.info(f"Loop #{loop_count} — polling Mantle testnet...")
        try:
            balance = rpc.get_balance(WALLET_ADDRESS)
            txs = rpc.get_recent_transactions(WALLET_ADDRESS)
            block = rpc.get_latest_block()
            
            snapshot = {
                "loop": loop_count,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "wallet": WALLET_ADDRESS,
                "balance_mnt": balance,
                "recent_txs": txs,
                "latest_block": block,
                "uptime_seconds": int((datetime.utcnow() - start_time).total_seconds()),
            }
            storage.save_snapshot(snapshot)
            log.info(f"Balance : {balance} MNT")
            log.info(f"Block : {block}")
            log.info(f"TXs : {len(txs)} found")
        except Exception as e:
            log.error(f"Poll failed: {e}")
            storage.save_error(str(e), loop_count)
        
        time.sleep(POLL_INTERVAL)

# ── API ENDPOINTS ──
@app.route('/')
def root():
    return jsonify({
        "name": "MantleAgentKit",
        "version": "0.1.0",
        "mode": "DEMO — Read-Only",
        "network": "Mantle Mainnet",
        "chain_id": 5000,
        "status": "running",
        "built_by": "@SANXARR234",
        "repo": "https://github.com/sanxarrr234/MantleAgentKit"
    })

@app.route('/agent/status')
def agent_status():
    return jsonify(storage.get_status())

@app.route('/agent/latest')
def agent_latest():
    latest = storage.get_latest()
    return jsonify(latest) if latest else jsonify({"error": "No data yet"}), 202

@app.route('/agent/history')
def agent_history():
    return jsonify({"history": storage.get_history()})

@app.route('/wallet/<address>')
def wallet_query(address):
    try:
        balance = rpc.get_balance(address)
        txs = rpc.get_recent_transactions(address)
        return jsonify({
            "address": address,
            "balance_mnt": balance,
            "chain_id": 5000,
            "explorer": f"https://explorer.mantle.xyz/address/{address}",
            "recent_txs": txs
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Start polling agent in background thread
    agent_thread = threading.Thread(target=run_agent, daemon=True)
    agent_thread.start()
    
    # Start Flask server on port 8080
    app.run(host='0.0.0.0', port=8080, debug=False)
