# api.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tempfile
import os
import boto3
from typing import List, Optional
from main import process_files

app = FastAPI(title="Travel Document Extractor API")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

s3_client = boto3.client('s3')

class S3LinkRequest(BaseModel):
    s3_urls: List[str]

class MixedRequest(BaseModel):
    s3_urls: Optional[List[str]] = []

def download_from_s3(s3_url: str) -> tuple[str, dict]:
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
        
        # Get file extension from key
        file_ext = os.path.splitext(key)[1] or ".pdf"
        
        # Download to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        s3_client.download_fileobj(bucket, key, temp_file)
        temp_file.close()
        
        # Get file metadata
        file_name = os.path.basename(key)
        file_size = os.path.getsize(temp_file.name)
        
        metadata = {
            "name": file_name,
            "url": s3_url,
            "size": file_size,
            "type": file_ext.replace(".", "").upper()
        }
        
        return temp_file.name, metadata
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download from S3 ({s3_url}): {str(e)}")

@app.get("/")
def root():
    return {"message": "Travel Document Extractor API", "status": "running"}

@app.post("/extract/upload")
async def extract_from_upload(files: List[UploadFile] = File(...)):
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
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp files
        for path in temp_paths:
            try:
                os.unlink(path)
            except:
                pass

@app.post("/extract/s3")
async def extract_from_s3(request: S3LinkRequest):
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
                    "status": "success"
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
    request: MixedRequest,
    files: Optional[List[UploadFile]] = File(None)
):
    """Extract data from both uploaded files and S3 URLs"""
    temp_paths = []
    file_metadata = []
    errors = []
    
    try:
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
        if request.s3_urls:
            for idx, s3_url in enumerate(request.s3_urls, 1):
                try:
                    print(f"Processing S3 link {idx}/{len(request.s3_urls)}: {s3_url}")
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
