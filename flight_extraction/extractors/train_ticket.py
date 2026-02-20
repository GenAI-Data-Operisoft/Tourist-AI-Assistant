# extractors/train_ticket.py
import json
from aws_clients import bedrock

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
      "datetime_local": "YYYY-MM-DDTHH:MM:SS+TZ",
      "platform": "string or null"
    }},
    "arrival": {{
      "station_name": "string",
      "station_code": "string or null",
      "datetime_local": "YYYY-MM-DDTHH:MM:SS+TZ"
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

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "temperature": 0,
        "max_tokens": 1500,
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

