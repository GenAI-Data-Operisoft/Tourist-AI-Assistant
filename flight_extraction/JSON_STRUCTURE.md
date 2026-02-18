# Updated JSON Structure Documentation

## Flight Itinerary/Ticket

### Complete Structure
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

### Field Descriptions

#### Top Level
- `document_type`: Type of document (flight_itinerary, boarding_pass, flight_invoice)
- `pnr`: Passenger Name Record / Booking Reference
- `issue_date`: Date ticket was issued (YYYY-MM-DD)
- `issuing_carrier`: Airline that issued the ticket (2-letter IATA code)
- `booking_source`: Where the ticket was booked (airline name, travel agency, etc.)

#### Passengers Array
Each passenger object contains:
- `title`: Mr/Ms/Mrs/Dr
- `first_name`: Passenger's first name
- `last_name`: Passenger's last name
- `ticket_number`: 13-digit ticket number
- `frequent_flyer`: Loyalty program details
  - `program`: Program name (e.g., Skywards, Miles & More)
  - `number_masked`: Masked FF number for privacy

#### Segments Array
Each flight segment contains:
- `segment_number`: Sequential number (1, 2, 3...)
- `marketing_carrier`: Airline selling the ticket
- `operating_carrier`: Airline operating the flight
- `flight_number`: Flight number (without carrier code)
- `aircraft`: Aircraft type (e.g., B777-300ER, A380)
- `cabin_class`: Economy/Premium Economy/Business/First
- `booking_class`: Single letter booking class (Y, M, J, F, etc.)

**Departure Object:**
- `airport`: 3-letter IATA airport code
- `terminal`: Terminal number/letter
- `datetime_local`: ISO 8601 datetime with timezone

**Arrival Object:**
- `airport`: 3-letter IATA airport code
- `terminal`: Terminal number/letter
- `datetime_local`: ISO 8601 datetime with timezone

**Baggage Allowance:**
- `checked`: Piece concept (1PC, 2PC) or weight (23KG)
- `weight_kg`: Weight per piece in kg
- `cabin_kg`: Cabin baggage allowance in kg

**Additional:**
- `seat`: Seat assignment (e.g., 22A)
- `special_services`: Array of SSR codes (VGML, WCHR, etc.)

#### Fare Object
- `currency`: 3-letter ISO currency code
- `total_amount`: Total fare amount (number)
- `fare_basis`: Fare basis code
- `refundable`: Boolean indicating if ticket is refundable

## Boarding Pass

### Structure
Boarding passes use a simplified, flat structure optimized for quick boarding information:

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

### Field Descriptions

- `document_type`: Always "boarding_pass"
- `pnr`: Booking reference
- `ticket_number`: 13-digit ticket number
- `passenger_name`: Full name in "FIRST LAST" format
- `flight`: Flight details
  - `carrier`: 2-letter airline code
  - `flight_number`: Flight number (without carrier)
  - `date`: Flight date (YYYY-MM-DD)
- `departure`: Departure information
  - `airport`: 3-letter IATA code
  - `terminal`: Terminal number/letter
  - `gate`: Gate number
  - `boarding_time`: ISO 8601 datetime with timezone
- `arrival`: Arrival information
  - `airport`: 3-letter IATA code
- `seat`: Seat assignment (e.g., "22A")
- `boarding_group`: Boarding group/zone
- `barcode`: Barcode information
  - `format`: AZTEC, QR, PDF417, etc.
  - `raw_data`: Raw barcode data string

## Flight Invoice

### Structure
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

## Merged Output

When multiple documents (ticket + boarding pass + invoice) are processed together, they are merged:

```json
{
  "bookingIdentity": {
    "type": "FLIGHT",
    "pnr": "ABC123",
    "flightNumber": "EK372"
  },
  "document_type": "flight_booking",
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
        "datetime_local": "2026-02-10T03:10:00+04:00",
        "gate": "A12",
        "boarding_time": "02:40"
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
  "seat": {
    "number": "22A",
    "class": "Economy",
    "zone": "2"
  },
  "fare": {
    "currency": "AED",
    "base_fare": 1850.00,
    "taxes": 450.75,
    "fees": 150.00,
    "total_amount": 2450.75,
    "fare_basis": "MSAVER",
    "refundable": false
  },
  "payment": {
    "invoice_number": "INV-2026-001234",
    "invoice_date": "2026-01-31",
    "method": "Credit Card",
    "card_last4": "1234",
    "transaction_id": "TXN123456789",
    "tax_details": {
      "gstin": "29ABCDE1234F1Z5",
      "tax_amount": 450.75
    }
  },
  "boarding_info": {
    "barcode": "M1KUMAR/RAHUL...",
    "sequence_number": "0025"
  },
  "documentsUsed": ["TICKET", "BOARDING_PASS", "INVOICE"],
  "reasoningInsights": {
    "averageConfidence": 95,
    "issues": [],
    "suggestions": []
  }
}
```

## Multi-Segment Example

For connecting flights or round trips:

```json
{
  "segments": [
    {
      "segment_number": 1,
      "flight_number": "372",
      "departure": {
        "airport": "DXB",
        "datetime_local": "2026-02-10T03:10:00+04:00"
      },
      "arrival": {
        "airport": "BKK",
        "datetime_local": "2026-02-10T12:20:00+07:00"
      }
    },
    {
      "segment_number": 2,
      "flight_number": "384",
      "departure": {
        "airport": "BKK",
        "datetime_local": "2026-02-17T14:30:00+07:00"
      },
      "arrival": {
        "airport": "DXB",
        "datetime_local": "2026-02-17T18:45:00+04:00"
      }
    }
  ]
}
```

## Hotel Booking/Voucher

### Structure
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

### Field Descriptions

- `document_type`: Always "hotel_voucher"
- `confirmation_number`: Hotel booking confirmation/reference number
- `issue_date`: Date voucher was issued (YYYY-MM-DD)
- `hotel`: Hotel information
  - `name`: Hotel name
  - `address`: Complete hotel address
  - `phone`: Hotel contact number
- `guest`: Guest information
  - `full_name`: Guest name in "FIRST LAST" format
- `stay`: Stay details
  - `check_in`: Check-in date (YYYY-MM-DD)
  - `check_out`: Check-out date (YYYY-MM-DD)
  - `nights`: Number of nights (calculated or extracted)
- `room`: Room details
  - `room_type`: Type of room (Deluxe, Suite, Standard, etc.)
  - `occupancy`: Number of guests
  - `meal_plan`: Meal plan included (Breakfast, Half Board, All Inclusive, etc.)
- `rate`: Rate information
  - `currency`: 3-letter ISO currency code
  - `total_amount`: Total booking amount
  - `payment_type`: Payment method (Prepaid, Pay at Hotel, etc.)
- `cancellation_policy`: Cancellation policy text

For group bookings:

```json
{
  "passengers": [
    {
      "title": "MR",
      "first_name": "RAHUL",
      "last_name": "KUMAR",
      "ticket_number": "1761234567890"
    },
    {
      "title": "MRS",
      "first_name": "PRIYA",
      "last_name": "KUMAR",
      "ticket_number": "1761234567891"
    },
    {
      "title": "MSTR",
      "first_name": "ARJUN",
      "last_name": "KUMAR",
      "ticket_number": "1761234567892"
    }
  ]
}
```

## Date/Time Formats

### ISO 8601 with Timezone
```
2026-02-10T03:10:00+04:00
```
- Date: 2026-02-10
- Time: 03:10:00
- Timezone: +04:00 (Dubai)

### Date Only
```
2026-02-10
```

### Time Only (24-hour)
```
03:10
```

## Special Service Request (SSR) Codes

Common codes in `special_services` array:
- `VGML` - Vegetarian meal
- `KSML` - Kosher meal
- `WCHR` - Wheelchair
- `PETC` - Pet in cabin
- `UMNR` - Unaccompanied minor
- `EXST` - Extra seat
