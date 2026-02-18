# Travel Document Extractor - React Frontend

Modern React UI for the Travel Document Extractor with split-view document preview and results.

## Features

- 📤 Upload multiple PDF files
- 🔗 Process documents from S3 URLs
- 📄 Live PDF preview (left panel)
- 📊 Extracted data display (right panel)
- 🎯 Confidence scoring with visual indicators
- ⚠️ Issues and suggestions from AI reasoning
- 💾 Download individual or all results as JSON
- ✈️ Support for flights, trains, and hotels

## Installation

```bash
cd frontend
npm install
```

## Development

1. Start the FastAPI backend (from parent directory):
```bash
cd ..
python api.py
```

2. Start the React dev server:
```bash
npm run dev
```

3. Open http://localhost:3000

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Tech Stack

- React 18
- Vite (build tool)
- Axios (HTTP client)
- Lucide React (icons)
- Native browser PDF viewer

## UI Layout

```
┌─────────────────────────────────────────┐
│           Header (Gradient)             │
├──────────────────┬──────────────────────┤
│                  │                      │
│  Document        │   Extracted Data     │
│  Preview         │   - Confidence       │
│  (PDF Viewer)    │   - Issues           │
│                  │   - Suggestions      │
│  [< 1/3 >]       │   - Details          │
│                  │   - Download         │
│                  │                      │
└──────────────────┴──────────────────────┘
```

## API Endpoints Used

- `POST /extract/upload` - Upload PDF files
- `POST /extract/s3` - Process S3 URLs
- `POST /extract/mixed` - Both uploads and S3
