from flask import Flask, request, jsonify, render_template_string
from ai_engine import generate_sales_response
from pathlib import Path
import json

app = Flask(__name__)

BASE_DIR = Path(__file__).parent


def load_product_information():
    with open(
        BASE_DIR / "product_database.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.dumps(json.load(file), indent=2)


def load_sales_brain():
    with open(
        BASE_DIR / "sales_agent_brain.md",
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GOTOP AUTOSALES</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f7f3f5;
            margin: 0;
            padding: 0;
        }

        .header {
            background: #8b1458;
            color: white;
            padding: 22px;
            text-align: center;
        }

        .header h1 {
            margin: 0;
            font-size: 26px;
        }

        .header p {
            margin: 6px 0 0;
        }

        .chat {
            max-width: 700px;
            margin: 20px auto;
            padding: 15px;
        }

        #messages {
            min-height: 300px;
            background: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        .message {
            margin: 10px 0;
            padding: 12px;
            border-radius: 10px;
            line-height: 1.5;
        }

        .user {
            background: #eee;
            text-align: right;
        }

        .agent {
            background: #f3d9e8;
        }

        .input-area {
            display: flex;
            gap: 8px;
            margin-top: 15px;
        }

        input {
            flex: 1;
            padding: 14px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 16px;
        }

        button {
            background: #8b1458;
            color: white;
            border: none;
            padding: 14px 18px;
            border-radius: 8px;
            font-size: 16px;
        }

        button:disabled {
            opacity: 0.6;
        }
    </style>
</head>

<body>

<div class="header">
    <h1>GOTOP AUTOSALES</h1>
    <p>AI-Powered Sales Agent</p>
</div>

<div class="chat">

    <div id="messages">
        <div class="message agent">
            <strong>GOTOP AUTOSALES:</strong><br>
            Hello! I'm your GOTOP AUTOSALES agent.
            How can I help you today?
        </div>
    </div>

    <div class="input-area">
        <input
            id="message"
            type="text"
            placeholder="Type your message..."
        >

        <button id="sendButton" onclick="sendMessage()">
            Send
        </button>
    </div>

</div>

<script>

async function sendMessage() {

    const input = document.getElementById("message");
    const button = document.getElementById("sendButton");
    const messages = document.getElementById("messages");

    const message = input.value.trim();

    if (!message) {
        return;
    }

    messages.innerHTML +=
        '<div class="message user"><strong>You:</strong><br>' +
        message +
        '</div>';

    input.value = "";
    button.disabled = true;
    button.innerText = "Thinking...";

    try {

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        if (data.response) {

            messages.innerHTML +=
                '<div class="message agent"><strong>GOTOP AUTOSALES:</strong><br>' +
                data.response.replace(/\n/g, "<br>") +
                '</div>';

        } else {

            messages.innerHTML +=
                '<div class="message agent"><strong>Error:</strong><br>' +
                (data.error || "Unable to respond.") +
                '</div>';
        }

    } catch (error) {

        messages.innerHTML +=
            '<div class="message agent"><strong>Error:</strong><br>' +
            'The AI service could not be reached.' +
            '</div>';
    }

    button.disabled = false;
    button.innerText = "Send";
}

document.getElementById("message").addEventListener(
    "keydown",
    function(event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    }
);

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HOME_PAGE)


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

    try:

        sales_brain = load_sales_brain()
        product_information = load_product_information()

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
