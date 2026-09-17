import os
from openai import OpenAI

MODEL = "gpt-5.6-luna"


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return OpenAI(api_key=api_key)


def generate_sales_response(
    customer_message,
    sales_brain,
    product_information
):
    client = get_client()

    instructions = f"""
You are GOTOP AUTOSALES, an AI-powered sales agent.

Follow the sales rules below exactly.

SALES AGENT BRAIN:
{sales_brain}

PRODUCT INFORMATION:
{product_information}

IMPORTANT RULES:
- Never invent product information.
- Never invent prices.
- Never invent discounts.
- Never invent stock levels.
- Never claim that payment has been verified unless the system confirms it.
- Never invent delivery or fulfilment status.
- Never make unsupported medical claims.
- Be clear, professional and helpful.
- Ask for missing information when necessary.
- Do not pressure the customer.
- Distinguish confirmed information from information that still requires verification.
"""

    response = client.responses.create(
        model=MODEL,
        instructions=instructions,
        input=customer_message
    )

    return response.output_text


if __name__ == "__main__":

    sales_brain = """
The agent helps customers understand products,
qualify their needs, place orders, handle payment
information accurately, and support fulfilment.
"""

    product_information = """
Product: SP-6 Advanced Oral Care
Current price: ₦7,000 per tube
Bulk offer: 10 or more tubes receive 10% off
Bulk price: ₦6,300 per tube
"""

    message = "How much is SP-6?"

    answer = generate_sales_response(
        customer_message=message,
        sales_brain=sales_brain,
        product_information=product_information
    )

    print("\n===== GOTOP AUTOSALES AI =====")
    print(answer)
    print("==============================")
