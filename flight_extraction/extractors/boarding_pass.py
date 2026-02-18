# extractors/boarding_pass.py
import json
from aws_clients import bedrock

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
    "boarding_time": "YYYY-MM-DDTHH:MM:SS+TZ"
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
- Extract barcode data if visible
- Missing fields → empty string
- No hallucination
- Preserve exact values from boarding pass

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
