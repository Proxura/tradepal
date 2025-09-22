# scanner.py
# Parses /data/flow.csv and /data/darkpool.csv, generates trade ideas, integrates Schwab option chain

import pandas as pd
import os
import random
from schwab_api import get_option_chain, get_equity_price

FLOW_PATH = "data/flow.csv"
DARKPOOL_PATH = "data/darkpool.csv"


def parse_flow():
    if not os.path.exists(FLOW_PATH):
        return []
    df = pd.read_csv(FLOW_PATH)
    df = df[df['unusual'] == True]
    return df[['ticker', 'type', 'volume', 'strike', 'expiry']].dropna()


def parse_darkpool():
    if not os.path.exists(DARKPOOL_PATH):
        return []
    df = pd.read_csv(DARKPOOL_PATH)
    df = df[df['sweep'] == True]
    return df[['ticker', 'amount', 'sentiment']].dropna()


def generate_trade_ideas():
    ideas = []
    flow = parse_flow()
    darkpool = parse_darkpool()

    tickers = set(flow['ticker']).union(set(darkpool['ticker']))

    for ticker in tickers:
        price = get_equity_price(ticker)
        if not price or price < 3 or price > 600:
            continue

        # Placeholder criteria for a good trade idea:
        option_chain = get_option_chain(ticker)
        if not option_chain:
            continue

        call_ideas = [opt for opt in option_chain if opt['type'] == 'CALL' and opt['delta'] >= 0.4 and opt['delta'] <= 0.7]
        if not call_ideas:
            continue

        selected = random.choice(call_ideas)
        ideas.append({
            'ticker': ticker,
            'type': 'option',
            'strike': selected['strike'],
            'expiry': selected['expiry'],
            'price': selected['ask'],
            'direction': 'bullish'
        })

    return ideas[:3]  # return top 3 ideas
