from conversation_engine import handle_customer_message
from customer_engine import create_customer
from order_engine import create_order
from payment_engine import create_payment_record
from fulfilment_engine import create_fulfilment
from follow_up_engine import create_follow_up


class GotopAutoSalesAgent:

    def __init__(self):
        self.name = "GOTOP AUTOSALES"
        self.version = "1.0"

    def receive_message(
        self,
        message,
        name="",
        phone="",
        location="",
        customer_type="INDIVIDUAL",
        quantity=0,
        source="UNKNOWN",
        consent_to_follow_up=False
    ):

        # 1. Understand the customer's message
        conversation = handle_customer_message(message)

        # 2. Create customer record
        customer = create_customer(
            name=name,
            phone=phone,
            location=location,
            customer_type=customer_type,
            message=message,
            quantity_interest=quantity,
            source=source,
            consent_to_follow_up=consent_to_follow_up
        )

        result = {
            "customer": customer,
            "conversation": conversation
        }

        # 3. Create order when quantity and location are available
        if quantity > 0 and location:

            order = create_order(
                quantity=quantity,
                location=location,
                customer_id=customer["customer_id"]
            )

            result["order"] = order

            # 4. Create payment record
            payment = create_payment_record(
                order_id=order["order_id"],
                customer_id=customer["customer_id"],
                amount_ngn=order["order_total_ngn"]
            )

            result["payment"] = payment

        return result

    def prepare_fulfilment(
        self,
        order_id,
        payment_verified,
        method
    ):

        fulfilment = create_fulfilment(
            order_id=order_id,
            method=method
        )

        if not payment_verified:
            return {
                "success": False,
                "message": (
                    "Fulfilment cannot begin until "
                    "payment is verified."
                ),
                "fulfilment": fulfilment
            }

        return {
            "success": True,
            "message": "Payment verified. Fulfilment may begin.",
            "fulfilment": fulfilment
        }

    def create_customer_follow_up(
        self,
        customer_id,
        message,
        consent_status
    ):

        return create_follow_up(
            customer_id=customer_id,
            follow_up_type="POST_PURCHASE_FOLLOW_UP",
            message=message,
            consent_status=consent_status
        )


if __name__ == "__main__":

    agent = GotopAutoSalesAgent()

    result = agent.receive_message(
        message="I want to buy 10 tubes",
        name="Test Customer",
        phone="",
        location="Ibadan",
        customer_type="INDIVIDUAL",
        quantity=10,
        source="WHATSAPP",
        consent_to_follow_up=True
    )

    print("\n====================================")
    print("      GOTOP AUTOSALES AGENT")
    print("====================================")

    print("\nCUSTOMER")
    print(result["customer"])

    print("\nCONVERSATION")
    print(result["conversation"])

    print("\nORDER")
    print(result["order"])

    print("\nPAYMENT")
    print(result["payment"])

    print("\n====================================")
