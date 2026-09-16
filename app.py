import json
from pathlib import Path

APP_NAME = "GOTOP AUTOSALES"
VERSION = "1.0"

BASE_DIR = Path(__file__).parent


def load_json(filename):
    file_path = BASE_DIR / filename

    if not file_path.exists():
        return {}

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_product():
    return load_json("product_database.json")


def calculate_delivery(quantity, location):
    product = load_product()
    delivery = product["delivery"]

    location_text = location.lower()

    if "ibadan" in location_text:
        rules = delivery["ibadan"]
    else:
        rules = delivery["outside_ibadan"]

    complete_blocks = quantity // 12
    remainder = quantity % 12

    fee = complete_blocks * rules["complete_12_tubes_fee"]

    if remainder > 0:
        fee += rules["remainder_1_to_9_fee"]

    return fee


def calculate_order(quantity, location):
    product = load_product()

    price = product["product"]["current_price_ngn"]
    bulk = product["product"]["bulk_offer"]

    if quantity >= bulk["minimum_quantity"]:
        unit_price = bulk["discounted_unit_price_ngn"]
        discount_percent = bulk["discount_percent"]
    else:
        unit_price = price
        discount_percent = 0

    product_total = quantity * unit_price
    delivery_fee = calculate_delivery(quantity, location)

    total = product_total + delivery_fee

    return {
        "product": product["product"]["name"],
        "quantity": quantity,
        "unit_price_ngn": unit_price,
        "discount_percent": discount_percent,
        "product_total_ngn": product_total,
        "delivery_fee_ngn": delivery_fee,
        "order_total_ngn": total,
        "delivery_location": location
    }


def create_order_summary(quantity, location):
    order = calculate_order(quantity, location)

    print("\n===== GOTOP AUTOSALES ORDER SUMMARY =====")
    print(f"Product: {order['product']}")
    print(f"Quantity: {order['quantity']} tube(s)")
    print(f"Unit price: ₦{order['unit_price_ngn']:,}")
    print(f"Discount: {order['discount_percent']}%")
    print(f"Product total: ₦{order['product_total_ngn']:,}")
    print(f"Delivery: ₦{order['delivery_fee_ngn']:,}")
    print("-----------------------------------------")
    print(f"TOTAL: ₦{order['order_total_ngn']:,}")
    print(f"Location: {order['delivery_location']}")
    print("=========================================\n")

    return order


def main():
    print(f"{APP_NAME} v{VERSION}")
    print("Sales engine ready.")

    # Test order
    create_order_summary(
        quantity=13,
        location="Ibadan"
    )


if __name__ == "__main__":
    main()
