import json
from pathlib import Path

BASE_DIR = Path(__file__).parent


def load_product():
    with open(
        BASE_DIR / "product_database.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def identify_intent(message):
    text = message.lower()

    buying_words = [
        "buy",
        "order",
        "purchase",
        "want",
        "need",
        "get",
        "price",
        "cost"
    ]

    bulk_words = [
        "wholesale",
        "bulk",
        "resell",
        "retail",
        "distributor",
        "10 tubes",
        "20 tubes",
        "50 tubes",
        "100 tubes"
    ]

    payment_words = [
        "payment",
        "pay",
        "account",
        "transfer"
    ]

    delivery_words = [
        "delivery",
        "deliver",
        "shipping",
        "dispatch"
    ]

    if any(word in text for word in payment_words):
        return "PAYMENT"

    if any(word in text for word in delivery_words):
        return "DELIVERY"

    if any(word in text for word in bulk_words):
        return "BULK_RESELLING"

    if any(word in text for word in buying_words):
        return "BUYING"

    return "INFORMATION"


def generate_response(message):
    product = load_product()
    intent = identify_intent(message)

    product_name = product["product"]["name"]
    price = product["product"]["current_price_ngn"]

    bulk_minimum = product["product"]["bulk_offer"]["minimum_quantity"]
    bulk_discount = product["product"]["bulk_offer"]["discount_percent"]
    bulk_price = product["product"]["bulk_offer"]["discounted_unit_price_ngn"]

    if intent == "BUYING":
        return (
            f"{product_name} is currently ₦{price:,} per tube. "
            f"If you are buying {bulk_minimum} tubes or more, "
            f"the applicable bulk offer is {bulk_discount}% off, "
            f"making it ₦{bulk_price:,} per tube. "
            "How many tubes would you like to order, and what is your location?"
        )

    if intent == "BULK_RESELLING":
        return (
            f"{product_name} is available for bulk purchase. "
            f"For {bulk_minimum} tubes or more, the applicable bulk offer "
            f"is {bulk_discount}% off, making it ₦{bulk_price:,} per tube. "
            "Please tell me the quantity you need, your location, "
            "and whether the order is for resale or business use."
        )

    if intent == "PAYMENT":
        return (
            "Payment is by approved bank transfer. "
            "The order should first be confirmed before payment details "
            "are provided. Payment is treated as received only after "
            "verification."
        )

    if intent == "DELIVERY":
        return (
            "Delivery charges depend on the destination and quantity. "
            "Please tell me your location and the number of tubes you "
            "would like to order so the delivery charge can be calculated."
        )

    return (
        f"{product_name} is an oral-care product currently available "
        f"at ₦{price:,} per tube. "
        "How can I help you today?"
    )


def handle_customer_message(message):
    return {
        "customer_message": message,
        "intent": identify_intent(message),
        "agent_response": generate_response(message)
    }


if __name__ == "__main__":
    test_message = "I want to buy 10 tubes"

    result = handle_customer_message(test_message)

    print("\n===== GOTOP AUTOSALES =====")
    print(f"Customer: {result['customer_message']}")
    print(f"Intent: {result['intent']}")
    print(f"Agent: {result['agent_response']}")
    print("===========================\n")
