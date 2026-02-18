# extractors/hotel_booking.py
import json
from aws_clients import bedrock
import re

def extract_hotel_booking(text: str) -> dict:
    prompt = f"""
Extract hotel booking/voucher fields as JSON with the following EXACT structure:

{{
  "document_type": "hotel_voucher",
  "confirmation_number": "string",
  "issue_date": "YYYY-MM-DD",
  "hotel": {{
    "name": "string",
    "address": "string",
    "phone": "string"
  }},
  "guest": {{
    "full_name": "string (FIRST LAST format)"
  }},
  "stay": {{
    "check_in": "YYYY-MM-DD",
    "check_out": "YYYY-MM-DD",
    "nights": number
  }},
  "room": {{
    "room_type": "string",
    "occupancy": number,
    "meal_plan": "string"
  }},
  "rate": {{
    "currency": "string (3-letter code)",
    "total_amount": number,
    "payment_type": "Prepaid/Pay at Hotel/etc"
  }},
  "cancellation_policy": "string"
}}

Rules:
- Use EXACT structure shown above
- guest.full_name should be "FIRST LAST" format
- Calculate nights from check_in and check_out dates
- Extract complete hotel address
- Missing fields → empty string or 0 for numbers
- No hallucination
- Preserve exact values from document

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
    print(f"output : {output}")
    output_text = output["content"][0]["text"]
    match = re.search(r'\{[\s\S]*\}', output_text)

    if match:
        json_data = match.group()
        print(json_data)
        return json.loads(json_data)
    
    return {}
