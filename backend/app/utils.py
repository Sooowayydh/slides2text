import subprocess
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import openai
import google.generativeai as genai
from typing import List, Tuple
import logging
import os
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def pptx_to_pdf(pptx_path: Path, out_dir: Path) -> Path:
    """Convert PPTX to PDF using LibreOffice headless."""
    try:
        # Check if LibreOffice is installed
        result = subprocess.run(["which", "soffice"], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("LibreOffice is not installed. Please install it using 'apt-get install libreoffice'")
        
        # Create output directory if it doesn't exist
        out_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Converting {pptx_path} to PDF in {out_dir}")
        
        # Get absolute paths
        pptx_abs = pptx_path.absolute()
        out_dir_abs = out_dir.absolute()
        
        # Run LibreOffice conversion
        result = subprocess.run([
            "soffice", "--headless", "--convert-to", "pdf",
            "--outdir", str(out_dir_abs), str(pptx_abs)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"LibreOffice conversion failed: {result.stderr}")
            raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")
        
        # Get the output PDF path
        pdf_path = out_dir_abs / pptx_path.with_suffix('.pdf').name
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not created at {pdf_path}")
        
        logger.info(f"Successfully converted to PDF: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Error in pptx_to_pdf: {str(e)}")
        raise

def pdf_to_images(pdf_path: Path, out_dir: Path) -> List[Path]:
    """Rasterize each PDF page to a PNG image."""
    try:
        # Create output directory if it doesn't exist
        out_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Converting PDF {pdf_path} to images in {out_dir}")
        
        # Get absolute paths
        pdf_abs = pdf_path.absolute()
        out_dir_abs = out_dir.absolute()
        
        # Convert PDF to images
        pil_images = convert_from_path(
            str(pdf_abs),
            dpi=200,
            output_folder=str(out_dir_abs),
            fmt="png"
        )
        
        if not pil_images:
            raise RuntimeError("No images were generated from the PDF")
        
        image_paths = [Path(img.filename) for img in pil_images]
        logger.info(f"Successfully converted to {len(image_paths)} images")
        return image_paths
        
    except Exception as e:
        logger.error(f"Error in pdf_to_images: {str(e)}")
        raise

def extract_text(image_path: Path) -> str:
    """Use Tesseract OCR to extract text from a slide image."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img).strip()
        logger.info(f"Extracted text from {image_path}")
        return text
    except Exception as e:
        logger.error(f"Error in extract_text: {str(e)}")
        raise

def summarize_openai(text: str, api_key: str) -> str:
    """Summarize text using OpenAI's API."""
    try:
        # Initialize OpenAI client with just the API key
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text concisely."},
                {"role": "user", "content": f"Please summarize the following text concisely:\n\n{text}"}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in summarize_openai: {str(e)}")
        raise

def summarize_gemini(raw_text: str, api_key: str, model: str) -> str:
    """Summarize extracted text via Google Gemini API."""
    try:
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        
        genai.configure(api_key=api_key)
        
        if not raw_text:
            return "[No text detected]"
        
        model_instance = genai.GenerativeModel(model)
        prompt = (
            "Below is OCR-extracted text from a slide. "
            "Provide a concise 2-3 sentence summary focusing on key points:\n\n" + raw_text
        )
        response = model_instance.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error in summarize_gemini: {str(e)}")
        raise 