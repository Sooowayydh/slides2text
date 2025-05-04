import React from 'react';
import { Box, Typography, Paper, CircularProgress } from '@mui/material';
import ReactMarkdown from 'react-markdown';

interface SlideResult {
  slide: number;
  text: string;
  summary: string;
}

interface ResultsDisplayProps {
  results: SlideResult[];
  status: 'processing' | 'success';
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results, status }) => {
  if (results.length === 0) return null;

  return (
    <Paper elevation={4} sx={{ p: 4, mb: 4, borderRadius: 4, background: 'rgba(169,181,223,0.95)' }}>
      <Typography variant="h5" color="primary" gutterBottom sx={{ fontWeight: 700 }}>
        Results
      </Typography>
      {results.map((result) => (
        <Box key={result.slide} sx={{ mb: 3 }}>
          <Typography variant="h6" color="primary" gutterBottom>
            Slide {result.slide}
          </Typography>
          <Paper elevation={2} sx={{ p: 2, mb: 2, background: '#FFF2F2' }}>
            <Typography variant="subtitle2" color="primary" gutterBottom>
              Summary:
            </Typography>
            <ReactMarkdown>{result.summary}</ReactMarkdown>
          </Paper>
          <Paper elevation={2} sx={{ p: 2, background: '#FFF2F2' }}>
            <Typography variant="subtitle2" color="primary" gutterBottom>
              Full Text:
            </Typography>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
              {result.text}
            </Typography>
          </Paper>
        </Box>
      ))}
      {status === 'processing' && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 2 }}>
          <CircularProgress size={20} />
          <Typography variant="body2" color="primary">
            Processing more slides...
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default ResultsDisplay; 