import React from 'react';
import { Typography, RadioGroup, FormControlLabel, Radio, TextField, Paper } from '@mui/material';

interface SettingsPanelProps {
  provider: string;
  onProviderChange: (provider: string) => void;
  openaiKey: string;
  onOpenaiKeyChange: (key: string) => void;
  geminiKey: string;
  onGeminiKeyChange: (key: string) => void;
  model: string;
  onModelChange: (model: string) => void;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({
  provider,
  onProviderChange,
  openaiKey,
  onOpenaiKeyChange,
  geminiKey,
  onGeminiKeyChange,
  model,
  onModelChange,
}) => {
  return (
    <Paper elevation={4} sx={{ p: 4, mb: 4, borderRadius: 4, background: 'rgba(169,181,223,0.95)', boxShadow: '0 4px 24px rgba(45, 51, 107, 0.10)' }}>
      <Typography variant="h6" color="primary" fontWeight={700} gutterBottom>
        Settings
      </Typography>
      <Typography variant="subtitle2" color="secondary" gutterBottom>
        Select AI Provider
      </Typography>
      <RadioGroup
        row
        value={provider}
        onChange={e => onProviderChange(e.target.value)}
        sx={{ mb: 2 }}
      >
        <FormControlLabel value="openai" control={<Radio sx={{ color: '#2D336B', '&.Mui-checked': { color: '#2D336B' } }} />} label="OpenAI GPT" />
        <FormControlLabel value="gemini" control={<Radio sx={{ color: '#2D336B', '&.Mui-checked': { color: '#2D336B' } }} />} label="Google Gemini" />
      </RadioGroup>
      {provider === 'openai' ? (
        <>
          <TextField
            label="OpenAI API Key"
            type="password"
            value={openaiKey}
            onChange={e => onOpenaiKeyChange(e.target.value)}
            fullWidth
            margin="normal"
            sx={{ background: '#FFF2F2', borderRadius: 2 }}
          />
          <TextField
            label="OpenAI Model"
            value={model}
            onChange={e => onModelChange(e.target.value)}
            fullWidth
            margin="normal"
            sx={{ background: '#FFF2F2', borderRadius: 2 }}
          />
        </>
      ) : (
        <>
          <TextField
            label="Gemini API Key"
            type="password"
            value={geminiKey}
            onChange={e => onGeminiKeyChange(e.target.value)}
            fullWidth
            margin="normal"
            sx={{ background: '#FFF2F2', borderRadius: 2 }}
          />
          <TextField
            label="Gemini Model"
            value={model}
            onChange={e => onModelChange(e.target.value)}
            fullWidth
            margin="normal"
            sx={{ background: '#FFF2F2', borderRadius: 2 }}
          />
        </>
      )}
    </Paper>
  );
};

export default SettingsPanel; 