import subprocess
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import openai
import google.generativeai as genai
from typing import List, Tuple
import logging
import os
import base64

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

def check_openai_environment():
    """Check environment variables that might affect OpenAI client."""
    env_vars = [
        'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY',
        'OPENAI_API_BASE', 'OPENAI_API_TYPE', 'OPENAI_API_VERSION',
        'OPENAI_ORGANIZATION', 'OPENAI_PROXY'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            logger.warning(f"Environment variable {var} is set: {value}")

def summarize_openai(image_path: Path, api_key: str) -> str:
    """Summarize slide content using OpenAI's o4-mini model."""
    try:
        # Set the API key directly
        openai.api_key = api_key
        
        # Load and encode the image
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        prompt = (
            "This is a slide from a presentation. Please analyze the visual content and text, "
            "and provide a concise 2-3 sentence summary focusing on the key points. "
            "Consider both the text content and any visual elements like diagrams, charts, or images."
        )
        
        response = openai.ChatCompletion.create(
            model="o4-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in summarize_openai: {str(e)}")
        raise

def summarize_gemini(image_path: Path, api_key: str, model: str) -> str:
    """Summarize slide content using Google Gemini's vision capabilities."""
    try:
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        
        genai.configure(api_key=api_key)
        
        # Initialize the model
        model_instance = genai.GenerativeModel(model)
        
        # Load the image
        image = Image.open(image_path)
        
        prompt = (
            "This is a slide from a presentation. Please analyze the visual content and text, "
            "and provide a concise 2-3 sentence summary focusing on the key points. "
            "Consider both the text content and any visual elements like diagrams, charts, or images."
        )
        
        # Generate content with the image
        response = model_instance.generate_content(
            [prompt, image],
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
        )
        
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error in summarize_gemini: {str(e)}")
        raise 