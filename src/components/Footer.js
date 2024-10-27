import React from 'react';
import { Box, Typography, Link } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import EmailIcon from '@mui/icons-material/Email';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import GitHubIcon from '@mui/icons-material/GitHub';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#b8860b', // Gold color for text and icons
    },
    background: {
      default: '#121212', // Dark background
    },
    text: {
      primary: '#b8860b', // Gold text color
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
          textAlign: 'center',
          display: 'flex',
          alignItems: 'center',
          flexWrap: 'wrap', // Allow wrapping if the space is too narrow
          gap: 1, // Narrow the gap between elements
          px: 30, // Add padding to make the content look a bit more compact
          marginLeft: 7,
        }}
      >
        <Box display="flex" alignItems="center">
          <EmailIcon sx={{ color: 'primary.main', mr: 0.5 }} />
          <Link href="mailto:goldenscythetradebot@gmail.com" underline="none">
            <Typography variant="body2" color="primary.main">
              goldenscythetradebot@gmail.com
            </Typography>
          </Link>
        </Box>

        {/* Divider */}
        <Typography variant="body2" sx={{ mx: 0.5 }}>|</Typography>

        {/* Copyright Text with LinkedIn and GitHub Links */}
        <Typography variant="body2" color="primary.main" sx={{ mr: 1 }}>
          © {new Date().getFullYear()} Evyatar Hermesh, All Rights Reserved
        </Typography>
        <Link
          href="https://www.linkedin.com/in/evyatarhermesh/"
          target="_blank"
          rel="noopener noreferrer"
          sx={{ ml: 0.5 }}
        >
          <LinkedInIcon sx={{ color: 'primary.main' }} />
        </Link>
        <Link
          href="https://github.com/evya8"
          target="_blank"
          rel="noopener noreferrer"
          sx={{ ml: 0.5 }}
        >
          <GitHubIcon sx={{ color: 'primary.main' }} />
        </Link>

        {/* Divider */}
        <Typography variant="body2" sx={{ mx: 0.5 }}>|</Typography>

        {/* "Powered by Alpaca" */}
        <Box display="flex" justifyContent="center" alignItems="center">
          <Typography variant="body2" mr={0.5} color="primary.main">
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
                padding: 0.25, // Reduce padding inside the Alpaca link
                borderRadius: 2,
                backgroundColor: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                marginLeft: 1,
              }}
            >
              <img
                src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRzKiWn7ybOOm7Bg5ITM5Cq_v5l6oFz726jzg&s"
                alt="Alpaca Markets"
                style={{ height: '20px' }} // Reduce image size for narrow space
              />
            </Box>
          </Link>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default Footer;
