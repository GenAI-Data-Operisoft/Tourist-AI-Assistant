# validators.py

def validate_same_flight(base: dict, new: dict):
    keys = ["pnr", "flightNumber"]

    for k in keys:
        if base.get(k) and new.get(k):
            if base[k] != new[k]:
                raise ValueError("Documents belong to different flights")
                
def get_flight_key(data: dict, doc_type: str) -> tuple:
    """
    Unique identifier for a booking based on document type
    """
    if doc_type in ["BOARDING_PASS", "INVOICE", "TICKET"]:
        # Try to get PNR from different possible locations
        pnr = data.get("pnr", "")
        
        # Try to get flight number from different structures
        flight_number = ""
        
        # Boarding pass structure
        if "flight" in data and isinstance(data["flight"], dict):
            carrier = data["flight"].get("carrier", "")
            flight_num = data["flight"].get("flight_number", "")
            flight_number = f"{carrier}{flight_num}" if carrier and flight_num else flight_num
        # Ticket/invoice structure
        elif "flight_number" in data:
            flight_number = data.get("flight_number", "")
        elif "segments" in data and isinstance(data["segments"], list) and len(data["segments"]) > 0:
            segment = data["segments"][0]
            carrier = segment.get("marketing_carrier", "")
            flight_num = segment.get("flight_number", "")
            flight_number = f"{carrier}{flight_num}" if carrier and flight_num else flight_num
        
        return (
            pnr.strip(),
            flight_number.strip(),
            "FLIGHT"
        )
    elif doc_type == "TRAIN_TICKET":
        # NEW train ticket structure
        ticket_ref = data.get("ticket_reference", "").strip()
        train_number = ""
        
        # Extract train number from journey object
        if "journey" in data and isinstance(data["journey"], dict):
            train_number = data["journey"].get("train_number", "").strip()
        
        return (
            ticket_ref,
            train_number,
            "TRAIN"
        )
    elif doc_type == "HOTEL_BOOKING":
        return (
            data.get("confirmation_number", "").strip(),
            data.get("hotel", {}).get("name", "").strip() if isinstance(data.get("hotel"), dict) else "",
            "HOTEL"
        )
    else:
        return ("", "", doc_type)
