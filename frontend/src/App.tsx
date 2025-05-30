import { useState } from 'react';
import { Container, CssBaseline, ThemeProvider, createTheme, Typography, Box, Divider, Stack } from '@mui/material';
import FileUpload from './components/FileUpload';
import ResultsDisplay from './components/ResultsDisplay';
import SettingsPanel from './components/SettingsPanel';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#2D336B' },
    secondary: { main: '#7886C7' },
    background: {
      default: '#FFF2F2',
      paper: 'rgba(169,181,223,0.95)',
    },
    text: {
      primary: '#2D336B',
      secondary: '#7886C7',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
    h3: { fontWeight: 800, letterSpacing: 1 },
    h5: { fontWeight: 700 },
    h6: { fontWeight: 700 },
    subtitle1: { fontWeight: 400 },
    button: { fontWeight: 700, textTransform: 'none' },
  },
  shape: {
    borderRadius: 18,
  },
});

interface SlideResult {
  slide: number;
  text: string;
  summary: string;
}

function App() {
  const [results, setResults] = useState<SlideResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [provider, setProvider] = useState<'openai' | 'gemini'>('openai');
  const [openaiKey, setOpenaiKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [processingStatus, setProcessingStatus] = useState<'processing' | 'success'>('processing');
  const [model, setModel] = useState('o4-mini');

  const handleProviderChange = (newProvider: string) => {
    setProvider(newProvider as 'openai' | 'gemini');
    // Update model based on provider
    setModel(newProvider === 'openai' ? 'o4-mini' : 'gemini-2.5-flash-preview-04-17');
  };

  const handleUploadComplete = (data: any) => {
    if (data.status === 'processing') {
      setResults(data.results);
      setProcessingStatus('processing');
    } else if (data.status === 'success') {
      setResults(data.results);
      setProcessingStatus('success');
    }
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
  };

  // Only enable upload if the correct API key is present
  const apiKey = provider === 'openai' ? openaiKey : geminiKey;
  const canUpload = !!apiKey;

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {/* Full viewport background gradient */}
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          zIndex: -1,
          background: 'linear-gradient(135deg, #FFF2F2 0%, #A9B5DF 100%)',
        }}
      />
      {/* Main content */}
      <Box sx={{ position: 'relative', zIndex: 1, minHeight: '100vh' }}>
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Box sx={{ mb: 4, textAlign: 'center' }}>
            <Typography variant="h2" component="h1" color="primary" gutterBottom sx={{ fontWeight: 800, letterSpacing: 1 }}>
              📑 Slide Summarizer
            </Typography>
            <Typography variant="h6" color="secondary" gutterBottom>
              Transform your presentations into concise summaries
            </Typography>
          </Box>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={4} sx={{ mb: 4 }}>
            <Box sx={{ width: { xs: '100%', md: '58.33%' } }}>
              <FileUpload
                onUploadComplete={handleUploadComplete}
                onError={handleError}
                provider={provider}
                apiKey={apiKey}
                canUpload={canUpload}
                model={model}
              />
              {error && (
                <div style={{ marginTop: '1rem', color: '#d32f2f', fontWeight: 600 }}>{error}</div>
              )}
            </Box>
            <Box sx={{ width: { xs: '100%', md: '41.67%' } }}>
              <SettingsPanel
                provider={provider}
                onProviderChange={handleProviderChange}
                openaiKey={openaiKey}
                onOpenaiKeyChange={setOpenaiKey}
                geminiKey={geminiKey}
                onGeminiKeyChange={setGeminiKey}
                model={model}
                onModelChange={setModel}
              />
            </Box>
          </Stack>
          {results.length > 0 && (
            <ResultsDisplay results={results} status={processingStatus} />
          )}
          <Divider sx={{ my: 6, borderColor: '#A9B5DF' }} />
          <Box sx={{ textAlign: 'center', color: '#7886C7', fontSize: 15, mb: 2 }}>
            Made with ❤️ by Suved Ganduri &middot; <a href="https://github.com/Sooowayydh/slides2text" style={{ color: '#2D336B', textDecoration: 'underline' }} target="_blank" rel="noopener noreferrer">GitHub</a>
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;