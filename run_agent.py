import argparse
import time
import json
import os
from auth import refresh_tokens_if_needed
from schwab_api import get_option_quote, place_order, get_account_balance

MEMORY_PATH = "memory.json"


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
    print(f"[+] Monitoring {ticker}...")
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


def run_scan(memory):
    print("[•] Scanning for new trades (CSV + Schwab signals)...")
    # Placeholder: logic for actual signal parsing
    trade_idea = {
        "ticker": "TSLA",
        "type": "option",
        "entry_price": 2.97,
        "target_price": 4.16,
        "stop_loss": 2.08
    }

    print(f"[+] Found opportunity: {trade_idea['ticker']} @ ${trade_idea['entry_price']}")
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

    trade_idea["action"] = action
    trade_idea["exit_price"] = exit_price
    trade_idea["timestamp"] = int(time.time())
    trade_idea["gain"] = round((exit_price - trade_idea["entry_price"]) * 100, 2)
    log_trade(memory, trade_idea)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Schwab Trading Agent")
    parser.add_argument("--scan", action="store_true", help="Scan and enter trade")
    parser.add_argument("--report", action="store_true", help="Show report of last trade")
    args = parser.parse_args()

    refresh_tokens_if_needed()
    memory = load_memory()

    if args.scan:
        run_scan(memory)

    elif args.report:
        print("[📈] Last trade:")
        print(json.dumps(memory.get("last_trade", {}), indent=2))
        print(f"[💰] Daily Earnings: ${memory.get('daily_earnings', 0):.2f}")

    else:
        parser.print_help()
