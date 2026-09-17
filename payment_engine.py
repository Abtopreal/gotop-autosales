import json
from pathlib import Path
from datetime import datetime
from uuid import uuid4

BASE_DIR = Path(__file__).parent


def load_payment_database():
    with open(
        BASE_DIR / "payments.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def create_payment_record(
    order_id,
    customer_id,
    amount_ngn,
    payment_reference=""
):
    now = datetime.utcnow().isoformat()

    return {
        "payment_id": "PAY-" + uuid4().hex[:8].upper(),
        "order_id": order_id,
        "customer_id": customer_id,
        "amount_ngn": amount_ngn,
        "payment_method": "BANK_TRANSFER",
        "bank": "First Bank PLC",
        "payment_reference": payment_reference,
        "payment_status": "PENDING",
        "verification_status": "NOT_VERIFIED",
        "payment_date": "",
        "verified_at": "",
        "notes": "",
        "created_at": now
    }


def customer_claimed_payment(payment_record):
    payment_record["payment_status"] = "CUSTOMER_CLAIMED_PAID"
    payment_record["verification_status"] = "PENDING_VERIFICATION"

    return payment_record


def verify_payment(payment_record, verified=False):

    if verified is True:
        now = datetime.utcnow().isoformat()

        payment_record["payment_status"] = "VERIFIED"
        payment_record["verification_status"] = "VERIFIED"
        payment_record["payment_date"] = now
        payment_record["verified_at"] = now

    else:
        payment_record["payment_status"] = "PENDING"
        payment_record["verification_status"] = "NOT_VERIFIED"

    return payment_record


def payment_is_verified(payment_record):
    return (
        payment_record.get("payment_status") == "VERIFIED"
        and
        payment_record.get("verification_status") == "VERIFIED"
    )


if __name__ == "__main__":

    payment = create_payment_record(
        order_id="ORD-TEST001",
        customer_id="CUS-TEST001",
        amount_ngn=83300,
        payment_reference="TEST-REFERENCE"
    )

    print("\n===== PAYMENT CREATED =====")
    print(payment)

    payment = customer_claimed_payment(payment)

    print("\n===== CUSTOMER CLAIMED PAID =====")
    print(payment)

    print("\nPayment verified?")
    print(payment_is_verified(payment))

    payment = verify_payment(
        payment,
        verified=True
    )

    print("\n===== PAYMENT VERIFIED =====")
    print(payment)

    print("\nPayment verified?")
    print(payment_is_verified(payment))
