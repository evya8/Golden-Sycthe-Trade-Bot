import React, { useContext, useState, useEffect } from 'react';
import { UserSettingsContext } from '../contexts/UserSettingsContext';
import { UserContext } from '../contexts/UserContext';
import SymbolsFilter from './SymbolsFilter';
import { Box, TextField, Button, Typography, CircularProgress, InputAdornment } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'; 
import { Link } from 'react-router-dom'; 
import { FaCog } from 'react-icons/fa';  
import axiosInstance from '../utils/axiosInstance';
import { toast } from 'react-toastify';
import BotOperations from './BotOperations';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import NewsFeed from './NewsFeed';
import AccountActivity from './AccountActivity';
import BotRunTimer from './BotRunTimer';
import BotPerformance from './BotPerformance';

const UserDashboard = () => {
  const { settings, setSettings, saveUserSettings, loading, error } = useContext(UserSettingsContext);
  const { user } = useContext(UserContext);
  const [positionSize, setPositionSize] = useState(settings?.position_size || 10);
  const [botRunning, setBotRunning] = useState(settings?.bot_active || false);

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

  const darkTheme = createTheme({
    palette: {
      mode: 'dark',
      background: {
        default: '#121212',
        paper: '#1e1e1e',
      },
      primary: {
        main: '#f0a500', 
      },
      success: {
        main: '#66bb6a', // Green for success (activate)
      },
      error: {
        main: '#ff7043', // Orange for error (deactivate)
      },
      text: {
        primary: '#ffffff', // White text
      },
    },
  });

  const hasApiKeys = settings?.alpaca_api_key && settings?.alpaca_api_secret;

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', alignItems: 'center', marginLeft: 10, flexDirection: 'row', width: '90%' }}>
        <Box sx={{ flex: 1, padding: 1 }}>
          {settings && (
            <Box>
              {!hasApiKeys ? (
                <Box
                  sx={{
                    marginLeft: 10,
                    marginRight: 13.5,
                    marginTop: 2,
                    padding: 1,
                    border: '1px solid #c9a243',
                    borderRadius: 1,
                    backgroundColor: 'background.paper',
                  }}
                >
                  <Typography
                    sx={{
                      color: '#c9a243',
                      fontSize: '1.1rem',
                      display: 'flex',
                      alignItems: 'center',
                    }}
                  >
                    <ErrorOutlineIcon sx={{  marginRight: 1 }} />
                    API Keys are required in order to connect the bot to Alpaca Markets platform. Please navigate to the API Keys page to complete the setup.
                  </Typography>

                  <Button
                    component={Link}
                    to="/user-settings"
                    endIcon={<FaCog />}
                    sx={{
                      fontSize: '1rem',
                      fontWeight: 'bold',
                      textAlign: 'left',
                      width: '100%',
                      marginTop: '10px',
                      textTransform: 'none',
                      color: '#c9a243',
                    }}
                  >
                    Or Click Here
                  </Button>
                </Box>
              ) : (
                <Box sx={{ marginTop: 2, marginBottom:7 , display: 'flex', alignItems: 'center' }}>
                  <BotRunTimer />
                  <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    border: '2px solid #333333', 
                    padding: '20px', 
                    borderRadius: '4px',
                    backgroundColor: 'background.paper', 
                    }}>
        
                  <Button
                    variant="contained"
                    color={botRunning ? 'error' : 'success'}
                    onClick={toggleBotActivation}
                    disabled={loading}
                    sx={{
                      padding: '12px 20px',
                      fontSize: '1rem',
                      minWidth: '185px',
                    }}
                  >
                    {botRunning ? 'Deactivate Bot' : 'Activate Bot'}
                  </Button>

                  <Typography sx={{ marginLeft: 5, marginTop: 1.6}}>
                    {botRunning ? 'Bot is activated, click to deactivate' : 'Bot is deactivated, click to activate'}
                  </Typography>
                  </Box>
                </Box>
              )}
                            <SymbolsFilter />

              <Box
                component="form"
                onSubmit={handlePositionSizeSubmit}
                sx={{
                  marginTop: 3,
                  display: 'flex',
                  flexDirection: 'row',
                  gap: 2,
                  border: '2px solid #333333',
                  padding: '20px',
                  borderRadius: '4px',
                  alignItems: 'center',
                  backgroundColor: 'background.paper',
                }}
              >
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
                  sx={{ width: '180px' }}
                />

                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  sx={{ marginLeft: 14, minWidth: '200px' }}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : 'Save Position Size'}
                </Button>

                <Typography
                  sx={{
                    marginLeft: 7,
                    
                    maxWidth: '300px',
                    textAlign: 'right',
                    fontSize: '1rem',
                  }}
                >
                  Position size will determine how much of your capital is invested in each stock.
                </Typography>
              </Box>

              {error && <Typography color="error">{error}</Typography>}
            </Box>
          )}
          <BotOperations />
          <AccountActivity />
          <BotPerformance />
        </Box>

        <Box sx={{ width: '17%', maxWidth: '400px', overflow: 'hidden', marginLeft: 2 }}>
          <NewsFeed />
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default UserDashboard;
