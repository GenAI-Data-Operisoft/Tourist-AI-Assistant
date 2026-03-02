# extractors/train_ticket.py
from llm_config import LLMConfig

def extract_train_ticket(text: str) -> dict:
    prompt = f"""
Extract train ticket fields as JSON with the following EXACT structure:

{{
  "document_type": "train_ticket",
  "ticket_reference": "string",
  "issue_date": "YYYY-MM-DD",
  "operator": {{
    "name": "string",
    "country": "string (2-letter code)"
  }},
  "passengers": [
    {{
      "full_name": "string (FIRST LAST format)",
      "passenger_type": "adult|child|infant|senior|unknown",
      "id_number_masked": "string or null"
    }}
  ],
  "journey": {{
    "train_number": "string",
    "service_name": "string",
    "departure": {{
      "station_name": "string",
      "station_code": "string or null",
      "date": "YYYY-MM-DD",
      "time": "HH:MM:SS",
      "timezone": "+TZ",
      "platform": "string or null"
    }},
    "arrival": {{
      "station_name": "string",
      "station_code": "string or null",
      "date": "YYYY-MM-DD",
      "time": "HH:MM:SS",
      "timezone": "+TZ"
    }}
  }},
  "class": {{
    "travel_class": "1A|2A|2S|3A|unknown",
    "coach": "string or null"
  }},
  "seat_or_berth": {{
    "type": "seat|upper_berth|lower_berth|unknown",
    "number": "string or null"
  }},
  "fare": {{
    "currency": "string (3-letter code)",
    "amount": number
  }},
  "barcode": {{
    "format": "QR|PDF417|Unknown",
    "raw_data": "string or null"
  }},
  "policies": {{
    "refundability": "refundable|non_refundable|unknown",
    "changes_allowed": "yes|no|unknown"
  }}
}}

Rules:
- Use EXACT structure shown above
- full_name should be "FIRST LAST" format (e.g., "RAHUL KUMAR")
- Use ISO 8601 format for datetime_local with timezone
- Split datetime into separate date, time, and timezone fields
- passenger_type must be one of: adult, child, infant, senior, unknown
- travel_class must be one of: 1A, 2A, 2S, 3A, unknown
- seat_or_berth.type must be one of: seat, upper_berth, lower_berth, unknown
- Extract all passengers if multiple
- Missing fields → null or empty string
- No hallucination
- Preserve exact values from ticket

Text:
<<<{text}>>>
"""

    response_text = LLMConfig.call_llm(prompt, max_tokens=1500)
    return LLMConfig.extract_json(response_text)
