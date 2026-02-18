# Document Structures Summary

## Overview

The system handles three types of flight documents, each with its own optimized structure:

1. **Flight Ticket** - Comprehensive booking details
2. **Boarding Pass** - Simplified boarding information
3. **Flight Invoice** - Payment and billing details

## 1. Flight Ticket (flight_itinerary)

### Purpose
Complete booking information with all flight segments, passengers, and fare details.

### Structure
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

### Key Features
- Multiple passengers support
- Multiple segments (connecting flights)
- Complete fare information
- Baggage allowance details
- Special services (meals, wheelchair, etc.)

## 2. Boarding Pass (boarding_pass)

### Purpose
Quick boarding information with gate, seat, and timing details.

### Structure
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

### Key Features
- Flat, simple structure
- Gate and boarding time
- Barcode data
- Boarding group/zone
- Single passenger, single flight

## 3. Flight Invoice (flight_invoice)

### Purpose
Payment and billing information with fare breakdown.

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

### Key Features
- Detailed fare breakdown
- Payment method information
- Tax details (GSTIN)
- Transaction tracking

## Merged Output

When all three documents are processed together:

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
  
  "boarding_passes": [
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
        "raw_data": "..."
      }
    }
  ],
  
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
  
  "documentsUsed": ["TICKET", "BOARDING_PASS", "INVOICE"],
  
  "reasoningInsights": {
    "averageConfidence": 95,
    "issues": [],
    "suggestions": []
  }
}
```

## Structure Comparison

| Feature | Ticket | Boarding Pass | Invoice |
|---------|--------|---------------|---------|
| Structure | Nested (segments/passengers) | Flat | Nested |
| Passengers | Array (multiple) | Single string | Object (single) |
| Flight Info | In segments | In flight object | In flight object |
| Gate Info | ❌ No | ✅ Yes | ❌ No |
| Barcode | ❌ No | ✅ Yes | ❌ No |
| Fare Breakdown | Basic | ❌ No | ✅ Detailed |
| Payment Info | ❌ No | ❌ No | ✅ Yes |
| Baggage | ✅ Yes | ❌ No | ❌ No |

## Usage Guidelines

### When to Use Each Structure

**Flight Ticket:**
- Complete booking information needed
- Multiple passengers or segments
- Baggage allowance required
- Special services tracking

**Boarding Pass:**
- Quick boarding information
- Gate and seat assignment
- Barcode scanning
- Real-time boarding updates

**Flight Invoice:**
- Payment processing
- Accounting and billing
- Tax reporting
- Refund processing

### Merging Strategy

1. **Ticket** provides the base structure
2. **Boarding Pass** adds gate and boarding details
3. **Invoice** adds payment information
4. All three are kept in `boarding_passes` array for reference

## Frontend Display

### Ticket Display
- Show all segments
- Display passenger list
- Show baggage allowance
- List special services

### Boarding Pass Display
- Highlight gate and boarding time
- Show barcode information
- Display boarding group
- Emphasize seat assignment

### Invoice Display
- Show fare breakdown
- Display payment method
- Show tax details
- Display transaction ID
