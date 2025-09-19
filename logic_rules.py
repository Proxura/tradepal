# logic_rules.py

import random
from memory import set_last_signal, get_last_signal, log_trade

def generate_mock_signal():
    """Randomly generate buy/sell/hold signal (for testing)"""
    signal = random.choice(["buy", "sell", "hold"])
    set_last_signal(signal)
    return signal

def should_buy():
    return get_last_signal() == "buy"

def should_sell():
    return get_last_signal() == "sell"

def run_trading_logic():
    signal = generate_mock_signal()

    if signal == "buy":
        log_trade("buy", "AAPL", 1, "Random signal logic")
        return "Buying AAPL"
    elif signal == "sell":
        log_trade("sell", "AAPL", 1, "Random signal logic")
        return "Selling AAPL"
    else:
        return "Holding position"
