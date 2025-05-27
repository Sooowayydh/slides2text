# PPT2Doc

A web application that converts PowerPoint presentations into detailed text documents using AI vision models.

## Purpose

PPT2Doc solves the challenge of converting PowerPoint presentations into text-based formats that can be effectively processed by language models and other text-based systems. While PowerPoint is excellent for visual storytelling and human audiences, its content is difficult to process through traditional text scraping methods because:

- Slides often contain minimal text, relying on visual elements to convey information
- Charts, graphs, and visual elements lose their semantic meaning when converted to plain text
- Traditional text extraction misses the rich context and relationships between visual elements
- The format is not ideal for retrieval augmented generation (RAG) systems that primarily work with text

PPT2Doc bridges this gap by using AI vision models to:
- Accurately transcribe all text content from slides
- Provide detailed descriptions of visual elements like charts and graphs
- Preserve the semantic relationships between different elements
- Generate text that maintains the original meaning and context

## Pipeline

1. **Input**: User uploads a PowerPoint (.pptx) file
2. **Processing**:
   - PowerPoint is converted to PDF using LibreOffice
   - PDF is converted to individual PNG images (one per slide)
   - Each slide image is processed by AI vision model (OpenAI o4-mini or Google Gemini)
   - AI model transcribes text and describes visual elements
3. **Output**: Generated text document containing transcribed content from all slides

## Tech Stack

### Frontend
- React with TypeScript
- Tailwind CSS for styling
- Vite for build tooling

### Backend
- FastAPI (Python)
- OpenAI API (o4-mini model)
- Google Gemini API
- LibreOffice for PPTX to PDF conversion
- pdf2image for PDF to PNG conversion
- Docker for containerization

## Features

- Upload PowerPoint (.ppt, .pptx) files
- Convert slides to text using OCR
- Generate AI-powered summaries using either:
  - OpenAI GPT-3.5 Turbo
  - Google Gemini AI
- Real-time processing status updates
- Modern, responsive UI
- Support for both concise and detailed summaries



