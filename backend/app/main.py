from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import tempfile
import os
import time
from pathlib import Path
import shutil
import asyncio
import logging

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
    allow_origins=["https://slides2text-nphs9ygdx-suveds-projects.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Add middleware to force HTTP/1.1
@app.middleware("http")
async def force_http_1_1(request: Request, call_next):
    response = await call_next(request)
    response.headers["Connection"] = "close"
    return response

class ProcessingRequest(BaseModel):
    provider: str = "openai"  # "openai" or "gemini"
    style: str = "concise"    # "concise", "detailed", or "bullet"

# Store processing status and results
processing_status: Dict[str, Dict] = {}

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
        logger.info(f"Created processing job with ID: {job_id}")
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            logger.info(f"Created temporary directory: {temp_path}")
            
            # Save uploaded file
            file_path = temp_path / file.filename
            try:
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                logger.info(f"Saved uploaded file to: {file_path}")
            except Exception as e:
                error_msg = f"Failed to save uploaded file: {str(e)}"
                logger.error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)
            
            # Convert PPTX to PDF
            pdf_dir = temp_path / "pdf"
            try:
                logger.info(f"Starting PPTX to PDF conversion for {file_path}")
                pdf_path = pptx_to_pdf(file_path, pdf_dir)
                logger.info(f"Successfully converted to PDF: {pdf_path}")
            except Exception as e:
                error_msg = f"Failed to convert PPTX to PDF: {str(e)}"
                logger.error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)
            
            # Convert PDF to images
            images_dir = temp_path / "images"
            try:
                logger.info(f"Starting PDF to images conversion for {pdf_path}")
                image_paths = pdf_to_images(pdf_path, images_dir)
                logger.info(f"Successfully converted to {len(image_paths)} images")
            except Exception as e:
                error_msg = f"Failed to convert PDF to images: {str(e)}"
                logger.error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)
            
            # Process each image
            results = []
            total_slides = len(image_paths)
            logger.info(f"Starting to process {total_slides} slides")
            
            for i, image_path in enumerate(image_paths, 1):
                try:
                    logger.info(f"Processing slide {i}/{total_slides}")
                    
                    # Extract text
                    text = extract_text(image_path)
                    logger.info(f"Extracted text from slide {i}")
                    
                    # Summarize using selected provider
                    summary = ""
                    if provider == "gemini":
                        try:
                            logger.info(f"Generating Gemini summary for slide {i}")
                            summary = summarize_gemini(
                                text,
                                gemini_api_key,
                                settings.GEMINI_MODEL
                            )
                            logger.info(f"Generated Gemini summary for slide {i}")
                        except Exception as e:
                            error_msg = f"Gemini summarization failed for slide {i}: {str(e)}"
                            logger.warning(error_msg)
                            summary = f"[Error: {error_msg}]"
                    else:
                        try:
                            logger.info(f"Generating OpenAI summary for slide {i}")
                            summary = summarize_openai(text, openai_api_key)
                            logger.info(f"Generated OpenAI summary for slide {i}")
                        except Exception as e:
                            error_msg = f"OpenAI summarization failed for slide {i}: {str(e)}"
                            logger.warning(error_msg)
                            summary = f"[Error: {error_msg}]"
                    
                    results.append({
                        "slide": i,
                        "text": text,
                        "summary": summary or "[No summary available]"
                    })
                    logger.info(f"Completed processing slide {i}/{total_slides}")
                    
                except Exception as e:
                    error_msg = f"Failed to process slide {i}: {str(e)}"
                    logger.error(error_msg)
                    results.append({
                        "slide": i,
                        "text": "[Error processing slide]",
                        "summary": f"[Error: {error_msg}]"
                    })
            
            # Update final status
            processing_status[job_id]["status"] = "completed"
            processing_status[job_id]["progress"] = 100
            processing_status[job_id]["message"] = "Processing completed successfully"
            processing_status[job_id]["results"] = results
            
            logger.info(f"Processing completed successfully for job {job_id}")
            return JSONResponse(content={
                "status": "success",
                "progress": 100,
                "message": "Processing completed successfully",
                "results": results
            })
            
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

async def process_file(
    pptx_path: Path,
    work_dir: Path,
    job_id: str,
    provider: str,
    style: str
):
    try:
        # Update status
        processing_status[job_id]["status"] = "processing"
        processing_status[job_id]["message"] = "Converting to PDF..."
        
        # Convert to PDF
        pdf_dir = work_dir / "pdf"
        pdf_file = pptx_to_pdf(pptx_path, pdf_dir)
        
        # Update status
        processing_status[job_id]["progress"] = 20
        processing_status[job_id]["message"] = "Converting PDF to images..."
        
        # Convert PDF to images
        img_dir = work_dir / "images"
        slides = pdf_to_images(pdf_file, img_dir)
        
        # Process each slide
        total_slides = len(slides)
        for idx, slide_img in enumerate(sorted(slides), start=1):
            # Update status
            progress = 20 + (idx / total_slides * 60)
            processing_status[job_id]["progress"] = int(progress)
            processing_status[job_id]["message"] = f"Processing slide {idx}/{total_slides}..."
            
            # Extract text
            raw_text = extract_text(slide_img)
            
            # Get summary based on provider and style
            try:
                if provider == "gemini":
                    summary = summarize_gemini(
                        raw_text,
                        settings.GEMINI_API_KEY,
                        settings.GEMINI_MODEL
                    )
                else:
                    summary = summarize_openai(raw_text, settings.OPENAI_API_KEY)
                
                # Store result
                processing_status[job_id]["results"].append({
                    "slide_num": idx,
                    "summary": summary,
                    "raw_text": raw_text
                })
                
            except Exception as e:
                processing_status[job_id]["results"].append({
                    "slide_num": idx,
                    "summary": f"Error: {str(e)}",
                    "raw_text": raw_text
                })
            
            # Add delay between API calls
            await asyncio.sleep(settings.PROCESSING_DELAY)
        
        # Update final status
        processing_status[job_id]["status"] = "completed"
        processing_status[job_id]["progress"] = 100
        processing_status[job_id]["message"] = "Processing complete!"
        
    except Exception as e:
        processing_status[job_id]["status"] = "error"
        processing_status[job_id]["message"] = str(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 