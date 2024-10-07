import React, { useContext, useState, useEffect } from 'react';
import { UserSettingsContext } from '../contexts/UserSettingsContext';
import { UserContext } from '../contexts/UserContext';
import SymbolsFilter from './SymbolsFilter';
import { Box, TextField, Button, Typography, CircularProgress, InputAdornment } from '@mui/material';
import axiosInstance from '../utils/axiosInstance';
import { toast } from 'react-toastify';
import BotOperations from './BotOperations';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import NewsFeed from './NewsFeed';
import AccountActivity from './AccountActivity';


const UserDashboard = () => {
  const { settings, setSettings, saveUserSettings, loading, error } = useContext(UserSettingsContext);
  const { user } = useContext(UserContext);
  const [positionSize, setPositionSize] = useState(settings?.position_size || 10);
  const [botRunning, setBotRunning] = useState(settings?.bot_active || false);

  // Fetch the initial bot status when the component mounts
  useEffect(() => {
    if (settings) {
      setPositionSize(settings.position_size);
      setBotRunning(settings.bot_active);
    }
  }, [settings]);

  const handlePositionSizeChange = (e) => {
    const value = parseInt(e.target.value, 10);
    if (value >= 0 && value % 5 === 0) {
      setPositionSize(value);
    }
  };

  const handlePositionSizeSubmit = (e) => {
    e.preventDefault();
    const updatedSettings = { ...settings, position_size: positionSize };
    setSettings(updatedSettings);
    saveUserSettings(updatedSettings);
  };

  const toggleBotActivation = () => {
    const userId = user?.id;

    if (!userId) {
      toast.error('User ID not found.');
      return;
    }

    axiosInstance.post('/toggle-bot/', { user_id: userId })
      .then(response => {
        setBotRunning(prevState => !prevState);
        toast.success(`Bot ${botRunning ? 'deactivated' : 'activated'} successfully.`);
      })
      .catch(error => {
        toast.error(`Error trying to ${botRunning ? 'activate' : 'deactivate'} the bot.`);
        console.error(`Error toggling bot:`, error.response?.data?.error);
      });
  };

  // Create a dark mode theme
  const darkTheme = createTheme({
    palette: {
      mode: 'dark',
    },
  });

  // Check if API keys are present in the settings
  const hasApiKeys = settings?.alpaca_api_key && settings?.alpaca_api_secret;


  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline /> 
      {/* Flex container for main content and news feed */}
      <Box sx={{ display: 'flex', flexDirection: 'row', width: '100%' }}>
        {/* Main content area */}
        <Box sx={{ flex: 1, padding: 2 }}>
          {settings && (
            <Box>
              {!hasApiKeys ? (
                <Typography sx={{ marginLeft: 43, marginTop: 2, color: '#c9a243' }}>
                  API Keys Not Found. Please Go To API Keys Page And Follow Instructions
                </Typography>
              ) : (
                <Box sx={{ marginLeft: 43, marginTop: 2, display: 'flex', alignItems: 'center' }}>
                  <Button
                    variant="contained"
                    color={botRunning ? 'error' : 'success'}
                    onClick={toggleBotActivation}
                    disabled={loading}
                    sx={{
                      padding: '12px 24px', // Adjust padding for larger button
                      fontSize: '1.25rem',   // Adjust font size for larger text
                      minWidth: '200px',     // Set a minimum width to make it larger horizontally
                    }}
                  >
                    {botRunning ? 'Deactivate Bot' : 'Activate Bot'}
                  </Button>

                  <Typography sx={{ marginLeft: 5, color: '#c9a243' }}>
                    {botRunning ? 'Bot is activated, click to deactivate' : 'Bot is deactivated, click to activate'}
                  </Typography>
                </Box>
              )}
              <Box
  component="form"
  onSubmit={handlePositionSizeSubmit}
  sx={{
    marginTop: 3,
    display: 'flex',
    flexDirection: 'row', // Keep elements in a row
    gap: 2,
    border: '2px solid #333333',
    padding: '20px',
    borderRadius: '4px',
    alignItems: 'center', // Ensure vertical alignment
    // justifyContent: 'space-between', // Spread items horizontally
  }}
>
  {/* TextField for Position Size */}
  <TextField
    label="Position Size"
    type="number"
    value={positionSize}
    onChange={handlePositionSizeChange}
    InputProps={{
      inputProps: {
        min: 5,
        max: 100,
        step: 5,
        style: { textAlign: 'center' },
      },
      endAdornment: <InputAdornment position="end">%</InputAdornment>,
    }}
    sx={{ width: '110px' }} // Keep the original width
  />

  {/* Save Button */}
  <Button
    type="submit"
    variant="contained"
    color="primary"
    sx={{ marginLeft: 1, minWidth: '150px' }} // Adjust button size
    disabled={loading}
  >
    {loading ? <CircularProgress size={24} /> : 'Save Position Size'}
  </Button>
  
  {/* Typography comment wrapped in two rows */}
  <Typography
    sx={{
      marginLeft: 32,
      color: '#c9a243',
      maxWidth: '300px', // Limit width to wrap text in two lines
      textAlign: 'right', // Align the text to the right
      fontSize: '1rem', // Keep the font size normal
    }}
  >
    Position size will determine how much of your capital is invested in each stock.
  </Typography>
</Box>

              {error && <Typography color="error">{error}</Typography>}
              <SymbolsFilter />
            </Box>
          )}
          <BotOperations />
          <AccountActivity />
        </Box>

        {/* NewsFeed area */}
        <Box sx={{ width: '17%', maxWidth: '400px', overflow: 'hidden', marginLeft: 2 }}>
          <NewsFeed />
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default UserDashboard;