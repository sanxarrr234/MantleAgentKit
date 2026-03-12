import time
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
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
MANTLE_RPC_URL = os.getenv("MANTLE_RPC_URL", "https://rpc.sepolia.mantle.xyz")

rpc = MantleRPC(MANTLE_RPC_URL)


def run_agent(storage: Storage = None):
  
    if storage is None:
        storage = Storage()

    log.info("=" * 50)
    log.info("MantleAgentKit — Starting Agent")
    log.info(f"Wallet  : {WALLET_ADDRESS or 'NOT SET'}")
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
            log.info(f"Block   : {block}")
            log.info(f"TXs     : {len(txs)} found")

        except Exception as e:
            log.error(f"Poll failed: {e}")
            storage.save_error(str(e), loop_count)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run_agent()
