import json
import os

import psutil
from flask import Flask, render_template, request, jsonify

from config import DEFAULT_COIN, CPU_PERCENT, WALLETS_FILE, get_default_wallet
from miner import XMRigManager, list_coins, get_coin

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", os.urandom(32).hex())
manager = XMRigManager()


def load_wallets():
    if WALLETS_FILE.exists():
        try:
            return json.loads(WALLETS_FILE.read_text())
        except Exception:
            pass
    return {}


def save_wallets(w):
    try:
        WALLETS_FILE.write_text(json.dumps(w, indent=2))
    except Exception:
        pass


def merged_wallets():
    w = load_wallets()
    for c in ("BTC", "XMR"):
        if not w.get(c):
            d = get_default_wallet(c)
            if d:
                w[c] = d
    return w


@app.route("/")
def index():
    return render_template(
        "index.html",
        coins=list_coins(),
        wallets=merged_wallets(),
        status=manager.status(),
        default_coin=DEFAULT_COIN,
        default_cpu=CPU_PERCENT,
    )


@app.route("/api/status")
def api_status():
    st = manager.status()
    st["stats"] = manager.stats()
    st["cpu_percent"] = manager.cpu_usage()
    try:
        st["mem_percent"] = psutil.virtual_memory().percent
    except Exception:
        st["mem_percent"] = 0
    st["cpu_count"] = os.cpu_count() or 1
    return jsonify(st)


@app.route("/api/wallets", methods=["GET", "POST"])
def api_wallets():
    if request.method == "GET":
        return jsonify(merged_wallets())
    data = request.get_json(force=True, silent=True) or {}
    coin = (data.get("coin") or "").upper()
    addr = (data.get("address") or "").strip()
    if not get_coin(coin):
        return jsonify({"ok": False, "error": "ارز نامعتبر"}), 400
    if len(addr) < 20:
        return jsonify({"ok": False, "error": "آدرس خیلی کوتاه است"}), 400
    w = load_wallets()
    w[coin] = addr
    save_wallets(w)
    return jsonify({"ok": True})


@app.route("/api/mining/start", methods=["POST"])
def api_start():
    data = request.get_json(force=True, silent=True) or {}
    coin = (data.get("coin") or "").upper()
    pool = data.get("pool") or ""
    wallet = (data.get("wallet") or "").strip()
    cpu_hint = data.get("cpu_hint")

    if not wallet:
        wallet = merged_wallets().get(coin, "")
    if not wallet:
        return jsonify({"ok": False, "error": "ولت تنظیم نشده"}), 400

    c = get_coin(coin)
    if not c:
        return jsonify({"ok": False, "error": "ارز نامعتبر"}), 400
    if pool not in [p["url"] for p in c["pools"]]:
        return jsonify({"ok": False, "error": "استخر نامعتبر"}), 400

    try:
        cpu_hint = int(cpu_hint) if cpu_hint else None
    except Exception:
        cpu_hint = None

    ok, msg = manager.start(coin, wallet, pool, cpu_hint)
    return jsonify({"ok": ok, "message": msg})


@app.route("/api/mining/stop", methods=["POST"])
def api_stop():
    ok, msg = manager.stop()
    return jsonify({"ok": ok, "message": msg})


@app.route("/healthz")
def healthz():
    return "ok"


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"\n⛏️  Keeper Miner — http://0.0.0.0:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
