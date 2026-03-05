# api.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tempfile
import os
import boto3
from botocore.config import Config
from typing import List, Optional, Tuple
from main import process_files
from auth import get_current_user

app = FastAPI(title="TOURISH AI ASSISTANT API")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://localhost:5173",
        "https://ai.tourish.biz"
        "https://ai-dev.tourish.biz",  # Add your production domain
        "http://65.2.55.2:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure S3 client with signature version 4
s3_config = Config(
    signature_version='s3v4',
    region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
)
s3_client = boto3.client('s3', config=s3_config)

class S3LinkRequest(BaseModel):
    s3_urls: List[str]

class MixedRequest(BaseModel):
    s3_urls: Optional[List[str]] = []

def download_from_s3(s3_url: str) -> Tuple[str, dict]:
    """Download file from S3 and return local temp path with metadata"""
    try:
        # Parse S3 URL (s3://bucket/key or https://bucket.s3.region.amazonaws.com/key)
        if s3_url.startswith("s3://"):
            parts = s3_url.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1]
        else:
            # Parse HTTPS URL
            parts = s3_url.split(".s3.")
            bucket = parts[0].replace("https://", "")
            key = parts[1].split("/", 1)[1] if "/" in parts[1] else ""
        
        # Get bucket region
        try:
            bucket_location = s3_client.get_bucket_location(Bucket=bucket)
            bucket_region = bucket_location['LocationConstraint']
            # LocationConstraint is None for us-east-1
            if bucket_region is None:
                bucket_region = 'us-east-1'
        except Exception as e:
            print(f"Could not determine bucket region: {e}")
            bucket_region = 'ap-south-1'  # Default to your region
        
        # Create region-specific S3 client with same credentials
        # This ensures session tokens are properly included
        session = boto3.Session()
        s3_regional_client = session.client(
            's3',
            region_name=bucket_region,
            config=Config(signature_version='s3v4')
        )
        
        # Get file extension from key
        file_ext = os.path.splitext(key)[1] or ".pdf"
        
        # Download to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        s3_regional_client.download_fileobj(bucket, key, temp_file)
        temp_file.close()
        
        # Get file metadata
        file_name = os.path.basename(key)
        file_size = os.path.getsize(temp_file.name)
        
        # Don't use presigned URLs - they fail with temporary credentials
        # Instead, we'll serve files through a backend proxy endpoint
        metadata = {
            "name": file_name,
            "url": s3_url,
            "bucket": bucket,
            "key": key,
            "size": file_size,
            "type": file_ext.replace(".", "").upper(),
            "region": bucket_region
        }
        
        return temp_file.name, metadata
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download from S3 ({s3_url}): {str(e)}")

@app.get("/")
def root():
    return {"message": "TOURISH AI ASSISTNAT API", "status": "running"}

@app.get("/s3-proxy/{bucket}/{key:path}")
async def s3_proxy(bucket: str, key: str):
    """Proxy endpoint to serve S3 files through backend (works with temporary credentials)"""
    from fastapi.responses import StreamingResponse
    import io
    
    try:
        # Get bucket region
        try:
            bucket_location = s3_client.get_bucket_location(Bucket=bucket)
            bucket_region = bucket_location['LocationConstraint']
            if bucket_region is None:
                bucket_region = 'us-east-1'
        except Exception as e:
            print(f"Could not determine bucket region: {e}")
            bucket_region = 'ap-south-1'
        
        # Create region-specific client
        session = boto3.Session()
        s3_regional_client = session.client(
            's3',
            region_name=bucket_region,
            config=Config(signature_version='s3v4')
        )
        
        # Get file from S3
        response = s3_regional_client.get_object(Bucket=bucket, Key=key)
        file_stream = response['Body']
        
        # Determine content type
        file_ext = os.path.splitext(key)[1].lower()
        content_type = 'application/pdf' if file_ext == '.pdf' else f'image/{file_ext.replace(".", "")}'
        
        # Stream the file
        return StreamingResponse(
            io.BytesIO(file_stream.read()),
            media_type=content_type,
            headers={
                "Content-Disposition": "inline",
                "Cache-Control": "public, max-age=3600"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch S3 file: {str(e)}")

@app.post("/extract/upload")
async def extract_from_upload(
    files: List[UploadFile] = File(...),
    user = Depends(get_current_user)
):
    """Extract data from uploaded PDF and image files"""
    temp_paths = []
    file_info = []
    
    try:
        # Save uploaded files to temp
        for file in files:
            # Check file extension
            filename_lower = file.filename.lower()
            if filename_lower.endswith('.pdf'):
                suffix = ".pdf"
            elif filename_lower.endswith(('.jpg', '.jpeg', '.png')):
                suffix = os.path.splitext(file.filename)[1]
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}. Only PDF, JPG, JPEG, PNG allowed.")
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            temp_paths.append(temp_file.name)
            file_info.append({
                "name": file.filename,
                "type": suffix.replace(".", "").upper()
            })
        
        # Process files
        results = process_files(temp_paths)
        
        return JSONResponse(content={
            "success": True,
            "count": len(results),
            "results": results
        })
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in extract_from_upload: {error_details}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp files
        for path in temp_paths:
            try:
                os.unlink(path)
            except:
                pass

@app.post("/extract/s3")
async def extract_from_s3(
    request: S3LinkRequest,
    user = Depends(get_current_user)
):
    """Extract data from S3 URLs - processes each link individually"""
    temp_paths = []
    file_metadata = []
    download_errors = []
    
    try:
        # Download from S3 one by one
        for idx, s3_url in enumerate(request.s3_urls, 1):
            try:
                print(f"Processing S3 link {idx}/{len(request.s3_urls)}: {s3_url}")
                temp_path, metadata = download_from_s3(s3_url)
                temp_paths.append(temp_path)
                file_metadata.append({
                    **metadata,
                    "index": idx,
                    "status": "success",
                    "source": "s3",
                    "url": s3_url  # Include S3 URL for frontend display
                })
            except HTTPException as e:
                download_errors.append({
                    "index": idx,
                    "url": s3_url,
                    "error": str(e.detail),
                    "status": "failed"
                })
                print(f"Failed to download {s3_url}: {e.detail}")
                continue
        
        if not temp_paths:
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to download any files. Errors: {download_errors}"
            )
        
        # Process files
        print(f"Extracting data from {len(temp_paths)} file(s)...")
        results = process_files(temp_paths)
        
        return JSONResponse(content={
            "success": True,
            "count": len(results),
            "results": results,
            "files": file_metadata,
            "errors": download_errors,
            "summary": {
                "total": len(request.s3_urls),
                "successful": len(file_metadata),
                "failed": len(download_errors)
            }
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp files
        for path in temp_paths:
            try:
                os.unlink(path)
            except:
                pass

@app.post("/extract/mixed")
async def extract_mixed(
    files: Optional[List[UploadFile]] = File(None),
    s3_urls: Optional[str] = Form(None),
    user = Depends(get_current_user)
):
    """Extract data from both uploaded files and S3 URLs"""
    temp_paths = []
    file_metadata = []
    errors = []
    
    print(f"DEBUG: Received files: {len(files) if files else 0}")
    print(f"DEBUG: Received s3_urls parameter: {s3_urls}")
    
    try:
        # Parse S3 URLs from JSON string
        s3_url_list = []
        if s3_urls:
            import json as json_lib
            s3_url_list = json_lib.loads(s3_urls)
            print(f"DEBUG: Parsed S3 URLs: {s3_url_list}")
        else:
            print("DEBUG: No s3_urls received")
        # Handle uploaded files
        if files:
            for idx, file in enumerate(files, 1):
                try:
                    filename_lower = file.filename.lower()
                    if filename_lower.endswith('.pdf'):
                        suffix = ".pdf"
                    elif filename_lower.endswith(('.jpg', '.jpeg', '.png')):
                        suffix = os.path.splitext(file.filename)[1]
                    else:
                        errors.append({
                            "index": idx,
                            "name": file.filename,
                            "error": "Unsupported file type",
                            "status": "skipped"
                        })
                        continue
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                    content = await file.read()
                    temp_file.write(content)
                    temp_file.close()
                    temp_paths.append(temp_file.name)
                    
                    file_metadata.append({
                        "name": file.filename,
                        "type": suffix.replace(".", "").upper(),
                        "size": len(content),
                        "source": "upload",
                        "status": "success"
                    })
                except Exception as e:
                    errors.append({
                        "index": idx,
                        "name": file.filename,
                        "error": str(e),
                        "status": "failed"
                    })
        
        # Handle S3 URLs one by one
        if s3_url_list:
            for idx, s3_url in enumerate(s3_url_list, 1):
                try:
                    print(f"Processing S3 link {idx}/{len(s3_url_list)}: {s3_url}")
                    temp_path, metadata = download_from_s3(s3_url)
                    temp_paths.append(temp_path)
                    file_metadata.append({
                        **metadata,
                        "source": "s3",
                        "status": "success"
                    })
                except HTTPException as e:
                    errors.append({
                        "index": idx,
                        "url": s3_url,
                        "error": str(e.detail),
                        "source": "s3",
                        "status": "failed"
                    })
                    print(f"Failed to download {s3_url}: {e.detail}")
                    continue
        
        if not temp_paths:
            raise HTTPException(status_code=400, detail="No files could be processed")
        
        # Process files
        print(f"Extracting data from {len(temp_paths)} file(s)...")
        results = process_files(temp_paths)
        
        return JSONResponse(content={
            "success": True,
            "count": len(results),
            "results": results,
            "files": file_metadata,
            "errors": errors,
            "summary": {
                "total": len(file_metadata) + len(errors),
                "successful": len(file_metadata),
                "failed": len(errors)
            }
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp files
        for path in temp_paths:
            try:
                os.unlink(path)
            except:
                pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
