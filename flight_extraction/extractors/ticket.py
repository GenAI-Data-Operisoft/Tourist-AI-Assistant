# extractors/ticket.py
import json
from aws_clients import bedrock

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
        "datetime_local": "YYYY-MM-DDTHH:MM:SS+TZ"
      }},
      "arrival": {{
        "airport": "string (3-letter code)",
        "terminal": "string",
        "datetime_local": "YYYY-MM-DDTHH:MM:SS+TZ"
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
- Missing fields → empty string or empty array
- No hallucination
- Preserve exact values from document

Text:
<<<{text}>>>
"""

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "temperature": 0,
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    }

    resp = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    output = json.loads(resp["body"].read())
    response_text = output["content"][0]["text"]
    
    # Extract JSON from response (handle markdown code blocks)
    try:
        # Try direct parsing first
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks or text
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # Try to find JSON object in text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        
        # If all fails, raise error with the actual response
        raise ValueError(f"Could not parse JSON from response: {response_text[:200]}")
