from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.background import BackgroundTasks
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import tempfile
import os
import time
from pathlib import Path
import shutil
import asyncio
import logging
import json
import io

from .utils import pptx_to_pdf, pdf_to_images, extract_text, summarize_openai, summarize_gemini
from .config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PPT to Doc API",
    description="API for converting PowerPoint presentations to summarized documents",
    version="1.0.0",
    docs_url=None,  # Disable Swagger UI
    redoc_url=None,  # Disable ReDoc
    openapi_url=None  # Disable OpenAPI schema
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Add middleware to handle response headers
@app.middleware("http")
async def add_response_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept"
    return response

class ProcessingRequest(BaseModel):
    provider: str = "openai"  # "openai" or "gemini"
    style: str = "concise"    # "concise", "detailed", or "bullet"

# Store processing status and results
processing_status: Dict[str, Dict] = {}
processing_streams: Dict[str, asyncio.Queue] = {}

@app.get("/")
@app.post("/")
async def root():
    return {"message": "PPT to Doc API is running"}

@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    provider: str = Form("openai"),
    style: str = Form("concise"),
    openai_api_key: str = Form(None),
    gemini_api_key: str = Form(None)
):
    try:
        # Log the incoming request
        logger.info(f"Received upload request for file: {file.filename}")
        logger.info(f"Provider: {provider}, Style: {style}")
        logger.info(f"File size: {file.size if hasattr(file, 'size') else 'unknown'} bytes")
        
        # Validate file extension
        if not file.filename.endswith(('.ppt', '.pptx')):
            error_msg = f"Invalid file type: {file.filename}. Only PowerPoint files (.ppt, .pptx) are allowed"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Validate API keys
        if provider == "openai" and not openai_api_key:
            error_msg = "OpenAI API key is required for OpenAI provider"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        elif provider == "gemini" and not gemini_api_key:
            error_msg = "Gemini API key is required for Gemini provider"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Generate a unique ID for this processing job
        job_id = str(int(time.time()))
        processing_status[job_id] = {
            "status": "uploading",
            "progress": 0,
            "message": "File uploaded, starting processing...",
            "results": []
        }
        processing_streams[job_id] = asyncio.Queue()
        logger.info(f"Created processing job with ID: {job_id}")
        
        # Read and store file contents before starting background task
        file_contents = await file.read()
        file_copy = UploadFile(
            filename=file.filename,
            file=io.BytesIO(file_contents)
        )
        
        # Start processing in background
        background_tasks.add_task(process_file_async, job_id, file_copy, provider, style, openai_api_key, gemini_api_key)
        
        return {"job_id": job_id}
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in processing_status:
        raise HTTPException(status_code=404, detail="Job not found")
    return processing_status[job_id]

@app.get("/stream/{job_id}")
async def stream_results(job_id: str):
    if job_id not in processing_streams:
        raise HTTPException(status_code=404, detail="Job not found")
    
    async def event_generator():
        try:
            while True:
                result = await processing_streams[job_id].get()
                if result == "DONE":
                    break
                yield {
                    "event": "message",
                    "data": json.dumps(result)
                }
        except Exception as e:
            logger.error(f"Error in event generator: {str(e)}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(event_generator())

async def process_file_async(
    job_id: str,
    file: UploadFile,
    provider: str,
    style: str,
    openai_api_key: str,
    gemini_api_key: str
):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            logger.info(f"Created temporary directory: {temp_path}")
            
            # Save uploaded file
            file_path = temp_path / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.info(f"Saved uploaded file to: {file_path}")
            
            # Convert PPTX to PDF
            pdf_dir = temp_path / "pdf"
            pdf_path = pptx_to_pdf(file_path, pdf_dir)
            
            # Convert PDF to images
            images_dir = temp_path / "images"
            image_paths = pdf_to_images(pdf_path, images_dir)
            
            # Process each image
            total_slides = len(image_paths)
            for i, image_path in enumerate(image_paths, 1):
                try:
                    # Extract text
                    text = extract_text(image_path)
                    logger.info(f"Extracted text from slide {i}")
                    
                    # Summarize using selected provider
                    summary = ""
                    if provider == "gemini":
                        summary = summarize_gemini(text, gemini_api_key, settings.GEMINI_MODEL)
                    else:
                        summary = summarize_openai(text, openai_api_key)
                    
                    result = {
                        "slide": i,
                        "text": text,
                        "summary": summary or "[No summary available]"
                    }
                    
                    # Send result to stream
                    await processing_streams[job_id].put(result)
                    logger.info(f"Sent result for slide {i}/{total_slides}")
                    
                except Exception as e:
                    error_msg = f"Failed to process slide {i}: {str(e)}"
                    logger.error(error_msg)
                    await processing_streams[job_id].put({
                        "slide": i,
                        "text": "[Error processing slide]",
                        "summary": f"[Error: {error_msg}]"
                    })
            
            # Signal completion
            await processing_streams[job_id].put("DONE")
            
    except Exception as e:
        error_msg = f"Error in background processing: {str(e)}"
        logger.error(error_msg)
        await processing_streams[job_id].put({
            "event": "error",
            "data": json.dumps({"error": error_msg})
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 