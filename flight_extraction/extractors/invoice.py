# extractors/invoice.py
import json
from aws_clients import bedrock

def extract_invoice(text: str) -> dict:
    prompt = f"""
Extract flight invoice/receipt fields as JSON with the following structure:

{{
  "document_type": "flight_invoice",
  "invoice_number": "string",
  "invoice_date": "YYYY-MM-DD",
  "pnr": "string",
  "issuing_carrier": "string",
  "passenger": {{
    "title": "MR/MS/MRS",
    "first_name": "string",
    "last_name": "string"
  }},
  "flight": {{
    "carrier": "string (2-letter code)",
    "flight_number": "string",
    "route": "string (e.g., DXB-BKK)",
    "date": "YYYY-MM-DD"
  }},
  "fare": {{
    "currency": "string (3-letter code)",
    "base_fare": number,
    "taxes": number,
    "fees": number,
    "total_amount": number
  }},
  "payment": {{
    "method": "string (Credit Card/Debit Card/etc)",
    "card_last4": "string",
    "transaction_id": "string"
  }},
  "tax_details": {{
    "gstin": "string",
    "tax_amount": number
  }}
}}

Rules:
- Extract all fare breakdown if available
- Use ISO date format (YYYY-MM-DD)
- Missing fields → empty string or 0 for numbers
- No hallucination

Text:
<<<{text}>>>
"""

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "temperature": 0,
        "max_tokens": 1200,
        "messages": [{"role": "user", "content": prompt}]
    }

    resp = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    output = json.loads(resp["body"].read())
    return json.loads(output["content"][0]["text"])
