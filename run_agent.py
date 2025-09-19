import argparse
from agent import TradingAgent
from memory import load_memory, save_memory

# Load current memory state
memory = load_memory()

# Create the trading agent instance
agent = TradingAgent(memory)

# CLI args
parser = argparse.ArgumentParser(description="Autonomous Trading Agent")
parser.add_argument("--scan", action="store_true", help="Scan flow + darkpool CSVs and suggest trades")
parser.add_argument("--trade", action="store_true", help="Place trade with limit sale + stop-loss")
parser.add_argument("--backtest", action="store_true", help="Run backtest simulation on historical data (coming soon)")

args = parser.parse_args()

# Process commands
if args.scan:
    agent.scan_for_trades()

elif args.trade:
    agent.execute_trade()

elif args.backtest:
    print("[⚠️ BACKTEST NOT YET IMPLEMENTED]")
    # Placeholder for future function: agent.run_backtest()

else:
    print("No valid command provided. Use --scan or --trade.")
