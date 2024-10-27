import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserContext } from '../contexts/UserContext';
import { Container, TextField, Button, Typography, Box } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const Login = () => {
  const { login, loading, user } = useContext(UserContext);
  const [formData, setFormData] = useState({ username: '', password: '' });
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    login(formData);
  };

  useEffect(() => {
    if (user) {
      navigate('/user-dashboard');
    }
  }, [user, navigate]);

  // Create a dark mode theme
  const darkTheme = createTheme({
    palette: {
      mode: 'dark',
      primary: {
        main: '#f0a500', // Gold color for primary elements
      },
      text: {
        primary: '#e0e0e0', // Off-white text for dark mode
      },
    },
  });

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="sm">
        <Box mt={8} textAlign="center">
          <Typography variant="h4" component="h2" gutterBottom sx={{ color: 'primary.main'  }}>
            Login
          </Typography>
          <form onSubmit={handleSubmit}>
            <Box mb={2} sx={{paddingTop:3}}>
              <TextField
                fullWidth
                label="Username"
                name="username"
                variant="outlined"
                value={formData.username}
                onChange={handleChange}
                required
                InputLabelProps={{
                  style: { color: '#e0e0e0' }, // Off-white label color
                }}
                InputProps={{
                  style: { color: '#e0e0e0' }, // Off-white input text color
                }}
              />
            </Box>
            <Box mb={2}>
              <TextField
                fullWidth
                label="Password"
                name="password"
                type="password"
                variant="outlined"
                value={formData.password}
                onChange={handleChange}
                required
                InputLabelProps={{
                  style: { color: '#e0e0e0' }, // Off-white label color
                }}
                InputProps={{
                  style: { color: '#e0e0e0' }, // Off-white input text color
                }}
              />
            </Box>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={loading}
              fullWidth
              sx={{ mt: 2 }}
            >
              Login
            </Button>
          </form>
        </Box>
      </Container>
    </ThemeProvider>
  );
};

export default Login;
