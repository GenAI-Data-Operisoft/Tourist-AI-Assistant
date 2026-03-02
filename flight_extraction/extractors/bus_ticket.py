# extractors/bus_ticket.py
from llm_config import LLMConfig

def extract_bus_ticket(text: str) -> dict:
    prompt = f"""Extract bus ticket fields as JSON with the following EXACT structure:

{{
  "document_type": "bus_ticket",
  "ticket_reference": "string",
  "issue_date": "YYYY-MM-DD",
  "provider": {{
    "name": "string",
    "contact_phone": "string"
  }},
  "passenger": {{
    "full_name": "string (FIRST LAST format)"
  }},
  "journey": {{
    "departure": {{
      "station_name": "string",
      "station_code": "string or null",
      "city": "string",
      "date": "YYYY-MM-DD",
      "time": "HH:MM:SS",
      "timezone": "+HH:MM or timezone abbreviation",
      "platform": "string or null"
    }},
    "arrival": {{
      "station_name": "string",
      "station_code": "string or null",
      "city": "string",
      "datetime_local": "YYYY-MM-DDTHH:MM:SS+TZ",
      "date": "YYYY-MM-DD",
      "time": "HH:MM:SS",
      "timezone": "+HH:MM or timezone abbreviation"
    }},
    "bus_details": {{
      "service_number": "string",
      "bus_type": "Coach|AC|Sleeper|Unknown"
    }}
  }},
  "seat": {{
    "seat_number": "string",
    "coach": "string or null"
  }},
  "fare": {{
    "currency": "string (3-letter code)",
    "amount": number
  }},
  "baggage": {{
    "included_kg": number,
    "notes": "string"
  }},
  "barcode": {{
    "format": "QR|PDF417|AZTEC|Unknown",
    "raw_data": "string or null"
  }},
  "policies": {{
    "refundability": "refundable|non_refundable|unknown",
    "changes_allowed": "yes|no|unknown"
  }}
}}

Rules:
- Use EXACT structure shown above
- passenger.full_name should be "FIRST LAST" format (e.g., "RAHUL KUMAR")
- For departure/arrival: keep datetime_local + add separate date, time, timezone fields
- Split datetime_local into: date (YYYY-MM-DD), time (HH:MM:SS), timezone (+07:00 or ICT)
- bus_type must be one of: Coach, AC, Sleeper, Unknown
- barcode.format must be one of: QR, PDF417, AZTEC, Unknown
- refundability must be one of: refundable, non_refundable, unknown
- changes_allowed must be one of: yes, no, unknown
- Missing fields → null or empty string
- No hallucination
- Preserve exact values from ticket

Text:
<<<
{text}
>>>"""

    response_text = LLMConfig.call_llm(prompt, max_tokens=1500)
    return LLMConfig.extract_json(response_text)
