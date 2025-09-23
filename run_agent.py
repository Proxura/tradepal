import argparse
import time
import json
import os

# Comment this in for live runs later:
# from auth import refresh_tokens_if_needed
# from schwab_api import get_option_quote, place_order, get_account_balance
from schwab_api import get_option_quote, place_order, get_account_balance_mock

MEMORY_PATH = "memory.json"
LIVE_MODE = False  # Flip to True for real Schwab API

def load_memory():
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r") as f:
            return json.load(f)
    else:
        return {}

def save_memory(memory):
    with open(MEMORY_PATH, "w") as f:
        json.dump(memory, f, indent=2)

def log_trade(memory, trade):
    memory["last_trade"] = trade
    memory.setdefault("trade_history", []).append(trade)
    memory["daily_earnings"] = memory.get("daily_earnings", 0) + trade.get("gain", 0)
    save_memory(memory)

def monitor_and_trim(ticker, entry_price, stop_loss, target_price):
    print(f"[🟢] Monitoring {ticker}...")
    while True:
        current_price = get_option_quote(ticker)
        print(f"\t[Live] {ticker}: ${current_price:.2f}")

        if current_price >= target_price:
            print("[✓] Target hit. Selling...")
            place_order(ticker, action="SELL")
            return "limit_sale_triggered", current_price

        if current_price <= stop_loss:
            print("[X] Stop loss hit. Exiting position...")
            place_order(ticker, action="SELL")
            return "stop_loss_exit", current_price

        time.sleep(60)

def estimate_probability(entry, target, stop):
    rr = (target - entry) / (entry - stop)
    if rr >= 2.5: return 0.75
    if rr >= 2: return 0.68
    if rr >= 1.5: return 0.60
    return 0.50

def run_scan(memory):
    print("[📡] Scanning for new trades...")

    account_balance = get_account_balance_mock() if not LIVE_MODE else get_account_balance()
    available_cash = account_balance.get("available_funds", 0)

    trade_idea = {
        "ticker": "NVDA_500C_092024",
        "type": "option",
        "entry_price": 4.20,
        "target_price": 5.88,
        "stop_loss": 2.94,
        "reason": "4.2x risk-reward + whale volume",
    }

    prob = estimate_probability(trade_idea["entry_price"], trade_idea["target_price"], trade_idea["stop_loss"])
    max_affordable_qty = int(available_cash // (trade_idea["entry_price"] * 100))
    projected_gain = round((trade_idea["target_price"] - trade_idea["entry_price"]) * 100 * max_affordable_qty, 2)

    print(f"\n[📈] Suggested Trade:")
    print(f"   Ticker: {trade_idea['ticker']}")
    print(f"   Buy: {max_affordable_qty} contracts @ ${trade_idea['entry_price']}")
    print(f"   Target: ${trade_idea['target_price']} | Stop: ${trade_idea['stop_loss']}")
    print(f"   Probability of success: {int(prob * 100)}%")
    print(f"   Est. Gain: ${projected_gain} | Reason: {trade_idea['reason']}")

    confirm = input("\nType 'GO' to enter trade or anything else to cancel: ")
    if confirm != "GO":
        print("[✘] Cancelled.")
        return

    print("[✓] Entering position...")
    place_order(trade_idea["ticker"], action="BUY")

    action, exit_price = monitor_and_trim(
        trade_idea["ticker"],
        trade_idea["entry_price"],
        trade_idea["stop_loss"],
        trade_idea["target_price"]
    )

    trade_idea.update({
        "quantity": max_affordable_qty,
        "action": action,
        "exit_price": exit_price,
        "timestamp": int(time.time()),
        "gain": round((exit_price - trade_idea["entry_price"]) * 100 * max_affordable_qty, 2),
        "probability": prob
    })

    log_trade(memory, trade_idea)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Schwab Trading Agent")
    parser.add_argument("--scan", action="store_true", help="Scan and suggest trade")
    parser.add_argument("--report", action="store_true", help="Show latest trade report")
    parser.add_argument("--live", action="store_true", help="Run with live Schwab API")
    args = parser.parse_args()

    # refresh_tokens_if_needed()  # Enable in live mode if needed
    if args.live:
        LIVE_MODE = True
        print("[⚠️] Running in LIVE mode. Real trades will be placed.")

    memory = load_memory()

    if args.scan:
        run_scan(memory)

    elif args.report:
        print("[📊] Last Trade:")
        print(json.dumps(memory.get("last_trade", {}), indent=2))
        print(f"[💰] Daily Earnings: ${memory.get('daily_earnings', 0):.2f}")

    else:
        parser.print_help()

