import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useContext } from 'react';
import { UserContext } from '../contexts/UserContext';
import LogoutButton from './LogoutButton';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Button from '@mui/material/Button';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import TopMarketMovers from './TopMarketMovers';

const Nav = ({ isHomePage }) => {
  const { isAuthenticated } = useContext(UserContext);
  const location = useLocation();

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
      <AppBar position="fixed" sx={{ zIndex: 1300 }}>
        <Toolbar>
          {/* "Golden Sycthe" Button */}
          <Button
            color="inherit"
            component={Link}
            to={isAuthenticated ? "/user-dashboard" : "/"}
            sx={{
              fontSize: '1.5rem',
              fontWeight: 'bold',
              color: '#f0a500', // Gold color for the title
            }}
          >
            Golden Sycthe
          </Button>
          {/* Conditionally show login and register links when on Home page */}
          {isHomePage && !isAuthenticated && (
            <>
              <Button color="inherit" component={Link} to="/register">
                Register
              </Button>
              <Button color="inherit" component={Link} to="/login">
                Login
              </Button>
            </>
          )}
          {/* Conditionally render Top Market Movers only on the /user-dashboard page */}
          {location.pathname === '/user-dashboard' && (
            <div style={{ flexGrow: 1, maxWidth: '75%', marginLeft: 'auto' }}>
              <TopMarketMovers marketType="stocks" top={10} />
            </div>
          )}
          {/* Show logout if authenticated */}
          {isAuthenticated && (
            <div style={{ marginLeft: 'auto' }}>
              <LogoutButton />
            </div>
          )}
        </Toolbar>
      </AppBar>
    </ThemeProvider>
  );
};

export default Nav;
