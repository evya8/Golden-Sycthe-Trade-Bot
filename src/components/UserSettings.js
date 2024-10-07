import React, { useContext, useState, useEffect } from 'react';
import { UserSettingsContext } from '../contexts/UserSettingsContext';
import { Box, TextField, Button, Typography } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const UserSettings = () => {
  const { settings, saveUserSettings, loading, error } = useContext(UserSettingsContext);
  const [formData, setFormData] = useState({
    alpaca_api_key: '',
    alpaca_api_secret: '',
  });

  // Populate formData with settings when settings are fetched
  useEffect(() => {
    if (settings) {
      setFormData((prevFormData) => ({
        ...prevFormData,
        alpaca_api_key: settings.alpaca_api_key || '',
        alpaca_api_secret: settings.alpaca_api_secret || '',
      }));
    }
  }, [settings]);

  // Handle form input changes
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.alpaca_api_key && formData.alpaca_api_secret) {
      saveUserSettings(formData);
    } else {
      alert("Please provide both API key and secret.");
    }
  };

  // Create a dark mode theme
  const darkTheme = createTheme({
    palette: {
      mode: 'dark',
    },
  });

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ padding: 2 }}>
        {/* Instructions on how to sign up for Alpaca and generate API keys */}
        <Typography variant="h4" gutterBottom color= "#c9a243" align='center'>
          How to Sign Up for Alpaca and Generate API Keys:
        </Typography>
        <Typography variant="body1" sx={{ marginLeft: 2 , marginTop: 4}} paragraph color= "#c9a243">
          Step 1: Go to the Alpaca website <a href="https://alpaca.markets/" target="_blank" rel="noopener noreferrer">https://alpaca.markets/</a> Signup for free and verify your account.
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        <img 
          src="https://miro.medium.com/v2/resize:fit:1400/format:webp/1*AP8mWEIQTxUQEX_WsXQiAQ.png" 
          alt="Alpaca Login Screenshot" 
          style={{ width: '80%', height: 'auto', marginBottom: '20px' }} 
        />
        </Box>
        <Typography variant="body1" sx={{ marginLeft: 2 , marginTop: 4 }} paragraph color= "#c9a243">
          Step 2: Once you log in, go to your paper account.
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        <img 
          src="https://miro.medium.com/v2/resize:fit:1400/format:webp/1*FNagpZKY-0wHrCDR2FL5Bg.png" 
          alt="Alpaca API Keys Screenshot" 
          style={{ width: '80%', height: 'auto', marginBottom: '20px' }} 
        />
        </Box>
        <Typography variant="body1" sx={{ marginLeft: 2 , marginTop: 4}} paragraph color= "#c9a243">
          Step 3: Your API Key and API Secret will be located on the right side of the screen. Click on 'View.'
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        <img 
          src="https://miro.medium.com/v2/resize:fit:1400/format:webp/1*b0w_DchW85gRfsNbI3L5tQ.png" 
          alt="Generate New Key Screenshot" 
          style={{ width: '80%', height: 'auto', marginBottom: '20px' }} 
        />
        </Box>
        <Typography variant="body1" sx={{ marginLeft: 2 , marginTop: 4}} paragraph color= "#c9a243">
          Step 4: If you haven’t generated your API Key and Secret yet, a "Generate New Key" option will be available. Click to generate them.
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        <img 
          src="https://miro.medium.com/v2/resize:fit:972/format:webp/1*MNxtlihw_urHm30Zpyes2w.png" 
          alt="API Key and Secret Screenshot" 
          style={{ width: '50%', height: 'auto', marginBottom: '20px' }} 
        />
        </Box>
        <Typography variant="body1" sx={{ marginLeft: 2 , marginTop: 4 }} paragraph color="#c9a243">
          Step 5: Once you generate the API Keys,an API Key ID and Secret Key will appear. <br/><br/>
          <strong>Please copy both of these into the form fields and save them.</strong> <br/>
          
        </Typography>

        {/* The form for entering API keys */}
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex',width: '35%', flexDirection: 'column',marginTop: 5,marginLeft: 5, gap: 2 }}>
          <TextField
            label="Alpaca API Key"
            name="alpaca_api_key"
            value={formData.alpaca_api_key}
            onChange={handleChange}
            variant="outlined"
            fullWidth
            required
            type="password"
          />
          <TextField
            label="Alpaca API Secret"
            name="alpaca_api_secret"
            value={formData.alpaca_api_secret}
            onChange={handleChange}
            variant="outlined"
            fullWidth
            required
            type="password"
          />
          <Button type="submit" variant="contained" color="primary" disabled={loading}>
            Save Keys
          </Button>
          {error && <Typography color="error">{error}</Typography>}
        </Box>

        <Typography variant="body1" sx={{ marginLeft: 2 , marginTop: 4 }} paragraph color= "#c9a243">
        DO NOT share your API keys and secrets with anyone.
        </Typography>
      </Box>
    </ThemeProvider>
  );
};

export default UserSettings;
