import React, { useContext, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { UserContext } from '../contexts/UserContext';
import { Container, Typography, Button, Box } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const Home = () => {
    const navigate = useNavigate();
    const { user } = useContext(UserContext);

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
                main: '#f0a500', // Gold color for buttons
            },
            text: {
                primary: '#e0e0e0', // Off-white text for dark mode
            },
        },
    });

    return (
        <ThemeProvider theme={darkTheme}>
            <CssBaseline />
            <Container maxWidth="md">
                <Box textAlign="center" mt={8}>
                    <Typography variant="h4" component="h1" gutterBottom sx={{ color: 'primary.main' }}>
                        Welcome to Golden Scythe
                    </Typography>
                    <Typography variant="h6" component="h1" gutterBottom sx={{ color: '#b8860b' }}>
                        Start Harvesting Your Profits with the Golden Scythe Trading Bot
                    </Typography>
                    {!user && (
                        <Typography variant="body1" component="p" sx={{ color: 'text.primary' }}>
                            Please{' '}
                            <Button color="primary" component={Link} to="/register">
                                Register
                            </Button>{' '}
                            or{' '}
                            <Button color="primary" component={Link} to="/login">
                                Login
                            </Button>{' '}
                            to continue.
                        </Typography>
                    )}
                </Box>
            </Container>
        </ThemeProvider>
    );
};

export default Home;
