# memory.py

import json

MEMORY_FILE = "memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "daily_earnings": [],
            "last_trade": None,
            "strategy_notes": "",
            "blacklist_commands": [],
            "risk_profile": {
                "max_loss_per_trade": 100,
                "min_profit_target": 50
            },
            "trade_history": [],
            "positions": {},
            "trade_log": []  # ✅ ADD THIS
        }

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

memory = load_memory()

def set_last_signal(signal):
    memory["last_trade"] = signal
    save_memory(memory)

def get_last_signal():
    return memory.get("last_trade", None)

def log_trade(action, symbol, qty, reason=""):
    memory["trade_history"].append({
        "action": action,
        "symbol": symbol,
        "qty": qty,
        "reason": reason
    })
    save_memory(memory)
