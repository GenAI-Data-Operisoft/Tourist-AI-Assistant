# main.py
import sys
from collections import defaultdict
from text_extraction import extract_text
from document_classifier import classify_document
from extractors.boarding_pass import extract_boarding_pass
from extractors.invoice import extract_invoice
from extractors.ticket import extract_ticket
from extractors.train_ticket import extract_train_ticket
from extractors.hotel_booking import extract_hotel_booking
from merger import merge_entities
from reasoning_agent import reason_about_extraction
import validators

EXTRACTOR_MAP = {
    "BOARDING_PASS": extract_boarding_pass,
    "INVOICE": extract_invoice,
    "TICKET": extract_ticket,
    "TRAIN_TICKET": extract_train_ticket,
    "HOTEL_BOOKING": extract_hotel_booking
}

def process_files(pdf_paths: list[str]) -> list[dict]:
    """
    Process multiple PDFs and return one merged output per flight
    """
    flight_groups = defaultdict(list)

    # 1️⃣ Extract + classify + extract entities + reasoning
    for pdf in pdf_paths:
        text, source = extract_text(pdf)
        doc_type = classify_document(text)

        if doc_type not in EXTRACTOR_MAP:
            continue

        data = EXTRACTOR_MAP[doc_type](text)
        
        # Apply reasoning agent
        reasoning = reason_about_extraction(data, doc_type, text)
        
        data["source"] = source
        data["documentType"] = doc_type
        data["reasoning"] = reasoning
        
        # Merge enriched data from reasoning agent
        if reasoning.get("enrichedData"):
            data.update(reasoning["enrichedData"])

        flight_key = validators.get_flight_key(data, doc_type)

        # Fallback for missing identifiers
        if not any(flight_key):
            flight_key = ("UNKNOWN", "UNKNOWN", doc_type)

        flight_groups[flight_key].append(data)

    # 2️⃣ Merge per booking/trip
    results = []

    for (identifier1, identifier2, booking_type), docs in flight_groups.items():
        # Get actual document type from first doc
        actual_doc_type = docs[0].get("documentType", "UNKNOWN") if docs else "UNKNOWN"
        
        merged = merge_entities(docs, actual_doc_type)

        # Set identity based on booking type
        if booking_type == "FLIGHT":
            merged["bookingIdentity"] = {
                "type": "FLIGHT",
                "pnr": identifier1,
                "flightNumber": identifier2
            }
        elif booking_type == "TRAIN":
            merged["bookingIdentity"] = {
                "type": "TRAIN",
                "pnr": identifier1,
                "trainNumber": identifier2
            }
        elif booking_type == "HOTEL":
            merged["bookingIdentity"] = {
                "type": "HOTEL",
                "bookingReference": identifier1,
                "hotelName": identifier2
            }
        else:
            merged["bookingIdentity"] = {
                "type": "UNKNOWN",
                "identifier1": identifier1,
                "identifier2": identifier2
            }

        merged["documentsUsed"] = [
            d.get("documentType") for d in docs
        ]
        
        # Aggregate reasoning insights
        all_issues = []
        all_suggestions = []
        avg_confidence = 0
        
        for doc in docs:
            if "reasoning" in doc:
                r = doc["reasoning"]
                all_issues.extend(r.get("issues", []))
                all_suggestions.extend(r.get("suggestions", []))
                avg_confidence += r.get("confidence", 0)
        
        if docs:
            avg_confidence = avg_confidence / len(docs)
        
        merged["reasoningInsights"] = {
            "averageConfidence": round(avg_confidence, 2),
            "issues": list(set(all_issues)),
            "suggestions": list(set(all_suggestions))
        }

        results.append(merged)

    return results


def process_uploaded_files(uploaded_files):
    # same behavior for Streamlit
    return process_files(uploaded_files)


if __name__ == "__main__":
    files = sys.argv[1:]
    outputs = process_files(files)
    for idx, out in enumerate(outputs, start=1):
        booking_type = out.get("bookingIdentity", {}).get("type", "UNKNOWN")
        print(f"\n--- {booking_type} Booking {idx} ---")
        print(out)
