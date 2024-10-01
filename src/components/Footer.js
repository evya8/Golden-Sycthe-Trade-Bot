import React from 'react';
import { Box, Typography, Link } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import EmailIcon from '@mui/icons-material/Email';


const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#b8860b',
    },
    text: {
      primary: '#b8860b',
    },
  },
});

const Footer = () => {
  return (
    <ThemeProvider theme={theme}>
      <Box
        component="footer"
        sx={{
          bgcolor: 'background.default',
          color: 'primary.main',
          py: 2,
          textAlign: 'center',
          display: 'flex', // Make this flex to align items in a row
          justifyContent: 'center', // Center horizontally
          alignItems: 'center', // Center vertically
          flexDirection: 'row', // Ensure items are in a row
          gap: 2, // Add some spacing between the items
        }}
      >
        <Box display="flex" alignItems="center">
          {/* Email Icon and Address */}
          <EmailIcon sx={{ color: 'primary.main', mr: 1 }} />
          <Typography variant="body1"  color="primary.main">
            goldenscythetradebot@gmail.com
          </Typography>
        </Box>

        {/* Divider (Optional) */}
        <Typography variant="body2" sx={{ mx: 1 }}>|</Typography>

        {/* Copyright Text */}
        <Typography variant="body2" color="primary.main">
          © {new Date().getFullYear()} Evyatar Hermesh. All rights reserved.
        </Typography>

        {/* Divider (Optional) */}
        <Typography variant="body2" sx={{ mx: 1 }}>|</Typography>

        {/* "Powered by Alpaca" */}
        <Box display="flex" justifyContent="center" alignItems="center">
          <Typography variant="body2" mr={1} color="primary.main">
            Powered by
          </Typography>
          <Link
            href="https://alpaca.markets"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Box
              sx={{
                border: '1px solid #c9a243',
                padding: 0.5,
                borderRadius: 2,
                backgroundColor: '#FFFFFF',
                alignItems: 'center',
                display: 'flex',
              }}
            >
              <img
                src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRzKiWn7ybOOm7Bg5ITM5Cq_v5l6oFz726jzg&s"
                alt="Alpaca Markets"
                style={{ height: '24px' }}
              />
            </Box>
          </Link>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default Footer;
