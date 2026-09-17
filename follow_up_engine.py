from datetime import datetime
from uuid import uuid4


def create_follow_up(
    customer_id,
    follow_up_type,
    message,
    order_id="",
    consent_status="UNKNOWN"
):
    return {
        "follow_up_id": "FU-" + uuid4().hex[:8].upper(),
        "customer_id": customer_id,
        "order_id": order_id,
        "follow_up_type": follow_up_type,
        "message": message,
        "scheduled_at": datetime.utcnow().isoformat(),
        "completed_at": "",
        "status": "SCHEDULED",
        "customer_response": "",
        "consent_status": consent_status,
        "notes": ""
    }


def can_follow_up(consent_status):
    return consent_status is True


def prepare_follow_up(follow_up, consent_status):
    if not can_follow_up(consent_status):
        follow_up["status"] = "CANCELLED"
        follow_up["notes"] = (
            "Follow-up not permitted without customer consent."
        )
        return follow_up

    follow_up["consent_status"] = "CONSENTED"
    follow_up["status"] = "READY"

    return follow_up


def mark_follow_up_sent(follow_up):
    if follow_up["status"] != "READY":
        raise ValueError(
            "Follow-up must be READY before it can be sent."
        )

    follow_up["status"] = "SENT"

    return follow_up


def record_customer_response(
    follow_up,
    response
):
    follow_up["customer_response"] = response
    follow_up["status"] = "RESPONDED"

    return follow_up


def complete_follow_up(follow_up):
    follow_up["status"] = "COMPLETED"
    follow_up["completed_at"] = datetime.utcnow().isoformat()

    return follow_up


if __name__ == "__main__":

    follow_up = create_follow_up(
        customer_id="CUS-TEST001",
        order_id="ORD-TEST001",
        follow_up_type="PAYMENT_FOLLOW_UP",
        message=(
            "Hello. This is a follow-up regarding your "
            "SP-6 order. Please let us know if you need "
            "any assistance."
        ),
        consent_status=True
    )

    print("\n===== FOLLOW-UP CREATED =====")
    print(follow_up)

    follow_up = prepare_follow_up(
        follow_up,
        consent_status=True
    )

    print("\n===== FOLLOW-UP READY =====")
    print(follow_up)

    follow_up = mark_follow_up_sent(follow_up)

    print("\n===== FOLLOW-UP SENT =====")
    print(follow_up)

    follow_up = record_customer_response(
        follow_up,
        "I will complete the payment shortly."
    )

    print("\n===== CUSTOMER RESPONDED =====")
    print(follow_up)

    follow_up = complete_follow_up(follow_up)

    print("\n===== FOLLOW-UP COMPLETED =====")
    print(follow_up)
