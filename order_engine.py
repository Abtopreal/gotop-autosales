import json
from pathlib import Path
from datetime import datetime
from uuid import uuid4

BASE_DIR = Path(__file__).parent


def load_product():
    with open(
        BASE_DIR / "product_database.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def calculate_delivery(quantity, location):
    product = load_product()

    if "ibadan" in location.lower():
        rules = product["delivery"]["ibadan"]
    else:
        rules = product["delivery"]["outside_ibadan"]

    complete_blocks = quantity // 12
    remainder = quantity % 12

    fee = complete_blocks * rules["complete_12_tubes_fee"]

    if remainder > 0:
        fee += rules["remainder_1_to_9_fee"]

    return fee


def calculate_order(quantity, location):
    product = load_product()

    base_price = product["product"]["current_price_ngn"]
    bulk = product["product"]["bulk_offer"]

    if quantity >= bulk["minimum_quantity"]:
        unit_price = bulk["discounted_unit_price_ngn"]
        discount_percent = bulk["discount_percent"]
    else:
        unit_price = base_price
        discount_percent = 0

    product_total = quantity * unit_price

    delivery_fee = calculate_delivery(
        quantity,
        location
    )

    order_total = product_total + delivery_fee

    return {
        "product": product["product"]["name"],
        "quantity": quantity,
        "unit_price_ngn": unit_price,
        "discount_percent": discount_percent,
        "product_total_ngn": product_total,
        "delivery_location": location,
        "delivery_fee_ngn": delivery_fee,
        "order_total_ngn": order_total
    }


def create_order(quantity, location, customer_id):
    order = calculate_order(
        quantity,
        location
    )

    now = datetime.utcnow().isoformat()

    order_record = {
        "order_id": "ORD-" + uuid4().hex[:8].upper(),
        "customer_id": customer_id,
        "product": order["product"],
        "quantity": order["quantity"],
        "unit_price_ngn": order["unit_price_ngn"],
        "discount_percent": order["discount_percent"],
        "product_total_ngn": order["product_total_ngn"],
        "delivery_location": order["delivery_location"],
        "delivery_fee_ngn": order["delivery_fee_ngn"],
        "order_total_ngn": order["order_total_ngn"],
        "payment_method": "BANK_TRANSFER",
        "payment_status": "AWAITING_PAYMENT",
        "fulfilment_status": "NOT_STARTED",
        "order_status": "DRAFT",
        "created_at": now,
        "updated_at": now,
        "notes": ""
    }

    return order_record


if __name__ == "__main__":

    test_order = create_order(
        quantity=13,
        location="Ibadan",
        customer_id="CUS-TEST001"
    )

    print("\n===== GOTOP AUTOSALES ORDER =====")

    for key, value in test_order.items():
        print(f"{key}: {value}")

    print("=================================\n")
