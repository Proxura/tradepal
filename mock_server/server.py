from flask import Flask, jsonify
import json
import os

app = Flask(__name__)
DATA_PATH = os.path.join(os.path.dirname(__file__), "data")

@app.route('/v1/option_chains/<ticker>')
def get_option_chain(ticker):
    try:
        with open(os.path.join(DATA_PATH, "option_chain.json")) as f:
            option_data = json.load(f)
        return jsonify(option_data.get(ticker.upper(), {"error": "Ticker not found"}))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)
