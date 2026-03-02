# document_classifier.py
import json
import re
from aws_clients import bedrock

ALLOWED_TYPES = {"BOARDING_PASS", "INVOICE", "TICKET", "TRAIN_TICKET", "HOTEL_BOOKING", "BUS_TICKET", "UNKNOWN"}

def _safe_json_extract(text: str) -> dict:
    """Extract the first JSON object found in text.
    Returns {} if none found or invalid."""
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return {}

def classify_document(text: str) -> str:
    prompt = f"""You are a document classification system.

Classify the document into EXACTLY one of:
- BOARDING_PASS (flight boarding pass)
- INVOICE (flight invoice/receipt)
- TICKET (flight ticket)
- TRAIN_TICKET (train/railway ticket or reservation)
- BUS_TICKET (bus ticket or coach reservation)
- HOTEL_BOOKING (hotel booking confirmation)
- UNKNOWN

Rules:
- Output MUST be valid JSON
- Use key: documentType
- No markdown
- No explanation

Example:
{{"documentType":"INVOICE"}}

Text:
<<<
{text}
>>>"""

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "temperature": 0,
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )

    raw = json.loads(response["body"].read())
    model_text = raw["content"][0]["text"]
    parsed = _safe_json_extract(model_text)
    doc_type = parsed.get("documentType", "UNKNOWN")

    if doc_type not in ALLOWED_TYPES:
        return "UNKNOWN"

    return doc_type
