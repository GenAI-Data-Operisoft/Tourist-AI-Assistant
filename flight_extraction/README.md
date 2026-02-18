# Travel Document Extractor

AI-powered system for extracting information from travel documents with intelligent reasoning.

## Supported Document Types

### ✈️ Flight Documents
- Boarding Pass
- Flight Invoice
- Flight Ticket

### 🚂 Train Documents
- Train Ticket
- Railway Reservation

### 🏨 Hotel Documents
- Hotel Booking Confirmation

## Key Features

### 1. Automatic Classification
Documents are automatically classified using Claude AI to determine their type.

### 2. Intelligent Extraction
Type-specific extractors pull relevant fields:
- **Flights**: PNR, flight number, passenger, dates, seat, gate, payment
- **Trains**: PNR, train number, passenger, dates, coach, seat, class, fare
- **Hotels**: Booking reference, guest info, hotel details, check-in/out dates, room type

### 3. AI Reasoning Agent 🧠
The reasoning agent validates and enriches extracted data:
- **Validation**: Checks for missing or inconsistent fields
- **Confidence Scoring**: Rates extraction quality (0-100)
- **Issue Detection**: Identifies potential problems
- **Suggestions**: Recommends improvements
- **Enrichment**: Adds computed fields (e.g., trip duration)

### 4. Smart Grouping
Documents are automatically grouped by booking:
- Multiple flight documents → Single flight record
- Train tickets → Train booking record
- Hotel confirmations → Hotel booking record

## Usage

### Streamlit App
```bash
streamlit run streamlit_app.py
```

### Command Line
```bash
python main.py document1.pdf document2.pdf
```

## Architecture

```
PDF Upload
    ↓
Text Extraction (Textract/PyMuPDF)
    ↓
Document Classification (Claude)
    ↓
Type-Specific Extraction (Claude)
    ↓
Reasoning Agent (Claude) ← Validates & Enriches
    ↓
Grouping by Booking ID
    ↓
Merge Related Documents
    ↓
JSON Output with Insights
```

## Output Format

```json
{
  "bookingIdentity": {
    "type": "FLIGHT|TRAIN|HOTEL",
    "pnr": "ABC123",
    "flightNumber": "AI101"
  },
  "passenger": {...},
  "flight|train|hotel": {...},
  "payment": {...},
  "reasoningInsights": {
    "averageConfidence": 85,
    "issues": ["Missing gate information"],
    "suggestions": ["Verify departure time"]
  },
  "documentsUsed": ["BOARDING_PASS", "INVOICE"]
}
```

## Requirements

- AWS Bedrock access (Claude 3 Haiku)
- Python 3.8+
- See requirements.txt for dependencies
