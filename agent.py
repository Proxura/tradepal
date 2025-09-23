import json
import os
import time
from datetime import datetime
from schwab_api import place_option_order, place_equity_order, get_quote, get_cash_balance, get_holdings, trim_position
from reporter import update_memory

MEMORY_PATH = "memory.json"


def load_memory():
    with open(MEMORY_PATH, "r") as f:
        return json.load(f)


def save_memory(data):
    with open(MEMORY_PATH, "w") as f:
        json.dump(data, f, indent=2)


def estimate_cost(trade_type, price, quantity):
    if trade_type == "option":
        return price * 100 * quantity  # 100 shares per contract
    else:
        return price * quantity


def find_trim_candidates(memory, needed_cash):
    holdings = get_holdings()
    min_pct = memory.get("minimum_trim_profit_pct", 5)
    candidates = []

    for holding in holdings:
        gain_pct = holding.get("gain_pct", 0)
        if gain_pct >= min_pct:
            est_value = holding["qty"] * holding["price"]
            candidates.append({
                "ticker": holding["ticker"],
                "qty": holding["qty"],
                "gain_pct": gain_pct,
                "est_value": est_value
            })

    candidates.sort(key=lambda x: x["gain_pct"], reverse=True)
    trimmed = []
    total_freed = 0

    for c in candidates:
        if total_freed >= needed_cash:
            break
        trim_qty = min(c["qty"], int((needed_cash - total_freed) / c["est_value"] * c["qty"]))
        if trim_qty > 0:
            trim_position(c["ticker"], trim_qty)
            trimmed.append({"ticker": c["ticker"], "qty": trim_qty})
            total_freed += c["est_value"] * trim_qty / c["qty"]

    return trimmed


def evaluate_trade(signal, memory):
    ticker = signal["ticker"]
    trade_type = signal["type"]
    direction = signal["direction"]
    confidence = signal["confidence"]
    source = signal.get("source", "manual")
    
    blacklist = memory.get("blacklist_commands", [])
    if ticker in blacklist:
        return None, f"{ticker} is blacklisted. Skipping."

    risk = memory["risk_profile"]
    cash = get_cash_balance()

    if trade_type == "option":
        price = float(signal["price"])
        max_contracts = int(cash / (price * 100))
        contracts = max(1, min(max_contracts, int(risk["max_loss_per_trade"] / (price * 100))))
        cost = estimate_cost("option", price, contracts)
        if cost > cash and memory.get("auto_trim_enabled", False):
            trimmed = find_trim_candidates(memory, cost - cash)
            cash = get_cash_balance()
            if cost > cash:
                return None, f"Not enough cash even after trimming. Needed ${cost}, have ${cash}."
        return {
            "type": "option",
            "ticker": ticker,
            "action": direction,
            "contracts": contracts,
            "price": price,
            "target_pct": risk["option_target_pct"],
            "stop_pct": risk["option_stop_pct"],
            "confidence": confidence,
            "source": source
        }, None

    elif trade_type == "equity":
        quote = get_quote(ticker)
        price = float(quote["last"])
        max_shares = int(cash / price)
        shares = max(1, min(max_shares, int(risk["max_loss_per_trade"] / price)))
        cost = estimate_cost("equity", price, shares)
        if cost > cash and memory.get("auto_trim_enabled", False):
            trimmed = find_trim_candidates(memory, cost - cash)
            cash = get_cash_balance()
            if cost > cash:
                return None, f"Not enough cash even after trimming. Needed ${cost}, have ${cash}."
        return {
            "type": "equity",
            "ticker": ticker,
            "action": direction,
            "shares": shares,
            "price": price,
            "target_pct": risk["equity_target_pct"],
            "stop_pct": risk["equity_stop_pct"],
            "confidence": confidence,
            "source": source
        }, None

    return None, "Unsupported trade type."


def execute_trade(plan, memory):
    if plan["type"] == "option":
        result = place_option_order(
            plan["ticker"], plan["action"], plan["contracts"], plan["price"], plan["target_pct"], plan["stop_pct"]
        )
    else:
        result = place_equity_order(
            plan["ticker"], plan["action"], plan["shares"], plan["price"], plan["target_pct"], plan["stop_pct"]
        )

    memory["last_trade"] = {
        "ticker": plan["ticker"],
        "type": plan["type"],
        "action": plan["action"],
        "timestamp": int(time.time()),
        "confidence": plan["confidence"],
        "source": plan["source"]
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
