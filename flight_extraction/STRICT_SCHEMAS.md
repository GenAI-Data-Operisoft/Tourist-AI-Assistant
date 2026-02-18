# Strict JSON Schemas - DO NOT DEVIATE

## ⚠️ CRITICAL: Exact Structure Requirements

Each document type MUST produce the EXACT JSON structure specified below. No variations allowed.

---

## 1. Flight Ticket (flight_itinerary)

### EXACT Structure
```json
{
  "document_type": "flight_itinerary",
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

### Required Fields
- ✅ `document_type` = "flight_itinerary"
- ✅ `pnr` (string)
- ✅ `passengers` (array of objects)
- ✅ `segments` (array of objects)
- ✅ `fare` (object)

### Optional Fields
- `issue_date`, `issuing_carrier`, `booking_source`

---

## 2. Boarding Pass (boarding_pass)

### EXACT Structure
```json
{
  "document_type": "boarding_pass",
  "pnr": "ABC123",
  "ticket_number": "1761234567890",
  "passenger_name": "RAHUL KUMAR",
  "flight": {
    "carrier": "EK",
    "flight_number": "372",
    "date": "2026-02-10"
  },
  "departure": {
    "airport": "DXB",
    "terminal": "3",
    "gate": "A12",
    "boarding_time": "2026-02-10T02:30:00+04:00"
  },
  "arrival": {
    "airport": "BKK"
  },
  "seat": "22A",
  "boarding_group": "2",
  "barcode": {
    "format": "AZTEC",
    "raw_data": "M1KUMAR/RAHUL..."
  }
}
```

### Required Fields
- ✅ `document_type` = "boarding_pass"
- ✅ `pnr` (string)
- ✅ `passenger_name` (string, NOT object)
- ✅ `flight` (object)
- ✅ `departure` (object)
- ✅ `arrival` (object)
- ✅ `seat` (string)

### Optional Fields
- `ticket_number`, `boarding_group`, `barcode`

---

## 3. Flight Invoice (flight_invoice)

### EXACT Structure
```json
{
  "document_type": "flight_invoice",
  "invoice_number": "INV-2026-001234",
  "invoice_date": "2026-01-31",
  "pnr": "ABC123",
  "issuing_carrier": "EK",
  "passenger": {
    "title": "MR",
    "first_name": "RAHUL",
    "last_name": "KUMAR"
  },
  "flight": {
    "carrier": "EK",
    "flight_number": "372",
    "route": "DXB-BKK",
    "date": "2026-02-10"
  },
  "fare": {
    "currency": "AED",
    "base_fare": 1850.00,
    "taxes": 450.75,
    "fees": 150.00,
    "total_amount": 2450.75
  },
  "payment": {
    "method": "Credit Card",
    "card_last4": "1234",
    "transaction_id": "TXN123456789"
  },
  "tax_details": {
    "gstin": "29ABCDE1234F1Z5",
    "tax_amount": 450.75
  }
}
```

### Required Fields
- ✅ `document_type` = "flight_invoice"
- ✅ `invoice_number` (string)
- ✅ `pnr` (string)
- ✅ `passenger` (object, NOT array)
- ✅ `fare` (object)

### Optional Fields
- `invoice_date`, `issuing_carrier`, `flight`, `payment`, `tax_details`

---

## 4. Hotel Voucher (hotel_voucher)

### EXACT Structure
```json
{
  "document_type": "hotel_voucher",
  "confirmation_number": "H12345678",
  "issue_date": "2026-01-31",
  "hotel": {
    "name": "Hotel Example Bangkok",
    "address": "123 ถนนสุขุมวิท Bangkok",
    "phone": "+66 2 123 4567"
  },
  "guest": {
    "full_name": "RAHUL KUMAR"
  },
  "stay": {
    "check_in": "2026-02-10",
    "check_out": "2026-02-15",
    "nights": 5
  },
  "room": {
    "room_type": "Deluxe King",
    "occupancy": 2,
    "meal_plan": "Breakfast"
  },
  "rate": {
    "currency": "THB",
    "total_amount": 18000,
    "payment_type": "Prepaid"
  },
  "cancellation_policy": "Free cancellation until 48 hours before check-in"
}
```

### Required Fields
- ✅ `document_type` = "hotel_voucher"
- ✅ `confirmation_number` (string)
- ✅ `hotel` (object)
- ✅ `guest` (object with `full_name`)
- ✅ `stay` (object)
- ✅ `room` (object)
- ✅ `rate` (object)

### Optional Fields
- `issue_date`, `cancellation_policy`

---

## Common Rules for ALL Documents

### 1. Field Names
- ❌ NO camelCase variations (e.g., `passengerName`)
- ✅ ONLY use exact field names as specified
- ❌ NO additional fields not in schema
- ❌ NO renaming of fields

### 2. Data Types
- Strings: Use `""` for empty values
- Numbers: Use `0` for missing numeric values
- Arrays: Use `[]` for empty arrays
- Objects: Use `{}` for empty objects
- Booleans: Use `true` or `false` (lowercase)

### 3. Date/Time Formats
- Date only: `YYYY-MM-DD` (e.g., "2026-02-10")
- DateTime with timezone: `YYYY-MM-DDTHH:MM:SS+TZ` (e.g., "2026-02-10T03:10:00+04:00")

### 4. Code Formats
- Airport codes: 3 letters (e.g., "DXB", "BKK")
- Airline codes: 2 letters (e.g., "EK", "AI")
- Currency codes: 3 letters (e.g., "AED", "USD", "THB")

### 5. Name Formats
- **Flight Ticket**: Separate `first_name` and `last_name`
- **Boarding Pass**: Combined `passenger_name` as "FIRST LAST"
- **Invoice**: Separate `first_name` and `last_name`
- **Hotel**: Combined `full_name` as "FIRST LAST"

---

## Validation Checklist

Before returning JSON, verify:

- [ ] `document_type` field is present and correct
- [ ] All required fields are present
- [ ] Field names match EXACTLY (case-sensitive)
- [ ] Data types are correct (string/number/boolean/array/object)
- [ ] No extra fields added
- [ ] Date formats are correct
- [ ] Passenger/guest name format matches document type
- [ ] Arrays are used where specified (not single objects)
- [ ] Objects are used where specified (not arrays)

---

## ❌ Common Mistakes to AVOID

### Wrong: Using camelCase
```json
{
  "passengerName": "RAHUL KUMAR",  // ❌ WRONG
  "flightNumber": "EK372"          // ❌ WRONG
}
```

### Correct: Using snake_case
```json
{
  "passenger_name": "RAHUL KUMAR",  // ✅ CORRECT
  "flight_number": "372"            // ✅ CORRECT
}
```

### Wrong: Array vs Object confusion
```json
{
  "passenger": ["RAHUL KUMAR"]  // ❌ WRONG for boarding pass
}
```

### Correct: String for boarding pass
```json
{
  "passenger_name": "RAHUL KUMAR"  // ✅ CORRECT
}
```

### Wrong: Adding extra fields
```json
{
  "document_type": "boarding_pass",
  "pnr": "ABC123",
  "extra_field": "value"  // ❌ WRONG - not in schema
}
```

### Correct: Only specified fields
```json
{
  "document_type": "boarding_pass",
  "pnr": "ABC123"  // ✅ CORRECT
}
```

---

## Testing

To verify strict adherence:

1. Extract document
2. Check `document_type` value
3. Validate against corresponding schema
4. Ensure NO extra fields
5. Ensure ALL required fields present
6. Verify data types match
7. Check name format matches document type

---

## Summary

| Document | Passenger Format | Flight Info | Key Identifier |
|----------|------------------|-------------|----------------|
| Flight Ticket | Array of objects | In `segments` array | `pnr` |
| Boarding Pass | Single string | In `flight` object | `pnr` |
| Flight Invoice | Single object | In `flight` object | `invoice_number` |
| Hotel Voucher | Single object (`full_name`) | N/A | `confirmation_number` |

**REMEMBER: These schemas are STRICT. Follow them EXACTLY.**
