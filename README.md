# PPT to Doc Converter

A web application that converts PowerPoint presentations into summarized documents using AI. The application supports both OpenAI and Google Gemini AI models for generating summaries.

## Features

- Upload PowerPoint (.ppt, .pptx) files
- Convert slides to text using OCR
- Generate AI-powered summaries using either:
  - OpenAI GPT-3.5 Turbo
  - Google Gemini AI
- Real-time processing status updates
- Modern, responsive UI
- Support for both concise and detailed summaries

## Tech Stack

### Frontend
- React
- Material-UI
- TypeScript
- Axios for API calls
- React Dropzone for file uploads

### Backend
- FastAPI
- Python 3.11
- OpenAI API (v0.28.0)
- Google Gemini AI API
- LibreOffice for PPT to PDF conversion
- Tesseract OCR for text extraction
- PDF2Image for PDF processing

## Prerequisites

- Node.js and npm (for frontend)
- Python 3.11 (for backend)
- LibreOffice
- Tesseract OCR
- Poppler Utils

## Local Development Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Docker Deployment

### Backend

1. Build the Docker image:
   ```bash
   cd backend
   docker build -t ppt2doc-backend .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 ppt2doc-backend
   ```

## Environment Variables

### Backend
Create a `.env` file in the backend directory with:
```
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### Frontend
Create a `.env` file in the frontend directory with:
```
REACT_APP_API_URL=http://localhost:8000
```

## API Endpoints

- `POST /upload`: Upload a PowerPoint file
  - Parameters:
    - `file`: PowerPoint file (.ppt, .pptx)
    - `provider`: "openai" or "gemini"
    - `style`: "concise" or "detailed"
    - `openai_api_key`: OpenAI API key (if using OpenAI)
    - `gemini_api_key`: Gemini API key (if using Gemini)

- `GET /status/{job_id}`: Check processing status
- `GET /stream/{job_id}`: Stream processing results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request


