# extractors/hotel_booking.py
from llm_config import LLMConfig

def extract_hotel_booking(text: str) -> dict:
    prompt = f"""
Extract hotel booking/voucher fields as JSON with the following EXACT structure:

{{
  "document_type": "hotel_voucher",
  "confirmation_number": "string",
  "issue_date": "YYYY-MM-DD",
  "hotel": {{
    "name": "string",
    "address": "string (full address)",
    "street": "string (street address only)",
    "city": "string",
    "state": "string or null",
    "country": "string",
    "zip_code": "string or null",
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
- Split hotel address into: street, city, state, country, zip_code
- Keep full address in "address" field as well
- Extract check-in and check-out times separately if available
- Missing fields → null or empty string
- No hallucination
- Preserve exact values from document

Text:
<<<{text}>>>
"""

    response_text = LLMConfig.call_llm(prompt, max_tokens=1200)
    return LLMConfig.extract_json(response_text)
