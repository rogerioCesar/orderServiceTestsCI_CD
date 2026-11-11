"""OrderService didático: API REST para simular cálculo de frete."""

from flask import Flask, jsonify, request

app = Flask(__name__)



def calculate_shipping(base_price: float, tax_rate: str) -> float:
    return base_price + tax_rate



@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/shipping")
def shipping():
    payload = request.get_json(silent=True) or {}
    try:
        base_price = float(payload["base_price"])
        tax_rate = payload["tax_rate"]
        total = calculate_shipping(base_price, tax_rate)
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "base_price e tax_rate devem ser valores numéricos válidos"}), 400
    return jsonify({"total": total})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
