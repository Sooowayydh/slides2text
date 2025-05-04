import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, CircularProgress, Alert, Button, Paper } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

interface FileUploadProps {
  onUploadComplete: (results: any) => void;
  onError: (error: string) => void;
  provider: string;
  apiKey: string;
  canUpload: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete, onError, provider, apiKey, canUpload }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileInfo, setFileInfo] = useState<{ name: string; size: number } | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;
    setSelectedFile(file);
    setFileInfo({ name: file.name, size: file.size });
    setError(null);
  }, []);

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('provider', provider);
      formData.append('style', 'concise');
      if (provider === 'openai') {
        formData.append('openai_api_key', apiKey);
      } else if (provider === 'gemini') {
        formData.append('gemini_api_key', apiKey);
      }
      const response = await axios.post('https://slides2text-backend.onrender.com/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Accept': 'application/json'
        },
        timeout: 60000, // Increase timeout to 60 seconds
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
        validateStatus: function (status) {
          return status >= 200 && status < 500; // Accept all status codes less than 500
        },
        maxRedirects: 0,
        decompress: true,
        withCredentials: false // Disable credentials
      });

      console.log('Response received:', response.data); // Add logging

      if (response.status >= 400) {
        throw new Error(response.data?.detail || 'Server error occurred');
      }

      if (!response.data || !response.data.results) {
        throw new Error('Invalid response format from server');
      }

      onUploadComplete(response.data);
    } catch (err) {
      console.error('Upload error:', err); // Add error logging
      let errorMessage = 'An error occurred during upload';
      if (axios.isAxiosError(err)) {
        if (err.response) {
          errorMessage = err.response.data?.detail || err.response.statusText || 'Server error occurred';
          console.error('Server response:', err.response.data); // Add response logging
        } else if (err.request) {
          errorMessage = 'No response received from server';
          console.error('No response received'); // Add request logging
        } else {
          errorMessage = err.message;
        }
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      setError(errorMessage);
      onError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.ms-powerpoint': ['.ppt'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
    },
    maxFiles: 1,
  });

  return (
    <Paper elevation={4} sx={{ p: 4, mb: 4, borderRadius: 4, background: 'rgba(169,181,223,0.95)', boxShadow: '0 4px 24px rgba(45, 51, 107, 0.10)' }}>
      <Box
        {...getRootProps()}
        sx={{
          border: '2.5px dashed #7886C7',
          borderRadius: 3,
          p: 4,
          textAlign: 'center',
          cursor: 'pointer',
          minHeight: 220,
          transition: 'background-color 0.2s, border-color 0.2s',
          backgroundColor: isDragActive ? '#A9B5DF' : '#FFF2F2',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          '&:hover': {
            backgroundColor: '#A9B5DF',
            borderColor: '#2D336B',
          },
        }}
      >
        <input {...getInputProps()} />
        {isUploading ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <CircularProgress color="secondary" />
            <Typography color="primary">Processing your presentation...</Typography>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <CloudUploadIcon sx={{ fontSize: 56, color: '#2D336B' }} />
            <Typography variant="h6" color="primary" fontWeight={700}>
              {isDragActive
                ? 'Drop the PowerPoint file here'
                : 'Drag and drop a PowerPoint file here, or click to select'}
            </Typography>
            <Typography variant="body2" color="#7886C7">
              Supported formats: .ppt, .pptx
            </Typography>
          </Box>
        )}
      </Box>
      {fileInfo && (
        <Box sx={{ mt: 2, textAlign: 'left' }}>
          <Typography variant="subtitle2" color="primary">File Information:</Typography>
          <Typography variant="body2">- Name: {fileInfo.name}</Typography>
          <Typography variant="body2">- Size: {(fileInfo.size / 1024).toFixed(1)} KB</Typography>
        </Box>
      )}
      <Box sx={{ mt: 2 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<CloudUploadIcon />}
          fullWidth
          sx={{ py: 1.5, fontWeight: 600, fontSize: '1.1rem', borderRadius: 2, background: '#2D336B', '&:hover': { background: '#7886C7' } }}
          disabled={!selectedFile || !canUpload || isUploading}
          onClick={handleUpload}
        >
          Summarize Slides
        </Button>
        {!canUpload && (
          <Typography variant="body2" color="#d32f2f" sx={{ mt: 1 }}>
            Please provide a {provider === 'openai' ? 'OpenAI' : 'Gemini'} API key in the Settings panel.
          </Typography>
        )}
      </Box>
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Paper>
  );
};

export default FileUpload; 