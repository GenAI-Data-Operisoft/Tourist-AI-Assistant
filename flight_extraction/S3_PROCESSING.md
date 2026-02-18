# S3 Link Processing Guide

## Overview

The system now processes S3 links **one by one**, providing detailed feedback for each file and handling errors gracefully.

## Features

### 1. Sequential Processing
Each S3 link is downloaded and processed individually:
```
Link 1: s3://bucket/ticket.pdf     → ✅ Success
Link 2: s3://bucket/boarding.jpg   → ✅ Success  
Link 3: s3://bucket/invalid.pdf    → ❌ Failed (Access Denied)
Link 4: s3://bucket/hotel.png      → ✅ Success
```

### 2. Error Handling
- Individual file failures don't stop the entire process
- Detailed error messages for each failed file
- Summary shows successful vs failed files

### 3. Progress Feedback
- Real-time status updates
- Shows which file is being processed
- Displays total progress

## API Response Format

### Successful Response
```json
{
  "success": true,
  "count": 3,
  "results": [...],
  "files": [
    {
      "name": "ticket.pdf",
      "url": "s3://bucket/ticket.pdf",
      "size": 245678,
      "type": "PDF",
      "status": "success"
    },
    {
      "name": "boarding.jpg",
      "url": "s3://bucket/boarding.jpg",
      "size": 156789,
      "type": "JPG",
      "status": "success"
    }
  ],
  "errors": [
    {
      "index": 3,
      "url": "s3://bucket/invalid.pdf",
      "error": "Access Denied",
      "status": "failed"
    }
  ],
  "summary": {
    "total": 3,
    "successful": 2,
    "failed": 1
  }
}
```

## Usage Examples

### Example 1: Multiple Valid S3 Links
```
Input:
s3://my-bucket/documents/flight-ticket.pdf
s3://my-bucket/documents/boarding-pass.jpg
s3://my-bucket/documents/hotel-booking.png

Output:
✅ Processed 3/3 files successfully
```

### Example 2: Mixed Success/Failure
```
Input:
s3://my-bucket/valid-ticket.pdf
s3://wrong-bucket/missing-file.pdf
s3://my-bucket/valid-boarding.jpg

Output:
⚠️ Processed 2/3 files successfully. 1 file(s) failed.

Errors:
• s3://wrong-bucket/missing-file.pdf: Failed to download from S3 (NoSuchBucket)
```

### Example 3: All Failures
```
Input:
s3://invalid-bucket/file1.pdf
s3://invalid-bucket/file2.pdf

Output:
❌ Failed to download any files
```

## Supported S3 URL Formats

### Format 1: S3 Protocol
```
s3://bucket-name/path/to/file.pdf
s3://my-documents/2024/january/ticket.pdf
```

### Format 2: HTTPS URL
```
https://bucket-name.s3.region.amazonaws.com/path/to/file.pdf
https://my-docs.s3.us-east-1.amazonaws.com/tickets/boarding.jpg
```

### Supported File Types
- PDF (.pdf)
- JPEG (.jpg, .jpeg)
- PNG (.png)

## Error Types

### Common Errors

1. **NoSuchBucket**
   - Bucket doesn't exist
   - Check bucket name spelling

2. **NoSuchKey**
   - File doesn't exist in bucket
   - Check file path

3. **AccessDenied**
   - No permission to access bucket/file
   - Check IAM permissions

4. **InvalidBucketName**
   - Bucket name format is invalid
   - Check S3 naming rules

## Frontend Display

### Processing Status
```
┌─────────────────────────────────────┐
│ 🔄 Processing Status                │
│                                     │
│ Processing 5 S3 link(s) one by one │
│ Processing 5 file(s)...             │
└─────────────────────────────────────┘
```

### Success with Partial Failures
```
┌─────────────────────────────────────┐
│ ⚠️ Processed 3/5 files successfully │
│    2 file(s) failed.                │
│                                     │
│ Some files failed to process:       │
│ • file1.pdf: Access Denied          │
│ • file2.jpg: NoSuchKey              │
└─────────────────────────────────────┘
```

### Complete Success
```
┌─────────────────────────────────────┐
│ ✅ Extraction completed              │
│    3 Booking(s) Extracted           │
└─────────────────────────────────────┘
```

## Backend Logging

The backend logs each S3 operation:

```
Processing S3 link 1/5: s3://bucket/file1.pdf
Processing S3 link 2/5: s3://bucket/file2.jpg
Failed to download s3://bucket/file3.pdf: Access Denied
Processing S3 link 4/5: s3://bucket/file4.png
Processing S3 link 5/5: s3://bucket/file5.pdf
Extracting data from 4 file(s)...
```

## Best Practices

### 1. Verify S3 Access
Before processing, ensure:
- AWS credentials are configured
- IAM role has S3 read permissions
- Bucket policies allow access

### 2. Check File Formats
- Only upload supported formats (PDF, JPG, PNG)
- Verify file extensions match content

### 3. Handle Large Batches
- For many files, consider processing in smaller batches
- Monitor memory usage
- Check AWS rate limits

### 4. Error Recovery
- Review error messages
- Fix access issues
- Retry failed files separately

## Testing

### Test with Mixed Results
```bash
# Create test S3 links file
cat > test_links.txt << EOF
s3://valid-bucket/ticket.pdf
s3://invalid-bucket/missing.pdf
s3://valid-bucket/boarding.jpg
EOF

# Test via API
curl -X POST http://localhost:8000/extract/s3 \
  -H "Content-Type: application/json" \
  -d '{
    "s3_urls": [
      "s3://valid-bucket/ticket.pdf",
      "s3://invalid-bucket/missing.pdf",
      "s3://valid-bucket/boarding.jpg"
    ]
  }'
```

## Troubleshooting

### Issue: All S3 downloads fail
**Solution:**
1. Check AWS credentials: `aws s3 ls`
2. Verify bucket access: `aws s3 ls s3://bucket-name`
3. Check IAM permissions

### Issue: Some files fail randomly
**Solution:**
1. Check file sizes (very large files may timeout)
2. Verify network stability
3. Check S3 bucket region

### Issue: Wrong file type detected
**Solution:**
1. Ensure file extensions are correct
2. Verify file content matches extension
3. Check S3 metadata

## Performance

### Processing Time
- Small files (< 1MB): ~2-3 seconds per file
- Medium files (1-5MB): ~5-10 seconds per file
- Large files (> 5MB): ~10-20 seconds per file

### Optimization Tips
- Use smaller image files when possible
- Compress PDFs before uploading to S3
- Process files in parallel (future enhancement)
