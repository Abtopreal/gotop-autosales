import json
from pathlib import Path
from datetime import datetime
from uuid import uuid4

BASE_DIR = Path(__file__).parent


def load_customer_database():
    with open(
        BASE_DIR / "customers.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def classify_intent(message):
    text = message.lower()

    bulk_words = [
        "wholesale",
        "bulk",
        "resell",
        "retailer",
        "retail",
        "distributor",
        "business"
    ]

    buying_words = [
        "buy",
        "order",
        "purchase",
        "want",
        "need",
        "get"
    ]

    payment_words = [
        "payment",
        "pay",
        "transfer"
    ]

    delivery_words = [
        "delivery",
        "deliver",
        "shipping",
        "dispatch"
    ]

    if any(word in text for word in bulk_words):
        return "BULK_RESELLING"

    if any(word in text for word in payment_words):
        return "PAYMENT"

    if any(word in text for word in delivery_words):
        return "DELIVERY"

    if any(word in text for word in buying_words):
        return "BUYING"

    return "INFORMATION"


def classify_lead(message):
    text = message.lower()

    hot_words = [
        "buy",
        "order",
        "purchase",
        "how do i pay",
        "account number",
        "send me",
        "delivery"
    ]

    warm_words = [
        "interested",
        "price",
        "cost",
        "how much",
        "tell me more",
        "available"
    ]

    if any(word in text for word in hot_words):
        return "HOT"

    if any(word in text for word in warm_words):
        return "WARM"

    return "INFORMATION_ONLY"


def create_customer(
    name,
    phone,
    location,
    customer_type,
    message,
    quantity_interest=0,
    source="UNKNOWN",
    consent_to_follow_up=False,
    notes=""
):
    now = datetime.utcnow().isoformat()

    return {
        "customer_id": "CUS-" + uuid4().hex[:8].upper(),
        "name": name,
        "phone": phone,
        "location": location,
        "customer_type": customer_type,
        "lead_status": classify_lead(message),
        "intent": classify_intent(message),
        "quantity_interest": quantity_interest,
        "product": "SP-6 Advanced Oral Care",
        "source": source,
        "consent_to_follow_up": consent_to_follow_up,
        "notes": notes,
        "created_at": now,
        "updated_at": now
    }


def update_customer(customer, message):
    customer["lead_status"] = classify_lead(message)
    customer["intent"] = classify_intent(message)
    customer["updated_at"] = datetime.utcnow().isoformat()

    return customer


if __name__ == "__main__":

    customer = create_customer(
        name="Test Customer",
        phone="",
        location="Ibadan",
        customer_type="INDIVIDUAL",
        message="I want to buy 10 tubes",
        quantity_interest=10,
        source="WHATSAPP",
        consent_to_follow_up=True
    )

    print("\n===== GOTOP AUTOSALES CUSTOMER =====")

    for key, value in customer.items():
        print(f"{key}: {value}")

    print("====================================\n")
