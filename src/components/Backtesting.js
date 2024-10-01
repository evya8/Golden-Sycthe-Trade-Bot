import React, { useContext, useState } from 'react';
import { BacktestContext } from '../contexts/BacktestContext';
import { UserContext } from '../contexts/UserContext'; 
import { SymbolsFilterContext } from '../contexts/SymbolsFilterContext'; // Import SymbolsFilterContext
import { createTheme, ThemeProvider, CssBaseline, Container, Button, TextField, Typography, Grid, Autocomplete, MenuItem, LinearProgress, Box } from '@mui/material';
import { createGlobalStyle } from 'styled-components';
import BacktestResult from './BacktestResult';

// Global style to invert the color of the calendar icon
const GlobalStyle = createGlobalStyle`
  input[type="date"]::-webkit-calendar-picker-indicator {
      filter: invert(1); /* Invert the calendar icon color to white */
  }
`;

const Backtesting = () => {
    const { runBacktest, backtestResult, loading, error } = useContext(BacktestContext);
    const { user } = useContext(UserContext); // Fetch user details from UserContext
    const { allStocks } = useContext(SymbolsFilterContext); // Fetch allStocks from SymbolsFilterContext

    const [formData, setFormData] = useState({
        tradeFrequency: 'weekly',
        symbol: null, // Single symbol selection
        startDate: '2023-01-02',
        endDate: '2023-06-01',
        totalCapital: 100000,
        
    });

    const darkTheme = createTheme({
        palette: {
            mode: 'dark',
        },
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSymbolChange = (event, newValue) => {
        setFormData({
            ...formData,
            symbol: newValue, // Set the single symbol selected
        });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        const { tradeFrequency, symbol, startDate, endDate, totalCapital } = formData;
        if (!symbol) {
            console.log("Symbol is required.");
            return;
        }
        // Check if user object exists and has an ID
        if (user && user.id) {
            runBacktest(user.id, tradeFrequency, symbol.symbol, startDate, endDate, totalCapital);
        } else {
            console.log("User ID not available.");
        }
    };

    return (
        <ThemeProvider theme={darkTheme}>
            <GlobalStyle /> {/* Apply global styles for the calendar icon */}
            <CssBaseline />
            <Container>
                <Typography variant="h4" gutterBottom sx={{ color: '#c9a243' }}>Backtesting</Typography>
                <Typography sx={{
                                marginLeft: 2,
                                color: '#c9a243',
                                maxWidth: '300px', // Limit width to wrap text in two lines
                                textAlign: 'left', // Align the text to the right
                                fontSize: '1rem', // Keep the font size normal
                                }}>
                Expirement with backtesting the strategy and see how it performs.</Typography>

                <form onSubmit={handleSubmit}>
                {/* Container with a maximum width */}
                <Box sx={{ maxWidth: '500px', p: 2 }}> {/* This ensures a max width and centers the form */}
                    
                    <Grid container spacing={2} >
                    
                    {/* Trade Frequency */}
                    <Grid item xs={12}>
                        <TextField
                        select
                        label="Trade Frequency"
                        name="tradeFrequency"
                        value={formData.tradeFrequency}
                        onChange={handleChange}
                        fullWidth
                        variant="outlined"
                        margin="normal"
                        >
                        <MenuItem value="weekly">Weekly</MenuItem>
                        <MenuItem value="daily">Daily</MenuItem>
                        <MenuItem value="hourly">Hourly</MenuItem>
                        </TextField>
                    </Grid>

                    {/* Symbol */}
                    <Grid item xs={12}>
                        <Autocomplete
                        options={allStocks}
                        value={formData.symbol}
                        onChange={handleSymbolChange}
                        getOptionLabel={(option) => option ? `${option.symbol} - ${option.company_name}` : ''}
                        renderInput={(params) => (
                            <TextField {...params} label="Stock Symbol" placeholder="Search and select..." fullWidth />
                        )}
                        />
                    </Grid>

                    {/* Start Date */}
                    <Grid item xs={6}>
                        <TextField
                            label="Start Date"
                            name="startDate"
                            type="date"
                            value={formData.startDate}
                            onChange={handleChange}
                            fullWidth
                            InputLabelProps={{
                                shrink: true,
                            }}
                            InputProps={{
                                inputProps: { style: { color: 'white' } }, // Optional: Change input text color to white if needed
                            }}
                            variant="outlined"
                            margin="normal"
                        />
                    </Grid>

                    {/* End Date */}
                    <Grid item xs={6}>
                        <TextField
                            label="End Date"
                            name="endDate"
                            type="date"
                            value={formData.endDate}
                            onChange={handleChange}
                            fullWidth
                            InputLabelProps={{
                                shrink: true,
                            }}
                            InputProps={{
                                inputProps: { style: { color: 'white' } }, // Optional: Change input text color to white if needed
                            }}
                            variant="outlined"
                            margin="normal"
                        />
                    </Grid>

                    {/* Total Capital */}
                    <Grid item xs={12}>
                        <TextField
                        label="Total Capital"
                        name="totalCapital"
                        type="number"
                        value={formData.totalCapital}
                        onChange={handleChange}
                        fullWidth
                        variant="outlined"
                        margin="normal"
                        InputProps={{
                            inputProps: {
                            min: 10000,
                            max: 10000000,
                            },
                        }}
                        />
                        <Typography sx={{
                                marginLeft: 0,
                                color: '#c9a243',
                                maxWidth: '600px', // Limit width to wrap text in two lines
                                textAlign: 'left', // Align the text to the right
                                fontSize: '0.85rem', // Keep the font size normal
                                }}>
                With this Backtesting method, each trade employs 100% of your capital.</Typography>
                    </Grid>

                    

                    </Grid>

                    {/* Submit Button */}
                    <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>
                    Run Backtest
                    </Button>
                </Box>
                </form>

                {/* Show Progress Bar when loading */}
                {loading && (
                    <Box sx={{ width: '100%', mt: 2 }}>
                        <Typography variant="body1" gutterBottom>Running backtest, please wait...</Typography>
                        <LinearProgress />
                    </Box>
                )}

                {/* Error Handling */}
                {error && <Typography color="error">Error: {error}</Typography>}

                {/* Backtest Result */}
                {backtestResult && (
                    <Box sx={{ mt: 4 }}>
                        <BacktestResult result={backtestResult} />
                    </Box>
                )}
            </Container>
        </ThemeProvider>
    );
};

export default Backtesting;
