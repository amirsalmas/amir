import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# ── ولت‌ها ──
# روی Railway، این‌ها رو تو Variables ست کن تا Redeploy پاکشون نکنه
DEFAULT_WALLET_BTC = os.getenv(
    "WALLET_BTC",
    "bc1q3pgr40jxs4ufg4hu9008m20ac5ar6rv96ejmu9"
)
DEFAULT_WALLET_XMR = os.getenv("WALLET_XMR", "")

DEFAULT_COIN = os.getenv("DEFAULT_COIN", "BTC")
CPU_PERCENT = int(os.getenv("CPU_PERCENT", "30"))

# ── مسیر XMRig ──
_default_xmrig = "xmrig.exe" if sys.platform == "win32" else "xmrig"
XMRIG_PATH = os.getenv("XMRIG_PATH", str(BASE_DIR / _default_xmrig))

WALLETS_FILE = DATA_DIR / "wallets.json"
MINING_STATE = DATA_DIR / "mining_state.json"


def get_default_wallet(coin: str) -> str:
    return {
        "BTC": DEFAULT_WALLET_BTC,
        "XMR": DEFAULT_WALLET_XMR,
    }.get(coin.upper(), "")
