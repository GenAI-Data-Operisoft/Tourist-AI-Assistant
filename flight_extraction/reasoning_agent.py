# reasoning_agent.py
import json
from aws_clients import bedrock

def reason_about_extraction(extracted_data: dict, document_type: str, original_text: str) -> dict:
    """
    LLM reasoning agent that validates, enriches, and provides insights about extracted data
    """
    prompt = f"""
You are a reasoning agent that validates and enriches travel document extraction.

Document Type: {document_type}
Extracted Data:
{json.dumps(extracted_data, indent=2)}

Original Text (first 1000 chars):
{original_text[:1000]}

Analyze the extraction and provide:
1. validation: Are all critical fields present? Any inconsistencies?
2. confidence: Rate extraction quality (0-100)
3. suggestions: Any missing or incorrect information?
4. enrichment: Add any useful derived information (e.g., duration, travel direction)
5. warnings: Any potential issues or anomalies

Return JSON with these keys:
- isValid (boolean)
- confidence (number 0-100)
- issues (list of strings)
- suggestions (list of strings)
- enrichedData (dict with additional computed fields)
- reasoning (string explaining your analysis)

Be concise and factual.
"""

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "temperature": 0.3,
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        resp = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        output = json.loads(resp["body"].read())
        reasoning_result = json.loads(output["content"][0]["text"])
        
        return reasoning_result
    except Exception as e:
        return {
            "isValid": True,
            "confidence": 50,
            "issues": [f"Reasoning agent error: {str(e)}"],
            "suggestions": [],
            "enrichedData": {},
            "reasoning": "Reasoning agent failed, using raw extraction"
        }
