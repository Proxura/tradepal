import argparse
import json
import os
import time
from logic_rules import generate_trade_ideas, evaluate_trade
from auth import get_schwab_session, place_order, check_order_status, get_current_price

MEMORY_FILE = 'memory.json'

# Load memory
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, 'r') as f:
        memory = json.load(f)
else:
    memory = {
        "daily_earnings": 0,
        "last_trade": {},
        "strategy_notes": "",
        "blacklist_commands": [],
        "risk_profile": {
            "max_loss_per_trade": 100,
            "min_profit_target": 50
        },
        "trade_history": [],
        "auto_limits": {
            "take_profit_pct": 0.40,
            "stop_loss_pct": -0.30,
            "poll_interval_seconds": 60
        }
    }

def save_memory():
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def scan_and_suggest():
    print("\n📊 Scanning data/flow.csv and data/darkpool.csv...")
    trade_ideas = generate_trade_ideas("data/flow.csv", "data/darkpool.csv")

    if not trade_ideas:
        print("No high-probability trade ideas found.")
        return

    for i, idea in enumerate(trade_ideas[:3]):
        print(f"\n🔥 Trade Idea #{i+1}")
        print(json.dumps(idea, indent=2))

    print("\nType 'GO' to execute the first idea, or Ctrl+C to cancel.")
    if input().strip().lower() == 'go':
        execute_trade(trade_ideas[0])

def execute_trade(trade):
    session = get_schwab_session()
    symbol = trade['symbol']
    qty = trade['qty']
    entry_price = float(get_current_price(symbol))
    limit_price = round(entry_price * (1 + memory['auto_limits']['take_profit_pct']), 2)
    stop_price = round(entry_price * (1 + memory['auto_limits']['stop_loss_pct']), 2)

    print(f"\n🚀 Executing trade for {symbol} @ ${entry_price} | TP: ${limit_price} | SL: ${stop_price}")
    order_id = place_order(session, symbol, qty)

    memory['last_trade'] = {
        "symbol": symbol,
        "qty": qty,
        "entry": entry_price,
        "tp": limit_price,
        "sl": stop_price,
        "order_id": order_id,
        "status": "live"
    }
    memory['trade_history'].append(memory['last_trade'])
    save_memory()

    monitor_trade(session)

def monitor_trade(session):
    print("\n⏱ Monitoring trade...")
    while True:
        last = memory['last_trade']
        current = float(get_current_price(last['symbol']))
        print(f"[MONITOR] {last['symbol']} @ ${current:.2f} (TP: ${last['tp']} | SL: ${last['sl']})")

        if current >= last['tp']:
            print("✅ Take-profit hit. Locking gain.")
            memory['last_trade']['status'] = 'closed_tp'
            memory['daily_earnings'] += memory['risk_profile']['min_profit_target']
            break
        elif current <= last['sl']:
            print("🛑 Stop-loss hit. Cutting loss.")
            memory['last_trade']['status'] = 'closed_sl'
            memory['daily_earnings'] -= memory['risk_profile']['max_loss_per_trade']
            break

        time.sleep(memory['auto_limits']['poll_interval_seconds'])

    save_memory()

def main():
    parser = argparse.ArgumentParser(description='Trading Agent CLI')
    parser.add_argument('--scan', action='store_true', help='Scan CSVs and generate trade ideas')
    parser.add_argument('--run', action='store_true', help='Run and monitor current trade')
    args = parser.parse_args()

    if args.scan:
        scan_and_suggest()
    elif args.run:
        monitor_trade(get_schwab_session())
    else:
        print("⚠️ No valid arguments. Use --scan or --run")

if __name__ == '__main__':
    main()
