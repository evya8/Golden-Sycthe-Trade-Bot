import React from 'react';
import { Link } from 'react-router-dom';
import { useContext } from 'react';
import { UserContext } from '../contexts/UserContext';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Button from '@mui/material/Button';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { FaHome, FaCog , FaUser} from 'react-icons/fa';
import { Typography ,Box} from '@mui/material';
import ScienceIcon from '@mui/icons-material/Science';

const SideNav = () => {
  const { isAuthenticated } = useContext(UserContext);
  const { user } = useContext(UserContext);
  

  // Create a dark mode theme and customize the button color
  const darkTheme = createTheme({
    palette: {
      mode: 'dark',
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            color: '#b8860b', // Set the text color to #b8860b
            '&:hover': {
              backgroundColor: 'rgba(184, 134, 11, 0.1)', // Add a light hover effect
            },
          },
        },
      },
    },
  });

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <AppBar 
        position="fixed"
        sx={{ 
          width: '180px', // Set width of SideNav
          height: 'calc(100vh - 64px)', // Full screen height minus the Nav height
          flexDirection: 'column', // Stack vertically
          left: 0, // Stick to the left
          top: '64px',  // Start below the Nav (which is typically 64px high)
          zIndex: 1200,  // Ensure it doesn't get overlapped by other components
          backgroundColor: 'inherit', // Inherit background from theme
        }}
      >
        <Toolbar sx={{ flexDirection: 'column', alignItems: 'flex-start', marginTop: '20px' }}>
  {isAuthenticated && (
              <>
          <Button
            sx={{
              display: 'flex', // Align icon and text in a row
              alignItems: 'center',
              backgroundColor: 'transparent', // No background for the entire button
              textTransform: 'none', // Prevent button from capitalizing the text
              padding: '8px 0px', 
            }}
            startIcon={<FaUser />} 
          >
            {/* Border and background wrap only the name */}
            <Box
              sx={{
                border: '1px solid #c9a243',
                borderRadius: 2,
                padding: '4px 8px', // Control padding inside the border
                backgroundColor: '#1c1c1c', // Background only for the name
                color: '#c9a243',
                display: 'inline-block',
              }}
            >
              <Typography
                variant="subtitle1"
                gutterBottom
                sx={{ textTransform: 'uppercase' }} // Convert the name to all caps
              >
                {user ? `${user.first_name} ${user.last_name}` : ''}
              </Typography>
            </Box>
          </Button>

      {/* Dashboard Button */}
      <Button
        color="inherit"
        component={Link}
        to="/user-dashboard"
        startIcon={<FaHome />} // Add the home icon
        sx={{
          fontSize: '1.2rem',
          fontWeight: 'bold',
          textAlign: 'left',
          width: '100%',
          marginTop: '10px',
          textTransform: 'none',
        }}
      >
        Dashboard
      </Button>

      {/* API Keys Button */}
      <Button
        color="inherit"
        component={Link}
        to="/user-settings"
        startIcon={<FaCog />} // Add the cog icon
        sx={{
          fontSize: '1.2rem',
          fontWeight: 'bold',
          textAlign: 'left',
          width: '100%',
          marginTop: '10px',
          textTransform: 'none',
        }}
      >
        API Keys
      </Button>
      <Button
        color="inherit"
        component={Link}
        to="/backtest"
        startIcon={<ScienceIcon />}
        sx={{
          fontSize: '1.3rem',
          fontWeight: 'bold',
          textAlign: 'left',
          width: '100%',
          marginTop: '10px',
          textTransform: 'none',
        }}
      >
        Backtest
      </Button>
    </>
  )}
</Toolbar>

      </AppBar>
    </ThemeProvider>
  );
};

export default SideNav;
