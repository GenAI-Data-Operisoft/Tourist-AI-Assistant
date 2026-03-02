# extractors/ticket.py
from llm_config import LLMConfig

def extract_ticket(text: str) -> dict:
    prompt = f"""
Extract flight ticket/itinerary fields as JSON with the following structure:

{{
  "document_type": "flight_itinerary",
  "pnr": "string",
  "issue_date": "YYYY-MM-DD",
  "issuing_carrier": "string (2-letter code)",
  "booking_source": "string",
  "passengers": [
    {{
      "title": "MR/MS/MRS",
      "first_name": "string",
      "last_name": "string",
      "ticket_number": "string",
      "frequent_flyer": {{
        "program": "string",
        "number_masked": "string"
      }}
    }}
  ],
  "segments": [
    {{
      "segment_number": 1,
      "marketing_carrier": "string (2-letter code)",
      "operating_carrier": "string (2-letter code)",
      "flight_number": "string",
      "aircraft": "string",
      "cabin_class": "Economy/Business/First",
      "booking_class": "string (1 letter)",
      "departure": {{
        "airport": "string (3-letter code)",
        "terminal": "string",
        "date": "YYYY-MM-DD",
        "time": "HH:MM:SS",
        "timezone": "+TZ"
      }},
      "arrival": {{
        "airport": "string (3-letter code)",
        "terminal": "string",
        "date": "YYYY-MM-DD",
        "time": "HH:MM:SS",
        "timezone": "+TZ"
      }},
      "baggage_allowance": {{
        "checked": "string (e.g., 1PC, 2PC)",
        "weight_kg": number,
        "cabin_kg": number
      }},
      "seat": "string",
      "special_services": ["string"]
    }}
  ],
  "fare": {{
    "currency": "string (3-letter code)",
    "total_amount": number,
    "fare_basis": "string",
    "refundable": boolean
  }}
}}

Rules:
- Extract all passengers if multiple
- Extract all flight segments if multi-leg journey
- Use ISO 8601 format for dates/times with timezone
- Split datetime_local into separate date, time, and timezone fields
- Missing fields → empty string or empty array or null
- No hallucination
- Preserve exact values from document

Text:
<<<{text}>>>
"""

    response_text = LLMConfig.call_llm(prompt, max_tokens=2000)
    return LLMConfig.extract_json(response_text)
