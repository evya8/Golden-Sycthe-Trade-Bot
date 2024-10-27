import React, { useEffect, useState, useContext, useCallback } from 'react';
import { UserSettingsContext } from '../contexts/UserSettingsContext';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  CircularProgress,
  Paper,
  Box,
  CssBaseline,
  ThemeProvider,
  createTheme,
} from '@mui/material';

// Dark theme for the table and box
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#f0a500', // New custom primary color (gold)
    },
    background: {
      default: '#0d0d0d', // Darker background for improved contrast
      paper: '#1a1a1a', // Slightly lighter paper background
    },
    text: {
      primary: '#e0e0e0', // Off-white text for reduced strain
    },
    error: {
      main: '#ff7043', // New error color (orange-red) to complement success.main
    },
    success: {
      main: '#66bb6a', // Success color
    },
  },
});

// Helper function to format date
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return isNaN(date.getTime()) ? 'N/A' : new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date);
};

const AccountActivity = () => {
  const [activities, setActivities] = useState([]);
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiKeyError, setApiKeyError] = useState(false);

  const { settings } = useContext(UserSettingsContext);
  const { alpaca_api_key, alpaca_api_secret } = settings;

  const fetchTradeData = useCallback(async () => {
    if (!alpaca_api_key || !alpaca_api_secret) {
      setApiKeyError(true);
      return;
    }

    setApiKeyError(false);
    setLoading(true);

    const groupActivitiesBySymbolAndDate = (activities) => {
      const groupedActivities = {};

      activities.forEach((activity) => {
        const symbol = activity.symbol;
        const dateKey = formatDate(activity.transaction_time);

        if (!groupedActivities[symbol]) {
          groupedActivities[symbol] = {};
        }

        if (!groupedActivities[symbol][dateKey]) {
          groupedActivities[symbol][dateKey] = {
            totalQty: 0,
            totalPrice: 0,
            totalTrades: 0,
            side: activity.side, // Capture the side (buy/sell)
          };
        }

        // Sum the quantity and calculate the total price
        const qty = parseFloat(activity.qty);
        const price = parseFloat(activity.price);

        groupedActivities[symbol][dateKey].totalQty += qty;
        groupedActivities[symbol][dateKey].totalPrice += price * qty;
        groupedActivities[symbol][dateKey].totalTrades += 1;
      });

      return groupedActivities;
    };

    try {
      const activitiesResponse = await fetch(
        `https://paper-api.alpaca.markets/v2/account/activities/FILL`,
        {
          headers: {
            'APCA-API-KEY-ID': alpaca_api_key,
            'APCA-API-SECRET-KEY': alpaca_api_secret,
          },
        }
      );
      const activitiesData = await activitiesResponse.json();
      console.log("Fetched Activities Data:", activitiesData);

      const positionsResponse = await fetch(
        `https://paper-api.alpaca.markets/v2/positions`,
        {
          headers: {
            'APCA-API-KEY-ID': alpaca_api_key,
            'APCA-API-SECRET-KEY': alpaca_api_secret,
          },
        }
      );
      const positionsData = await positionsResponse.json();
      console.log("Fetched Positions Data:", positionsData);

      setActivities(groupActivitiesBySymbolAndDate(activitiesData));
      setPositions(positionsData);
    } catch (error) {
      console.error('Error fetching trade data:', error);
    } finally {
      setLoading(false);
    }
  }, [alpaca_api_key, alpaca_api_secret]);

  useEffect(() => {
    if (alpaca_api_key && alpaca_api_secret) {
      fetchTradeData();
    }
  }, [alpaca_api_key, alpaca_api_secret, fetchTradeData]);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box
        sx={{
          border: '2px solid #404040',
          padding: '20px',
          borderRadius: '4px',
          marginTop: '20px',
        }}
      >
        <Typography variant="h4" gutterBottom color="primary.main">
          Account Activity
        </Typography>
        <Typography variant="h6" gutterBottom color="primary.main">
          Open Positions
        </Typography>

        {loading ? (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '50vh',
            }}
          >
            <CircularProgress />
          </Box>
        ) : apiKeyError ? (
          <Typography color="error.main" variant="h6">
            Error: Missing Alpaca API key or secret.
          </Typography>
        ) : (
          <Box>
            {/* Open Positions */}
            <Paper elevation={3} sx={{ width: '100%', overflow: 'auto', maxHeight: 500, mb: 3 }}>
              <TableContainer>
                <Table sx={{ minWidth: 650 }} aria-label="open positions table">
                  <TableHead>
                    <TableRow sx={{ position: 'sticky', top: 0, backgroundColor: '#333', zIndex: 1 }}>
                      <TableCell>
                        <Typography variant="subtitle1" fontWeight="bold">
                          Symbol
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="subtitle1" fontWeight="bold">
                          Qty
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="subtitle1" fontWeight="bold">
                          Entry Price
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="subtitle1" fontWeight="bold">
                          Current Price
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="subtitle1" fontWeight="bold">
                          PnL (%)
                        </Typography>
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {positions.map((position, index) => (
                      <TableRow key={index} hover>
                        <TableCell>{position.symbol}</TableCell>
                        <TableCell>{parseFloat(position.qty).toFixed(2)}</TableCell>
                        <TableCell>{parseFloat(position.avg_entry_price).toFixed(2)}</TableCell>
                        <TableCell>{parseFloat(position.current_price).toFixed(2)}</TableCell>
                        <TableCell>
                          {(
                            ((position.current_price - position.avg_entry_price) /
                              position.avg_entry_price) *
                            100
                          ).toFixed(2)}
                          %
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>

            {/* Trades */}
            <Typography variant="h6" gutterBottom color="primary.main">
              Activities
            </Typography>
            <Paper elevation={3} sx={{ width: '100%', overflow: 'auto', maxHeight: 500 }}>
              <TableContainer>
                <Table sx={{ minWidth: 650 }} aria-label="account activities table">
                  <TableHead sx={{ position: 'sticky' }} >
                    <TableRow>
                      <TableCell>
                        <Typography variant="subtitle1" fontWeight="bold">
                          Symbol
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="subtitle1" fontWeight="bold">
                          Side
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="subtitle1" fontWeight="bold">
                          Average Price
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="subtitle1" fontWeight="bold">
                        Total Qty 
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="subtitle1" fontWeight="bold">
                        Date 
                        </Typography>
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  {Object.entries(activities).map(([symbol, dates]) => 
                    Object.entries(dates)
                      .sort(([dateA], [dateB]) => new Date(dateB) - new Date(dateA))  // Sort by date
                      .map(([date, data], index) => (
                        <TableRow key={index} hover>
                          <TableCell>{symbol}</TableCell>
                          <TableCell>{data.side}</TableCell>
                          <TableCell>{(data.totalPrice / data.totalQty).toFixed(2)}</TableCell>
                          <TableCell>{data.totalQty.toFixed(2)}</TableCell>
                          <TableCell>{date}</TableCell>
                        </TableRow>
                      ))
                  )}
                </Table>
              </TableContainer>
            </Paper>
          </Box>
        )}
      </Box>
    </ThemeProvider>
  );
};

export default AccountActivity;
