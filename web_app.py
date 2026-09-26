from flask import Flask, request, jsonify, render_template_string
from ai_engine import generate_sales_response
from pathlib import Path
import json

app = Flask(__name__)

BASE_DIR = Path(__file__).parent


def load_product():
    with open(
        BASE_DIR / "product_database.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def load_sales_brain():
    with open(
        BASE_DIR / "sales_agent_brain.md",
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GOTOP AUTOSALES</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 600px;
            margin: auto;
            background: white;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            background: #111;
            color: white;
            padding: 18px;
            text-align: center;
            font-size: 22px;
            font-weight: bold;
        }

        #chat {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
        }

        .message {
            margin: 10px 0;
            padding: 12px;
            border-radius: 10px;
            line-height: 1.5;
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
            display: flex;
            gap: 8px;
            padding: 12px;
            border-top: 1px solid #ddd;
            background: white;
        }

        #message {
            flex: 1;
            padding: 12px;
            border: 1px solid #bbb;
            border-radius: 8px;
            font-size: 16px;
            outline: none;
        }

        #send {
            padding: 12px 18px;
            border: none;
            border-radius: 8px;
            background: #111;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }

        #send:disabled {
            background: #aaa;
            cursor: not-allowed;
        }
    </style>
</head>

<body>

<div class="container">

    <div class="header">
        GOTOP AUTOSALES
    </div>

    <div id="chat">
        <div class="message agent">
            Hello! I am GOTOP AUTOSALES. How can I help you today?
        </div>
    </div>

    <div class="input-area">

        <input
            id="message"
            type="text"
            placeholder="Type your message..."
            autocomplete="off"
        >

        <button
            id="send"
            type="button"
            disabled
        >
            Send
        </button>

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

    if (!message) {
        return;
    }

    addMessage(message, "user");

    input.value = "";

    updateSendButton();

    sendButton.disabled = true;

    sendButton.textContent = "Sending...";

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

            addMessage(data.response, "agent");

        } else if (data.error) {

            addMessage(
                "Error: " + data.error,
                "agent"
            );

        } else {

            addMessage(
                "Sorry, I could not process that message.",
                "agent"
            );

        }

    } catch (error) {

        addMessage(
            "Connection error. Please try again.",
            "agent"
        );

    }


    sendButton.textContent = "Send";

    updateSendButton();

}


sendButton.addEventListener("click", sendMessage);


input.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {

        event.preventDefault();

        if (!sendButton.disabled) {
            sendMessage();
        }

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
    return jsonify({
        "status": "healthy"
    })


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data received."
        }), 400

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "error": "Message is empty."
        }), 400

    try:

        product_information = json.dumps(
            load_product(),
            indent=2
        )

        sales_brain = load_sales_brain()

        response = generate_sales_response(
            customer_message=message,
            sales_brain=sales_brain,
            product_information=product_information
        )

        return jsonify({
            "response": response
        })

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
