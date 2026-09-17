import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent


def load_fulfilment_database():
    with open(
        BASE_DIR / "fulfilment.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def create_fulfilment(order_id, method):
    if method not in ["DELIVERY", "PICKUP"]:
        raise ValueError(
            "Fulfilment method must be DELIVERY or PICKUP."
        )

    return {
        "order_id": order_id,
        "fulfilment_method": method,
        "status": "NOT_STARTED",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "notes": ""
    }


def start_fulfilment(fulfilment_record, payment_verified):
    if not payment_verified:
        raise ValueError(
            "Fulfilment cannot begin until payment is verified."
        )

    fulfilment_record["status"] = "PROCESSING"
    fulfilment_record["updated_at"] = datetime.utcnow().isoformat()

    return fulfilment_record


def mark_ready(fulfilment_record):
    method = fulfilment_record["fulfilment_method"]

    if method == "DELIVERY":
        fulfilment_record["status"] = "READY_FOR_DELIVERY"

    elif method == "PICKUP":
        fulfilment_record["status"] = "READY_FOR_PICKUP"

    fulfilment_record["updated_at"] = datetime.utcnow().isoformat()

    return fulfilment_record


def dispatch_order(fulfilment_record):
    if fulfilment_record["fulfilment_method"] != "DELIVERY":
        raise ValueError(
            "Only delivery orders can be dispatched."
        )

    if fulfilment_record["status"] != "READY_FOR_DELIVERY":
        raise ValueError(
            "Order must be ready for delivery before dispatch."
        )

    fulfilment_record["status"] = "OUT_FOR_DELIVERY"
    fulfilment_record["updated_at"] = datetime.utcnow().isoformat()

    return fulfilment_record


def complete_fulfilment(fulfilment_record):
    allowed_statuses = [
        "OUT_FOR_DELIVERY",
        "READY_FOR_PICKUP"
    ]

    if fulfilment_record["status"] not in allowed_statuses:
        raise ValueError(
            "Order is not ready to be completed."
        )

    fulfilment_record["status"] = "COMPLETED"
    fulfilment_record["updated_at"] = datetime.utcnow().isoformat()

    return fulfilment_record


if __name__ == "__main__":

    fulfilment = create_fulfilment(
        order_id="ORD-TEST001",
        method="DELIVERY"
    )

    print("\n===== FULFILMENT CREATED =====")
    print(fulfilment)

    fulfilment = start_fulfilment(
        fulfilment,
        payment_verified=True
    )

    print("\n===== PROCESSING =====")
    print(fulfilment)

    fulfilment = mark_ready(fulfilment)

    print("\n===== READY FOR DELIVERY =====")
    print(fulfilment)

    fulfilment = dispatch_order(fulfilment)

    print("\n===== OUT FOR DELIVERY =====")
    print(fulfilment)

    fulfilment = complete_fulfilment(fulfilment)

    print("\n===== COMPLETED =====")
    print(fulfilment)
