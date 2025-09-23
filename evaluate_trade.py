import json
import os

def evaluate_option_trade(option, available_cash, risk_profile):
    """
    Evaluate a single option trade candidate and return a structured evaluation.
    """
    cost_per_contract = option['ask'] * 100
    max_loss = risk_profile.get('max_loss_per_trade', 100)
    min_profit_target = risk_profile.get('min_profit_target', 50)
    
    affordable_contracts = int(available_cash // cost_per_contract)
    expected_gain = option['estimated_profit']
    expected_loss = option['estimated_loss']
    probability = option['probability']
    
    if affordable_contracts == 0:
        return None

    meets_risk = expected_loss <= max_loss and expected_gain >= min_profit_target

    return {
        'type': 'option',
        'ticker': option['ticker'],
        'strike': option['strike'],
        'expiry': option['expiry'],
        'side': option['side'],
        'price': option['ask'],
        'contracts': affordable_contracts,
        'probability': probability,
        'expected_gain': expected_gain,
        'expected_loss': expected_loss,
        'meets_risk': meets_risk,
    }


def evaluate_stock_trade(stock, available_cash, risk_profile):
    """
    Evaluate a single stock trade candidate and return a structured evaluation.
    """
    max_loss = risk_profile.get('max_loss_per_trade', 100)
    min_profit_target = risk_profile.get('min_profit_target', 50)

    shares = int(available_cash // stock['price'])
    expected_gain = stock['estimated_profit']
    expected_loss = stock['estimated_loss']
    probability = stock['probability']

    if shares == 0:
        return None

    meets_risk = expected_loss <= max_loss and expected_gain >= min_profit_target

    return {
        'type': 'stock',
        'ticker': stock['ticker'],
        'price': stock['price'],
        'shares': shares,
        'probability': probability,
        'expected_gain': expected_gain,
        'expected_loss': expected_loss,
        'meets_risk': meets_risk,
    }


def load_mock_data(mock_file_path):
    """
    Load mock options or stock data for evaluation.
    """
    if not os.path.exists(mock_file_path):
        return []

    with open(mock_file_path, 'r') as f:
        return json.load(f)
