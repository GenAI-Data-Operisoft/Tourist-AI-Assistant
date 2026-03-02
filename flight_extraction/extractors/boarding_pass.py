# extractors/boarding_pass.py
from llm_config import LLMConfig

def extract_boarding_pass(text: str) -> dict:
    prompt = f"""
Extract boarding pass fields as JSON with the following EXACT structure:

{{
  "document_type": "boarding_pass",
  "pnr": "string",
  "ticket_number": "string",
  "passenger_name": "string (FIRST LAST format)",
  "flight": {{
    "carrier": "string (2-letter code)",
    "flight_number": "string",
    "date": "YYYY-MM-DD"
  }},
  "departure": {{
    "airport": "string (3-letter code)",
    "terminal": "string",
    "gate": "string",
    "boarding_date": "YYYY-MM-DD",
    "boarding_time_only": "HH:MM:SS",
    "timezone": "+TZ"
  }},
  "arrival": {{
    "airport": "string (3-letter code)"
  }},
  "seat": "string",
  "boarding_group": "string",
  "barcode": {{
    "format": "AZTEC/QR/PDF417",
    "raw_data": "string"
  }}
}}

Rules:
- Use EXACT structure shown above
- passenger_name should be "FIRST LAST" format (e.g., "RAHUL KUMAR")
- Use ISO 8601 format for boarding_time with timezone
- Split boarding_time into separate date, time, and timezone fields
- Extract barcode data if visible
- Missing fields → empty string or null
- No hallucination
- Preserve exact values from boarding pass

Text:
<<<{text}>>>
"""

    response_text = LLMConfig.call_llm(prompt, max_tokens=1200)
    return LLMConfig.extract_json(response_text)
