# main.py

from flask import Flask
from logic_rules import run_trading_logic
from memory import memory

app = Flask(__name__)

@app.route("/")
def home():
    result = run_trading_logic()
    return f"""
        <h1>TradePal Bot</h1>
        <p>{result}</p>
        <h2>Current Positions:</h2>
        <pre>{memory.get('positions', {})}</pre>
        <h2>Trade Log:</h2>
        <pre>{memory.get('trade_log', [])}</pre>
    """

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=8182)


