from flask import Flask, request, jsonify, render_template_string
from ai_engine import generate_sales_response
from pathlib import Path
import json
import re

app = Flask(__name__)
BASE_DIR = Path(__file__).parent


def load_json(filename):
    with open(BASE_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


def load_product():
    return load_json("product_database.json")


def load_sales_brain():
    with open(
        BASE_DIR / "sales_agent_brain.md",
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


def find_sp6_product(data):
    """Find the SP-6 product record in the existing product database."""

    if isinstance(data, dict):
        name = str(
            data.get("product_name", data.get("name", ""))
        ).lower()

        if (
            ("sp-6" in name or "sp6" in name
             or "advanced oral care" in name)
            and "current_price_ngn" in data
        ):
            return data

        for value in data.values():
            result = find_sp6_product(value)
            if result is not None:
                return result

    elif isinstance(data, list):
        for item in data:
            result = find_sp6_product(item)
            if result is not None:
                return result

    return None


def calculate_delivery(quantity, location, delivery_data):
    """Calculate delivery using the configured delivery rules."""

    rules = delivery_data["delivery_rules"][location]

    complete_blocks = quantity // 12
    remainder = quantity % 12

    fee = complete_blocks * rules["complete_12_tubes_fee"]

    if 1 <= remainder <= 9:
        fee += rules["remainder_1_to_9_fee"]
    elif 10 <= remainder <= 11:
        fee += rules["complete_12_tubes_fee"]

    return fee


def landini_response():
    return (
        "Thank you for your interest in Landini Tractors.\n\n"
        "For distributor, dealer and strategic partnership "
        "enquiries in Nigeria, please contact:\n\n"
        "Mr. Leonardo\n"
        "Chief Coordinator and Strategist\n\n"
        "Telephone/WhatsApp:\n"
        "+39 3202790222\n"
        "+39 3463026092\n\n"
        "Email: newagetomatoes@gmail.com\n\n"
        "Please contact Mr. Leonardo directly for further "
        "information about the opportunity and requirements."
    )


def sp6_response(message):
    text = message.lower()

    database = load_product()
    product = find_sp6_product(database)

    if product is None:
        return (
            "I could not locate the SP-6 product record in the "
            "product database. Please check product_database.json."
        )

    price = product.get("current_price_ngn")

    if price is None:
        return "The SP-6 price is missing from the product database."

    bulk = product.get("bulk_offer", {})
    minimum = int(bulk.get("minimum_quantity", 10))
    bulk_price = bulk.get("discounted_unit_price_ngn", 6300)

    delivery_data = load_json("delivery.json")

    quantity_match = re.search(
        r"\b(\d+)\s*(?:tubes?|units?)\b",
        text
    )

    quantity = (
        int(quantity_match.group(1))
        if quantity_match
        else None
    )

    delivery_words = [
        "delivery",
        "deliver",
        "shipping",
        "transport",
        "delivery fee",
        "to ibadan",
        "outside ibadan"
    ]

    asks_delivery = any(word in text for word in delivery_words)

    if quantity is None or quantity <= 0:
        return (
            "GOTOP AUTOSALES — SP-6 ADVANCED ORAL CARE\n\n"
            f"Price per tube: ₦{price:,.0f}\n"
            f"Bulk offer: {minimum} tubes or more at "
            f"₦{bulk_price:,.0f} per tube.\n\n"
            "To calculate your total, tell me the number of tubes "
            "you need and whether delivery is in Ibadan or outside "
            "Ibadan."
        )

    unit_price = bulk_price if quantity >= minimum else price
    subtotal = quantity * unit_price

    response = (
        "GOTOP AUTOSALES — SP-6 ADVANCED ORAL CARE\n\n"
        f"Quantity: {quantity} tube(s)\n"
        f"Unit price: ₦{unit_price:,.0f}\n"
        f"Product subtotal: ₦{subtotal:,.0f}\n"
    )

    if quantity >= minimum:
        response += (
            f"Bulk discount: {bulk.get('discount_percent', 10)}%\n"
        )

    if asks_delivery:
        if "ibadan" not in text:
            return (
                response
                + "\nPlease specify whether delivery is within "
                "Ibadan or outside Ibadan so the correct delivery "
                "fee can be calculated."
            )

        if "outside ibadan" in text:
            location = "outside_ibadan"
            location_name = "Outside Ibadan"
        else:
            location = "ibadan"
            location_name = "Ibadan"

        fee = calculate_delivery(
            quantity,
            location,
            delivery_data
        )

        response += (
            f"Delivery location: {location_name}\n"
            f"Delivery fee: ₦{fee:,.0f}\n"
            f"Total including delivery: ₦{subtotal + fee:,.0f}\n"
        )

    response += (
        "\nPlease confirm your order quantity and delivery "
        "location before making payment."
    )

    return response


HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport"
 content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>GOTOP AUTOSALES</title>

<style>
* { box-sizing: border-box; }

html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    font-family: Arial, sans-serif;
    background: #f5f5f5;
}

body { overflow: hidden; }

.container {
    width: 100%;
    max-width: 600px;
    height: 100vh;
    height: 100dvh;
    margin: auto;
    background: white;
    display: flex;
    flex-direction: column;
}

.header {
    flex: 0 0 auto;
    background: #111;
    color: white;
    padding: 16px;
    text-align: center;
    font-size: 22px;
    font-weight: bold;
}

#chat {
    flex: 1 1 auto;
    min-height: 0;
    padding: 15px;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
}

.message {
    margin: 10px 0;
    padding: 12px;
    border-radius: 10px;
    line-height: 1.5;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.user {
    background: #e8f0fe;
    text-align: right;
}

.agent {
    background: #f1f1f1;
    text-align: left;
}

.input-area {
    flex: 0 0 auto;
    display: flex;
    gap: 8px;
    padding: 10px;
    padding-bottom: calc(10px + env(safe-area-inset-bottom));
    border-top: 1px solid #ddd;
    background: white;
}

#message {
    flex: 1 1 auto;
    min-width: 0;
    padding: 12px;
    border: 1px solid #bbb;
    border-radius: 8px;
    font-size: 16px;
}

#send {
    flex: 0 0 auto;
    padding: 12px 16px;
    min-width: 72px;
    border: none;
    border-radius: 8px;
    background: #111;
    color: white;
    font-size: 16px;
    cursor: pointer;
    touch-action: manipulation;
}

#send:disabled {
    background: #aaa;
    cursor: not-allowed;
}

@media (max-width: 480px) {
    .header { padding: 14px 10px; font-size: 19px; }
    #chat { padding: 10px; }
    .message { padding: 10px; font-size: 15px; }
    .input-area {
        gap: 6px;
        padding: 8px;
        padding-bottom: calc(8px + env(safe-area-inset-bottom));
    }
    #message { padding: 11px; font-size: 16px; }
    #send { padding: 11px 13px; min-width: 68px; font-size: 15px; }
}
</style>
</head>

<body>
<div class="container">
    <div class="header">GOTOP AUTOSALES</div>

    <div id="chat">
        <div class="message agent">
            Hello! I am GOTOP AUTOSALES. How can I help you today?
        </div>
    </div>

    <div class="input-area">
        <input id="message" type="text"
               placeholder="Type your message..."
               autocomplete="off">
        <button id="send" type="button" disabled>Send</button>
    </div>
</div>

<script>
const input = document.getElementById("message");
const sendButton = document.getElementById("send");
const chat = document.getElementById("chat");

function addMessage(text, type) {
    const message = document.createElement("div");
    message.className = "message " + type;
    message.textContent = text;
    chat.appendChild(message);
    chat.scrollTop = chat.scrollHeight;
}

function updateSendButton() {
    sendButton.disabled = input.value.trim() === "";
}

input.addEventListener("input", updateSendButton);

async function sendMessage() {
    const message = input.value.trim();

    if (!message || sendButton.disabled) return;

    addMessage(message, "user");
    input.value = "";
    updateSendButton();
    sendButton.disabled = true;
    sendButton.textContent = "Sending...";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: message})
        });

        const data = await response.json();

        if (data.response) {
            addMessage(data.response, "agent");
        } else {
            addMessage(
                "Error: " + (data.error || "Unable to process message."),
                "agent"
            );
        }
    } catch (error) {
        addMessage("Connection error. Please try again.", "agent");
    }

    sendButton.textContent = "Send";
    updateSendButton();
}

sendButton.addEventListener("click", sendMessage);

input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        if (!sendButton.disabled) sendMessage();
    }
});

updateSendButton();
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No data received."}), 400

    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message is empty."}), 400

    text = message.lower()

    landini_keywords = [
        "landini",
        "tractor distributor",
        "tractor dealer",
        "tractors distributor",
        "tractors dealer",
        "agricultural machinery distributor",
        "landini partnership"
    ]

    if any(word in text for word in landini_keywords):
        return jsonify({"response": landini_response()})

    sp6_keywords = [
        "sp-6",
        "sp6",
        "advanced oral care",
        "oral care",
        "toothpaste"
    ]

    generic_product_words = [
        "tube",
        "tubes",
        "delivery",
        "deliver",
        "shipping",
        "transport"
    ]

    is_sp6 = any(word in text for word in sp6_keywords)

    is_quantity_delivery = (
        bool(re.search(r"\b\d+\s*(?:tubes?|units?)\b", text))
        and any(word in text for word in generic_product_words)
    )

    if is_sp6 or is_quantity_delivery:
        try:
            return jsonify({"response": sp6_response(message)})
        except Exception:
            app.logger.exception("SP-6 response failed")
            return jsonify({
                "response": (
                    "Sorry, I could not retrieve the SP-6 information. "
                    "Please check product_database.json and delivery.json."
                )
            })

    try:
        product_information = json.dumps(load_product(), indent=2)
        sales_brain = load_sales_brain()

        response = generate_sales_response(
            customer_message=message,
            sales_brain=sales_brain,
            product_information=product_information
        )

        return jsonify({"response": response})

    except Exception as error:
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
