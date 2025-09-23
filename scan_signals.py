# scan_signals.py

import csv
import json
import os
from evaluate_trade import evaluate_option_trade, evaluate_stock_trade

MOCK_OPTION_PATH = './mock_server/data/mock_option_chain.json'
FLOW_CSV_PATH = './scanner/flow.csv'
DARKPOOL_CSV_PATH = './scanner/darkpool.csv'


def load_mock_option_chain():
    with open(MOCK_OPTION_PATH, 'r') as f:
        return json.load(f)


def load_csv_signals(csv_path):
    trades = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            trades.append(row)
    return trades


def scan_all_signals(cash_balance, memory):
    """Scans both flow.csv and darkpool.csv, cross-analyzes with option chain and memory."""
    option_chain = load_mock_option_chain()
    flow_signals = load_csv_signals(FLOW_CSV_PATH)
    darkpool_signals = load_csv_signals(DARKPOOL_CSV_PATH)

    all_signals = flow_signals + darkpool_signals
    scored_trades = []

    for signal in all_signals:
        ticker = signal.get('ticker') or signal.get('symbol')
        if not ticker or ticker in memory.get("blacklist_commands", []):
            continue

        # OPTION TRADE
        if signal.get('type') == 'option':
            score = evaluate_option_trade(signal, option_chain, cash_balance, memory)
        # STOCK TRADE
        else:
            score = evaluate_stock_trade(signal, cash_balance, memory)

        if score:
            scored_trades.append(score)

    # Sort by probability of success, then gain
    sorted_trades = sorted(scored_trades, key=lambda x: (-x['probability'], -x['expected_gain']))

    return sorted_trades[:3]  # Top 3 trades


if __name__ == '__main__':
    # Debug mode for testing
    from memory import load_memory
    memory = load_memory()
    cash = memory.get("available_cash", 1000)
    top_trades = scan_all_signals(cash, memory)
    for trade in top_trades:
        print(json.dumps(trade, indent=2))
