# Unified JSON Structure for Flight Documents

## Overview

All flight-related documents (tickets, boarding passes, and invoices) now use the **SAME unified structure** for consistency and easier merging.

## Unified Structure

```json
{
  "document_type": "flight_itinerary|boarding_pass|flight_invoice",
  "pnr": "ABC123",
  "issue_date": "2026-01-31",
  "issuing_carrier": "EK",
  "booking_source": "Emirates",
  "passengers": [
    {
      "title": "MR",
      "first_name": "RAHUL",
      "last_name": "KUMAR",
      "ticket_number": "1761234567890",
      "frequent_flyer": {
        "program": "Skywards",
        "number_masked": "****7890"
      }
    }
  ],
  "segments": [
    {
      "segment_number": 1,
      "marketing_carrier": "EK",
      "operating_carrier": "EK",
      "flight_number": "372",
      "aircraft": "B777-300ER",
      "cabin_class": "Economy",
      "booking_class": "M",
      "departure": {
        "airport": "DXB",
        "terminal": "3",
        "gate": "A12",
        "datetime_local": "2026-02-10T03:10:00+04:00"
      },
      "arrival": {
        "airport": "BKK",
        "terminal": "1",
        "datetime_local": "2026-02-10T12:20:00+07:00"
      },
      "baggage_allowance": {
        "checked": "1PC",
        "weight_kg": 23,
        "cabin_kg": 7
      },
      "seat": "22A",
      "special_services": ["VGML"]
    }
  ],
  "fare": {
    "currency": "AED",
    "total_amount": 2450.75,
    "fare_basis": "MSAVER",
    "refundable": false
  }
}
```

## Document Type Differences

### Flight Ticket (flight_itinerary)
- **Complete information** about the booking
- All fields populated
- Multiple segments for connecting flights
- Complete fare breakdown
- Passenger ticket numbers

### Boarding Pass (boarding_pass)
- **Same structure** as ticket
- Focus on boarding details:
  - `departure.gate` - Gate number
  - `seat` - Seat assignment
  - Times are precise
- Fare section may be minimal or empty
- Usually single segment (current flight)

### Flight Invoice (flight_invoice)
- **Same structure** as ticket
- Additional payment fields (handled separately)
- Complete fare breakdown with taxes
- May have limited flight details

## Benefits of Unified Structure

### 1. Easy Merging
When you have ticket + boarding pass + invoice:
```javascript
// All use same structure
ticket.segments[0] + boardingPass.segments[0] = merged segment with gate info
```

### 2. Consistent Access
```javascript
// Same code works for all document types
document.passengers[0].first_name
document.segments[0].departure.airport
document.fare.total_amount
```

### 3. Simplified Validation
```javascript
// One validation schema for all
validateFlightDocument(document)
```

## Merging Example

### Input Documents

**Ticket:**
```json
{
  "document_type": "flight_itinerary",
  "pnr": "ABC123",
  "passengers": [{"first_name": "RAHUL", "last_name": "KUMAR"}],
  "segments": [{
    "flight_number": "372",
    "departure": {"airport": "DXB", "terminal": "3"},
    "seat": "22A"
  }],
  "fare": {"total_amount": 2450.75}
}
```

**Boarding Pass:**
```json
{
  "document_type": "boarding_pass",
  "pnr": "ABC123",
  "passengers": [{"first_name": "RAHUL", "last_name": "KUMAR"}],
  "segments": [{
    "flight_number": "372",
    "departure": {"airport": "DXB", "terminal": "3", "gate": "A12"},
    "seat": "22A"
  }]
}
```

### Merged Output

```json
{
  "document_type": "flight_booking",
  "pnr": "ABC123",
  "passengers": [{"first_name": "RAHUL", "last_name": "KUMAR"}],
  "segments": [{
    "flight_number": "372",
    "departure": {
      "airport": "DXB",
      "terminal": "3",
      "gate": "A12"  // ← Added from boarding pass
    },
    "seat": "22A"
  }],
  "fare": {"total_amount": 2450.75}
}
```

## Field Population by Document Type

| Field | Ticket | Boarding Pass | Invoice |
|-------|--------|---------------|---------|
| pnr | ✅ Always | ✅ Always | ✅ Always |
| issue_date | ✅ Always | ⚠️ Sometimes | ✅ Always |
| issuing_carrier | ✅ Always | ⚠️ Sometimes | ✅ Always |
| booking_source | ✅ Always | ⚠️ Sometimes | ⚠️ Sometimes |
| passengers | ✅ Full details | ✅ Full details | ✅ Basic info |
| segments | ✅ All segments | ✅ Current flight | ⚠️ Basic info |
| segments.gate | ❌ Usually empty | ✅ Always | ❌ Empty |
| segments.seat | ✅ Usually | ✅ Always | ❌ Empty |
| segments.aircraft | ✅ Usually | ⚠️ Sometimes | ❌ Empty |
| fare | ✅ Complete | ⚠️ Minimal | ✅ Complete |

## Code Examples

### Extracting from Any Document
```python
# Same extraction logic for all types
data = extract_document(text)

# Access fields consistently
pnr = data.get("pnr")
passenger_name = data["passengers"][0]["first_name"]
departure_airport = data["segments"][0]["departure"]["airport"]
```

### Merging Documents
```python
# Merge ticket + boarding pass
merged = merge_flight_entities([ticket_data, boarding_pass_data])

# Result has:
# - Passenger info from both
# - Segments with gate from boarding pass
# - Fare from ticket
```

### Frontend Display
```jsx
// Same component for all document types
{document.segments.map(segment => (
  <div>
    <p>Flight: {segment.flight_number}</p>
    <p>From: {segment.departure.airport}</p>
    <p>Gate: {segment.departure.gate || 'TBA'}</p>
    <p>Seat: {segment.seat}</p>
  </div>
))}
```

## Migration Notes

### Old Structure (Boarding Pass)
```json
{
  "passenger": {"name": "RAHUL KUMAR"},
  "flight": {"from": "DXB", "to": "BKK"},
  "seat": {"number": "22A"}
}
```

### New Structure (Boarding Pass)
```json
{
  "passengers": [{"first_name": "RAHUL", "last_name": "KUMAR"}],
  "segments": [{
    "departure": {"airport": "DXB"},
    "arrival": {"airport": "BKK"},
    "seat": "22A"
  }]
}
```

## Validation Rules

All documents must have:
1. `document_type` - One of: flight_itinerary, boarding_pass, flight_invoice
2. `pnr` - Booking reference
3. `passengers` - Array with at least one passenger
4. `segments` - Array with at least one segment

Optional but recommended:
- `issue_date`
- `issuing_carrier`
- `fare` (can be empty for boarding passes)

## Summary

✅ **One structure for all flight documents**
✅ **Easy to merge multiple documents**
✅ **Consistent field access**
✅ **Simplified validation**
✅ **Better data quality**
