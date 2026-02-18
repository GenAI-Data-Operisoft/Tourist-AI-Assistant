# Complete Document Structures Reference

## Overview

The system extracts data from 5 different travel document types:

1. **Flight Ticket** (flight_itinerary)
2. **Boarding Pass** (boarding_pass)
3. **Flight Invoice** (flight_invoice)
4. **Train Ticket** (train_ticket)
5. **Hotel Voucher** (hotel_voucher)

---

## 1. Flight Ticket

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

---

## 2. Boarding Pass

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

---

## 3. Flight Invoice

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

---

## 4. Train Ticket

```json
{
  "document_type": "train_ticket",
  "pnr": "1234567890",
  "ticket_number": "TKT123456",
  "passenger": {
    "title": "MR",
    "first_name": "RAHUL",
    "last_name": "KUMAR",
    "age": 35,
    "gender": "M"
  },
  "train": {
    "train_number": "12345",
    "train_name": "Rajdhani Express",
    "departure": {
      "station": "NDLS",
      "station_name": "New Delhi",
      "datetime_local": "2026-02-10T16:30:00+05:30"
    },
    "arrival": {
      "station": "BCT",
      "station_name": "Mumbai Central",
      "datetime_local": "2026-02-11T08:45:00+05:30"
    }
  },
  "seat": {
    "coach": "A1",
    "seat_number": "45",
    "class": "2A",
    "berth": "Lower"
  },
  "fare": {
    "currency": "INR",
    "base_fare": 1500,
    "reservation_charge": 50,
    "total_amount": 1550
  },
  "booking_date": "2026-01-25"
}
```

---

## 5. Hotel Voucher

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

---

## Quick Reference Table

| Document Type | Key Identifier | Passenger Format | Date Format |
|---------------|----------------|------------------|-------------|
| Flight Ticket | pnr | Array of objects | ISO 8601 with TZ |
| Boarding Pass | pnr | Single string | ISO 8601 with TZ |
| Flight Invoice | invoice_number | Single object | ISO 8601 |
| Train Ticket | pnr | Single object | ISO 8601 with TZ |
| Hotel Voucher | confirmation_number | Single object | YYYY-MM-DD |

## Common Fields

### All Documents
- `document_type` - Type identifier
- Date fields in ISO format

### Flight Documents (Ticket, Boarding Pass, Invoice)
- `pnr` - Booking reference
- Airport codes (3-letter IATA)
- Carrier codes (2-letter IATA)

### Booking Documents (Ticket, Hotel, Train)
- Passenger/Guest information
- Date and time details
- Fare/Rate information

## Unique Features

### Flight Ticket
- Multiple passengers
- Multiple segments (connecting flights)
- Baggage allowance
- Special services (SSR codes)

### Boarding Pass
- Gate information
- Boarding time
- Barcode data
- Boarding group

### Flight Invoice
- Fare breakdown (base + taxes + fees)
- Payment method
- Tax details (GSTIN)
- Transaction ID

### Train Ticket
- Coach and berth details
- Station codes
- Class information
- Reservation charges

### Hotel Voucher
- Hotel contact information
- Stay duration (nights)
- Room type and occupancy
- Meal plan
- Cancellation policy

## Merging Behavior

### Flight Documents
When ticket + boarding pass + invoice are merged:
- Passengers from ticket
- Segments with gate from boarding pass
- Fare from ticket/invoice
- Payment from invoice
- Boarding passes stored separately

### Train Documents
Single document, no merging needed

### Hotel Documents
Single document, no merging needed

## Frontend Display

### Flight Booking
- Passenger cards (expandable)
- Segment cards (per flight leg)
- Boarding pass cards (blue background)
- Fare breakdown
- Payment details

### Train Booking
- Passenger info
- Train details
- Seat/berth info
- Fare breakdown

### Hotel Booking
- Guest info
- Hotel details with address
- Stay dates and duration
- Room details
- Rate information
- Cancellation policy (highlighted)
