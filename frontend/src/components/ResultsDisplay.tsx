import React, { useState } from 'react';
import { Box, Typography, Paper, Divider, Button, Collapse } from '@mui/material';
import ReactMarkdown from 'react-markdown';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';

interface SlideResult {
  slide: number;
  text: string;
  summary: string;
}

interface ResultsDisplayProps {
  results: SlideResult[];
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  const [openIndexes, setOpenIndexes] = useState<{ [key: number]: boolean }>({});

  const handleToggle = (idx: number) => {
    setOpenIndexes((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5" color="primary" fontWeight={700} gutterBottom>
        Presentation Summary
      </Typography>
      {results.map((result, index) => (
        <Paper
          key={result.slide}
          elevation={4}
          sx={{
            p: 4,
            mb: 4,
            borderRadius: 4,
            background: 'rgba(169,181,223,0.95)',
            boxShadow: '0 4px 24px rgba(45, 51, 107, 0.10)',
          }}
        >
          <Typography variant="h6" color="primary" fontWeight={700} gutterBottom>
            Slide {result.slide}
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Button
              variant={openIndexes[index] ? 'contained' : 'outlined'}
              color="secondary"
              size="small"
              onClick={() => handleToggle(index)}
              sx={{ mb: 1, borderRadius: 2, fontWeight: 600 }}
              startIcon={openIndexes[index] ? <VisibilityOffIcon /> : <VisibilityIcon />}
            >
              {openIndexes[index] ? 'Hide Extracted Text' : 'Show Extracted Text'}
            </Button>
            <Collapse in={!!openIndexes[index]}>
              <Typography variant="subtitle2" color="secondary" gutterBottom>
                Extracted Text:
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', color: '#2D336B' }}>
                {result.text}
              </Typography>
            </Collapse>
          </Box>
          <Divider sx={{ my: 2, borderColor: '#7886C7' }} />
          <Box>
            <Typography variant="subtitle2" color="secondary" gutterBottom>
              Summary:
            </Typography>
            <ReactMarkdown>{result.summary}</ReactMarkdown>
          </Box>
        </Paper>
      ))}
    </Box>
  );
};

export default ResultsDisplay; 