import json
import os
import time
from datetime import datetime
from schwab_api import place_option_order, place_equity_order, get_quote
from reporter import update_memory

MEMORY_PATH = "memory.json"


def load_memory():
    with open(MEMORY_PATH, "r") as f:
        return json.load(f)


def save_memory(data):
    with open(MEMORY_PATH, "w") as f:
        json.dump(data, f, indent=2)


def evaluate_trade(signal, memory):
    ticker = signal["ticker"]
    trade_type = signal["type"]
    direction = signal["direction"]
    confidence = signal["confidence"]

    blacklist = memory.get("blacklist_commands", [])
    if ticker in blacklist:
        return None, f"{ticker} is blacklisted. Skipping."

    risk = memory["risk_profile"]

    if trade_type == "option":
        price = float(signal["price"])
        contracts = max(1, int(risk["max_loss_per_trade"] / (price * 100)))
        target_pct = risk["option_target_pct"]
        stop_pct = risk["option_stop_pct"]
        return {
            "type": "option",
            "ticker": ticker,
            "action": direction,
            "contracts": contracts,
            "price": price,
            "target_pct": target_pct,
            "stop_pct": stop_pct,
            "confidence": confidence
        }, None

    elif trade_type == "equity":
        quote = get_quote(ticker)
        price = float(quote["last"])
        shares = max(1, int(risk["max_loss_per_trade"] / price))
        target_pct = risk["equity_target_pct"]
        stop_pct = risk["equity_stop_pct"]
        return {
            "type": "equity",
            "ticker": ticker,
            "action": direction,
            "shares": shares,
            "price": price,
            "target_pct": target_pct,
            "stop_pct": stop_pct,
            "confidence": confidence
        }, None

    return None, "Unsupported trade type."


def execute_trade(plan, memory):
    if plan["type"] == "option":
        result = place_option_order(
            plan["ticker"],
            plan["action"],
            plan["contracts"],
            plan["price"],
            plan["target_pct"],
            plan["stop_pct"]
        )
    else:
        result = place_equity_order(
            plan["ticker"],
            plan["action"],
            plan["shares"],
            plan["price"],
            plan["target_pct"],
            plan["stop_pct"]
        )

    memory["last_trade"] = {
        "ticker": plan["ticker"],
        "type": plan["type"],
        "action": plan["action"],
        "timestamp": int(time.time())
    }
    save_memory(memory)
    update_memory(plan, result)
    return result


def agent_main(signals):
    memory = load_memory()
    for signal in signals:
        plan, error = evaluate_trade(signal, memory)
        if error:
            print(f"❌ {error}")
            continue

        print(f"✅ Proposed Trade: {plan}")
        confirm = input("Type 'GO' to execute this trade: ").strip().upper()
        if confirm == "GO":
            result = execute_trade(plan, memory)
            print(f"🟢 Executed: {result}")
        else:
            print("⏭️ Skipped by user.")
