# S3 Processing - Frontend Example

## User Experience Flow

### Step 1: Input S3 Links
```
┌─────────────────────────────────────────┐
│ 🔗 S3 Links (one per line)              │
├─────────────────────────────────────────┤
│ s3://my-bucket/ticket.pdf               │
│ s3://my-bucket/boarding.jpg             │
│ s3://my-bucket/hotel.png                │
│ https://docs.s3.us-east-1.../invoice.pdf│
└─────────────────────────────────────────┘
         [Extract Data]
```

### Step 2: Processing Status
```
┌─────────────────────────────────────────┐
│ 🔄 Processing Status                    │
│                                         │
│ Processing 4 S3 link(s) one by one...  │
│ Processing 4 file(s)...                 │
│                                         │
│ [Spinner Animation]                     │
└─────────────────────────────────────────┘
```

### Step 3a: All Success
```
┌─────────────────────────────────────────┐
│ ✅ Extraction completed                  │
│    3 Booking(s) Extracted               │
│                                         │
│ [Process New Documents]                 │
└─────────────────────────────────────────┘

┌──────────────────┬──────────────────────┐
│ 📄 Document      │ 📊 Extracted Data    │
│                  │                      │
│ [Dropdown ▼]     │ ✈️ Flight Booking 1  │
│ 1. ticket.pdf    │ 🎯 Confidence: 95%   │
│ 2. boarding.jpg  │                      │
│ 3. hotel.png     │ PNR: ABC123          │
│                  │ Flight: AI101        │
└──────────────────┴──────────────────────┘
```

### Step 3b: Partial Success
```
┌─────────────────────────────────────────┐
│ ⚠️ Processed 3/4 files successfully.    │
│    1 file(s) failed.                    │
│                                         │
│ ⚠️ Some files failed to process:        │
│ • s3://my-bucket/invalid.pdf:           │
│   Access Denied                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ ✅ Extraction completed                  │
│    2 Booking(s) Extracted               │
│                                         │
│ [Process New Documents]                 │
└─────────────────────────────────────────┘
```

### Step 3c: Complete Failure
```
┌─────────────────────────────────────────┐
│ ❌ Processing failed                     │
│                                         │
│ Failed to download any files. Errors:   │
│ • s3://bucket1/file.pdf: NoSuchBucket   │
│ • s3://bucket2/file.jpg: AccessDenied   │
└─────────────────────────────────────────┘
```

## Code Example

### React Component State
```jsx
const [processingStatus, setProcessingStatus] = useState({
  total: 4,
  current: 0,
  message: 'Processing 4 S3 link(s) one by one...'
});

const [fileErrors, setFileErrors] = useState([
  {
    index: 2,
    url: 's3://bucket/invalid.pdf',
    error: 'Access Denied',
    status: 'failed'
  }
]);
```

### Processing Status Display
```jsx
{processingStatus && (
  <div className="processing-status">
    <Loader2 size={20} className="spinner" />
    <div className="status-text">
      <div>{processingStatus.message}</div>
      <div className="status-detail">
        Processing {processingStatus.total} file(s)...
      </div>
    </div>
  </div>
)}
```

### Error Display
```jsx
{fileErrors.length > 0 && (
  <div className="file-errors">
    <div className="errors-header">
      <AlertCircle size={18} />
      <span>Some files failed to process:</span>
    </div>
    <ul className="errors-list">
      {fileErrors.map((err, idx) => (
        <li key={idx}>
          <strong>{err.url}:</strong> {err.error}
        </li>
      ))}
    </ul>
  </div>
)}
```

## API Response Handling

### Success Response
```javascript
const response = await axios.post('/extract/s3', {
  s3_urls: [
    's3://bucket/file1.pdf',
    's3://bucket/file2.jpg',
    's3://bucket/file3.png'
  ]
});

// Response structure:
{
  success: true,
  count: 3,
  results: [...],
  files: [
    { name: 'file1.pdf', status: 'success', ... },
    { name: 'file2.jpg', status: 'success', ... },
    { name: 'file3.png', status: 'success', ... }
  ],
  errors: [],
  summary: {
    total: 3,
    successful: 3,
    failed: 0
  }
}
```

### Partial Failure Response
```javascript
{
  success: true,
  count: 2,
  results: [...],
  files: [
    { name: 'file1.pdf', status: 'success', ... },
    { name: 'file3.png', status: 'success', ... }
  ],
  errors: [
    {
      index: 2,
      url: 's3://bucket/file2.jpg',
      error: 'NoSuchKey: The specified key does not exist',
      status: 'failed'
    }
  ],
  summary: {
    total: 3,
    successful: 2,
    failed: 1
  }
}
```

## CSS Styling

### Processing Status
```css
.processing-status {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 8px;
  margin-bottom: 1rem;
  border: 1px solid #93c5fd;
}

.spinner {
  animation: spin 1s linear infinite;
}
```

### Error Display
```css
.file-errors {
  padding: 0.875rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.errors-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #dc2626;
}
```

## Real-World Example

### Scenario: Travel Agency Processing
```
Agency uploads 10 S3 links:
- 5 flight tickets (PDF)
- 3 boarding passes (JPG)
- 2 hotel bookings (PNG)

Processing:
✅ ticket1.pdf - Success
✅ ticket2.pdf - Success
❌ ticket3.pdf - Access Denied (wrong bucket)
✅ ticket4.pdf - Success
✅ ticket5.pdf - Success
✅ boarding1.jpg - Success
✅ boarding2.jpg - Success
❌ boarding3.jpg - NoSuchKey (file deleted)
✅ hotel1.png - Success
✅ hotel2.png - Success

Result:
- 8/10 files processed successfully
- 6 bookings extracted (some files merged)
- 2 errors displayed to user
- User can review and retry failed files
```

## Benefits

### 1. Resilience
- One bad link doesn't break entire batch
- Partial results are still useful

### 2. Transparency
- User sees exactly what failed
- Clear error messages for debugging

### 3. Efficiency
- Successful files are processed immediately
- No need to retry entire batch

### 4. User Control
- Can fix errors and retry specific files
- Can proceed with partial results
