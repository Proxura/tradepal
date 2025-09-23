# reporter.py
import json
import datetime

MEMORY_FILE = 'memory.json'

def load_memory():
    with open(MEMORY_FILE, 'r') as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=4)

def log_trade_result(ticker, result, profit_loss, strategy):
    memory = load_memory()
    timestamp = datetime.datetime.now().isoformat()

    trade_log = {
        "timestamp": timestamp,
        "ticker": ticker,
        "result": result,  # 'win' or 'loss'
        "profit_loss": profit_loss,
        "strategy": strategy
    }

    # Update trade history
    memory.setdefault("trade_history", []).append(trade_log)
    memory["last_trade"] = trade_log

    # Update daily earnings
    today = timestamp.split("T")[0]
    memory.setdefault("daily_earnings", {})
    memory["daily_earnings"].setdefault(today, 0)
    memory["daily_earnings"][today] += profit_loss

    # Auto-learn strategy notes
    memory.setdefault("strategy_notes", {})
    memory["strategy_notes"].setdefault(strategy, {"wins": 0, "losses": 0})
    if result == "win":
        memory["strategy_notes"][strategy]["wins"] += 1
    else:
        memory["strategy_notes"][strategy]["losses"] += 1

    save_memory(memory)
    print(f"[LOGGED] {ticker} - {result.upper()} - ${profit_loss} via {strategy}")

# Example usage:
# log_trade_result("TSLA", "win", 112.50, "cash_secured_put")
