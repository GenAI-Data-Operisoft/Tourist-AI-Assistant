# Setup Guide - Travel Document Extractor

Complete setup instructions for the React + FastAPI application.

## Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- AWS credentials configured (for Bedrock and S3)
- AWS Bedrock access to Claude 3 Haiku

## Backend Setup

### 1. Install Python Dependencies

```bash
cd tourish_market/flight_extraction
pip install -r ../requirements.txt
```

### 2. Configure AWS Credentials

Make sure your AWS credentials are configured:

```bash
aws configure
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### 3. Start the FastAPI Server

```bash
python api.py
```

The API will be available at http://localhost:8000

Test it: http://localhost:8000 (should show status message)

## Frontend Setup

### 1. Install Node Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The React app will be available at http://localhost:3000

## Usage

### Upload PDFs

1. Open http://localhost:3000
2. Click "Choose files..." and select PDF documents
3. Click "Extract Data"
4. View documents on the left, results on the right

### Use S3 Links

1. Paste S3 URLs in the text area (one per line):
   ```
   s3://my-bucket/documents/ticket.pdf
   https://my-bucket.s3.us-east-1.amazonaws.com/boarding-pass.pdf
   ```
2. Click "Extract Data"

### Mixed Mode

You can upload files AND provide S3 links at the same time!

## API Endpoints

### POST /extract/upload
Upload PDF files for extraction.

**Request:**
- Content-Type: multipart/form-data
- Body: files (multiple PDF files)

**Response:**
```json
{
  "success": true,
  "count": 2,
  "results": [...]
}
```

### POST /extract/s3
Process documents from S3 URLs.

**Request:**
```json
{
  "s3_urls": [
    "s3://bucket/file1.pdf",
    "s3://bucket/file2.pdf"
  ]
}
```

### POST /extract/mixed
Process both uploaded files and S3 URLs.

**Request:**
- Content-Type: multipart/form-data
- Body: files (optional)
- Query params: s3_urls (optional)

## Troubleshooting

### Backend Issues

**Error: "No module named 'aws_clients'"**
- Make sure you're in the correct directory
- Check that aws_clients.py exists

**Error: "Unable to locate credentials"**
- Configure AWS credentials: `aws configure`
- Or set environment variables

**Error: "Access denied to Bedrock"**
- Request access to Claude 3 Haiku in AWS Bedrock console
- Check your IAM permissions

### Frontend Issues

**Error: "Network Error" or "CORS"**
- Make sure the backend is running on port 8000
- Check CORS settings in api.py

**PDF not displaying**
- Some browsers block PDF iframes
- Try a different browser (Chrome/Edge recommended)

**Error: "npm install fails"**
- Delete node_modules and package-lock.json
- Run `npm install` again

## Production Deployment

### Backend

```bash
# Using gunicorn
pip install gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

```bash
cd frontend
npm run build
```

Serve the `dist` folder with nginx or any static file server.

## Environment Variables

Create a `.env` file in the backend directory:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
API_PORT=8000
```

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │  HTTP   │   FastAPI    │  SDK    │  AWS        │
│   Frontend  ├────────>│   Backend    ├────────>│  Bedrock    │
│  (Port 3000)│         │  (Port 8000) │         │  & S3       │
└─────────────┘         └──────────────┘         └─────────────┘
```

## Support

For issues or questions, check:
- Backend logs in the terminal running api.py
- Browser console for frontend errors
- Network tab in browser DevTools for API calls
