import requests
import logging

log = logging.getLogger(__name__)

MANTLE_EXPLORER_API = "api.mantlescan.xyz"


class MantleRPC:
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _call(self, method: str, params: list) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        }
        res = self.session.post(self.rpc_url, json=payload, timeout=10)
        res.raise_for_status()
        data = res.json()
        if "error" in data:
            raise Exception(f"RPC error: {data['error']}")
        return data.get("result")

    def get_balance(self, address: str) -> str:
        try:
            hex_balance = self._call("eth_getBalance", [address, "latest"])
            wei = int(hex_balance, 16)
            mnt = wei / 10**18
            return f"{mnt:.6f}"
        except Exception as e:
            log.error(f"get_balance failed: {e}")
            return "0.000000"

    def get_latest_block(self) -> int:
        try:
            hex_block = self._call("eth_blockNumber", [])
            return int(hex_block, 16)
        except Exception as e:
            log.error(f"get_latest_block failed: {e}")
            return 0

    def get_recent_transactions(self, address: str, limit: int = 5) -> list:
        try:
            params = {
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "page": 1,
                "offset": limit,
                "sort": "desc",
            }
            res = self.session.get(
                MANTLE_EXPLORER_API,
                params=params,
                timeout=10
            )
            res.raise_for_status()
            data = res.json()

            if data.get("status") != "1":
                return []

            txs = []
            for tx in data.get("result", [])[:limit]:
                txs.append({
                    "hash": tx.get("hash", ""),
                    "from": tx.get("from", ""),
                    "to": tx.get("to", ""),
                    "value_mnt": str(int(tx.get("value", "0")) / 10**18),
                    "timestamp": tx.get("timeStamp", ""),
                    "status": "success" if tx.get("isError") == "0" else "failed",
                })
            return txs

        except Exception as e:
            log.error(f"get_recent_transactions failed: {e}")
            return []

    def get_chain_id(self) -> int:
        try:
            hex_id = self._call("eth_chainId", [])
            return int(hex_id, 16)
        except Exception as e:
            log.error(f"get_chain_id failed: {e}")
            return 0
