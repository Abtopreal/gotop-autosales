from flask import Flask, request, jsonify
from ai_engine import generate_sales_response

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "agent": "GOTOP AUTOSALES",
        "version": "1.0",
        "status": "online"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}

    customer_message = data.get("message", "").strip()

    if not customer_message:
        return jsonify({
            "error": "Customer message is required."
        }), 400

    sales_brain = data.get(
        "sales_brain",
        "Follow the GOTOP AUTOSALES sales rules."
    )

    product_information = data.get(
        "product_information",
        "Use the configured GOTOP AUTOSALES product information."
    )

    try:

        answer = generate_sales_response(
            customer_message=customer_message,
            sales_brain=sales_brain,
            product_information=product_information
        )

        return jsonify({
            "agent": "GOTOP AUTOSALES",
            "customer_message": customer_message,
            "response": answer
        })

    except Exception as error:

        return jsonify({
            "error": "AI service is not currently available.",
            "details": str(error)
        }), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
