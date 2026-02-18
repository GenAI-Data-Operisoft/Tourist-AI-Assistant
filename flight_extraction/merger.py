# merger.py
def merge_entities(entities: list[dict], doc_type: str) -> dict:
    """
    Merge entities based on document type
    """
    if doc_type in ["BOARDING_PASS", "INVOICE", "TICKET"]:
        return _merge_flight_entities(entities)
    elif doc_type == "TRAIN_TICKET":
        return _merge_train_entities(entities)
    elif doc_type == "HOTEL_BOOKING":
        return _merge_hotel_entities(entities)
    else:
        # Fallback: return raw merged data
        return _merge_generic_entities(entities)

def _merge_generic_entities(entities: list[dict]) -> dict:
    """
    Generic merger for unknown document types
    """
    final = {}
    for e in entities:
        for k, v in e.items():
            if v and k not in ["source", "documentType", "reasoning"]:
                final[k] = v
    return final

# merger.py
def merge_entities(entities: list[dict], doc_type: str) -> dict:
    """
    Merge entities based on document type
    """
    if doc_type in ["BOARDING_PASS", "INVOICE", "TICKET"]:
        return _merge_flight_entities(entities)
    elif doc_type == "TRAIN_TICKET":
        return _merge_train_entities(entities)
    elif doc_type == "HOTEL_BOOKING":
        return _merge_hotel_entities(entities)
    else:
        # Fallback: return raw merged data
        return _merge_generic_entities(entities)

def _deep_merge(base: dict, update: dict) -> dict:
    """Deep merge two dictionaries"""
    result = base.copy()
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        elif value:  # Only update if value is not empty
            result[key] = value
    return result

def _merge_flight_entities(entities: list[dict]) -> dict:
    """Merge flight-related documents (ticket, boarding pass, invoice)"""
    final = {
        "document_type": "flight_booking",
        "pnr": "",
        "issue_date": "",
        "issuing_carrier": "",
        "booking_source": "",
        "passengers": [],
        "segments": [],
        "fare": {},
        "payment": {},
        "boarding_passes": []
    }

    # Track unique passengers by last name + first name
    passenger_keys = set()

    for e in entities:
        doc_type = e.get("document_type", "")
        
        # Merge PNR (highest priority field)
        if e.get("pnr") and not final["pnr"]:
            final["pnr"] = e["pnr"]
        
        # Handle boarding pass (different structure)
        if doc_type == "boarding_pass":
            # Store boarding pass separately
            final["boarding_passes"].append(e)
            
            # Extract passenger name and add to passengers list
            if e.get("passenger_name"):
                name_parts = e["passenger_name"].split(" ", 1)
                passenger = {
                    "first_name": name_parts[0] if len(name_parts) > 0 else "",
                    "last_name": name_parts[1] if len(name_parts) > 1 else "",
                    "ticket_number": e.get("ticket_number", "")
                }
                passenger_key = f"{passenger['last_name']}_{passenger['first_name']}"
                if passenger_key not in passenger_keys:
                    passenger_keys.add(passenger_key)
                    final["passengers"].append(passenger)
            
            # Add flight info to segments if not already there
            if e.get("flight"):
                flight = e["flight"]
                segment = {
                    "segment_number": 1,
                    "marketing_carrier": flight.get("carrier", ""),
                    "operating_carrier": flight.get("carrier", ""),
                    "flight_number": flight.get("flight_number", ""),
                    "departure": e.get("departure", {}),
                    "arrival": e.get("arrival", {}),
                    "seat": e.get("seat", "")
                }
                
                # Check if segment exists
                segment_exists = any(
                    s.get("flight_number") == segment["flight_number"]
                    for s in final["segments"]
                )
                
                if not segment_exists:
                    final["segments"].append(segment)
                else:
                    # Update existing segment with boarding pass info
                    for idx, s in enumerate(final["segments"]):
                        if s.get("flight_number") == segment["flight_number"]:
                            # Add gate and boarding time from boarding pass
                            if segment.get("departure"):
                                if not s.get("departure"):
                                    s["departure"] = {}
                                s["departure"] = _deep_merge(s["departure"], segment["departure"])
                            if segment.get("seat"):
                                s["seat"] = segment["seat"]
                            final["segments"][idx] = s
            
            continue
        
        # Handle ticket and invoice (same structure)
        # Merge issue date
        if e.get("issue_date") and not final["issue_date"]:
            final["issue_date"] = e["issue_date"]
        
        # Merge issuing carrier
        if e.get("issuing_carrier") and not final["issuing_carrier"]:
            final["issuing_carrier"] = e["issuing_carrier"]
        
        # Merge booking source
        if e.get("booking_source") and not final["booking_source"]:
            final["booking_source"] = e["booking_source"]
        
        # Merge passengers (avoid duplicates)
        if e.get("passengers"):
            for passenger in e["passengers"]:
                passenger_key = f"{passenger.get('last_name', '')}_{passenger.get('first_name', '')}"
                if passenger_key not in passenger_keys:
                    passenger_keys.add(passenger_key)
                    final["passengers"].append(passenger)
        
        # Merge segments
        if e.get("segments"):
            for segment in e["segments"]:
                # Check if segment already exists
                segment_exists = any(
                    s.get("segment_number") == segment.get("segment_number") and
                    s.get("flight_number") == segment.get("flight_number")
                    for s in final["segments"]
                )
                
                if not segment_exists:
                    final["segments"].append(segment)
                else:
                    # Update existing segment with additional info
                    for idx, s in enumerate(final["segments"]):
                        if (s.get("segment_number") == segment.get("segment_number") and
                            s.get("flight_number") == segment.get("flight_number")):
                            # Deep merge the segment
                            final["segments"][idx] = _deep_merge(s, segment)
        
        # Merge fare information
        if e.get("fare"):
            final["fare"] = _deep_merge(final["fare"], e["fare"])
        
        # Handle invoice-specific fields
        if doc_type == "flight_invoice":
            if e.get("invoice_number"):
                final["payment"]["invoice_number"] = e["invoice_number"]
            if e.get("invoice_date"):
                final["payment"]["invoice_date"] = e["invoice_date"]
            if e.get("payment"):
                final["payment"] = _deep_merge(final["payment"], e["payment"])
            if e.get("tax_details"):
                final["payment"]["tax_details"] = e["tax_details"]

    # Clean up empty fields
    final = {k: v for k, v in final.items() if v or k == "fare"}  # Keep fare even if empty
    
    return final

def _merge_train_entities(entities: list[dict]) -> dict:
    final = {
        "passenger": {},
        "train": {},
        "seat": {},
        "payment": {}
    }

    for e in entities:
        for k in e:
            if e[k]:
                if k in ["seatNumber", "coach", "class"]:
                    final["seat"][k] = e[k]
                elif k in ["fare", "bookingDate"]:
                    final["payment"][k] = e[k]
                elif k in ["pnr", "trainNumber", "trainName", "from", "to", "travelDate", "departureTime", "arrivalTime"]:
                    final["train"][k] = e[k]
                elif k == "passengerName":
                    final["passenger"]["name"] = e[k]

    return final

def _merge_hotel_entities(entities: list[dict]) -> dict:
    """Merge hotel booking documents"""
    final = {
        "document_type": "hotel_booking",
        "confirmation_number": "",
        "issue_date": "",
        "hotel": {},
        "guest": {},
        "stay": {},
        "room": {},
        "rate": {},
        "cancellation_policy": ""
    }

    for e in entities:
        # Merge confirmation number
        if e.get("confirmation_number") and not final["confirmation_number"]:
            final["confirmation_number"] = e["confirmation_number"]
        
        # Merge issue date
        if e.get("issue_date") and not final["issue_date"]:
            final["issue_date"] = e["issue_date"]
        
        # Merge hotel info
        if e.get("hotel"):
            final["hotel"] = _deep_merge(final["hotel"], e["hotel"])
        
        # Merge guest info
        if e.get("guest"):
            final["guest"] = _deep_merge(final["guest"], e["guest"])
        
        # Merge stay info
        if e.get("stay"):
            final["stay"] = _deep_merge(final["stay"], e["stay"])
        
        # Merge room info
        if e.get("room"):
            final["room"] = _deep_merge(final["room"], e["room"])
        
        # Merge rate info
        if e.get("rate"):
            final["rate"] = _deep_merge(final["rate"], e["rate"])
        
        # Merge cancellation policy
        if e.get("cancellation_policy") and not final["cancellation_policy"]:
            final["cancellation_policy"] = e["cancellation_policy"]

    # Clean up empty fields
    # final = {k: v for k, v in final.items() if v}
    
    return final
