# extractors/train_ticket.py
import json
from aws_clients import bedrock

def extract_train_ticket(text: str) -> dict:
    prompt = f"""
Extract train ticket fields as JSON.

Fields:
- passengerName
- pnr
- trainNumber
- trainName
- from
- to
- travelDate
- departureTime
- arrivalTime
- seatNumber
- coach
- class
- fare
- bookingDate

Missing → empty string.
No hallucination.

Text:
<<<{text}>>>
"""

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "temperature": 0,
        "max_tokens": 800,
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
