import argparse
import time
import os
from logic_rules import get_trade_signals_from_csvs, get_trade_signals_from_schwab
from memory import log_trade, load_memory, save_memory
from agent import place_trade, monitor_trade

def run_scan():
    # Check if CSV files exist
    flow_exists = os.path.exists("data/flow.csv")
    darkpool_exists = os.path.exists("data/darkpool.csv")

    if flow_exists and darkpool_exists:
        print("📊 CSV files detected. Using flow + dark pool data...")
        trade_ideas = get_trade_signals_from_csvs()
    else:
        print("📡 No CSVs found. Scanning Schwab API for trade ideas...")
        trade_ideas = get_trade_signals_from_schwab()

    if not trade_ideas:
        print("🚫 No valid trade signals found.")
        return

    print("\n💡 Trade Ideas Found:")
    for idx, idea in enumerate(trade_ideas):
        print(f"{idx + 1}. {idea}")

    print("\n⚠️ Type 'GO' to confirm execution of the first trade.")
    confirm = input(">>> ").strip().lower()
    if confirm != "go":
        print("❌ Trade aborted by user.")
        return

    trade = trade_ideas[0]
    print(f"🚀 Placing trade: {trade}")
    trade_id = place_trade(trade)
    log_trade(trade_id, trade)

    print("📈 Monitoring trade with +40% / –30% rule...")
    while True:
        status = monitor_trade(trade_id)
        if status in ["stop-loss hit", "take-profit hit", "closed"]:
            print(f"✅ Trade complete: {status}")
            break
        time.sleep(60)  # Check every 60 seconds

def main():
    parser = argparse.ArgumentParser(description="Trading Agent CLI")
    parser.add_argument("--scan", action="store_true", help="Run trade signal scan and monitoring")

    args = parser.parse_args()

    if args.scan:
        run_scan()
    else:
        print("📘 Usage: python run_agent.py --scan")

if __name__ == "__main__":
    main()
