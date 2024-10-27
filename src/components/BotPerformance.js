import React, { useEffect, useState, useContext, useCallback } from 'react';
import { UserSettingsContext } from '../contexts/UserSettingsContext';
import {
  Typography,
  CircularProgress,
  Box,
  CssBaseline,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import Plot from 'react-plotly.js'; // Import Plotly component

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

// Helper function to format date for display purposes
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return isNaN(date.getTime()) ? 'N/A' : new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date);
};

// Helper function to determine dot size based on return percentage
const calculateDotSize = (pnl) => {
  // Minimum size is 25, increase by 10 for every 2.5% increment
  const increment = Math.floor(Math.abs(pnl) / 4) * 10;
  return 25 + increment;
};

// Function to determine the color of a dot based on PnL and status
const assignColor = (pnl, status) => {
  if (status === 'Open') {
    return 'yellow'; // Open positions - yellow
  }
  if (pnl !== null && pnl >= 0) {
    return 'green'; // Positive returns - green
  }
  return 'red'; // Negative returns - red
};

const BotPerformance = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiKeyError, setApiKeyError] = useState(false);
  const [trades, setTrades] = useState([]); // State to hold processed trade data for visualization

  const { settings } = useContext(UserSettingsContext);
  const { alpaca_api_key, alpaca_api_secret } = settings;

  // Helper function to pair buys and sells
  const processTrades = (activitiesData) => {
    // Sort activities by date before processing
    const sortedActivities = activitiesData.sort((a, b) => new Date(a.transaction_time) - new Date(b.transaction_time));
    const groupedBySymbol = {};

    sortedActivities.forEach((activity) => {
      const symbol = activity.symbol;
      if (!groupedBySymbol[symbol]) {
        groupedBySymbol[symbol] = [];
      }
      groupedBySymbol[symbol].push(activity);
    });

    const tradesArray = [];

    // Process each symbol to calculate PnL
    for (const symbol in groupedBySymbol) {
      const symbolData = groupedBySymbol[symbol];
      let buyActivity = null;

      symbolData.forEach((activity) => {
        if (activity.side === 'buy') {
          buyActivity = activity;
        } else if (activity.side === 'sell' && buyActivity) {
          // Calculate PnL, duration, and create a trade entry
          const pnl = ((parseFloat(activity.price) - parseFloat(buyActivity.price)) / parseFloat(buyActivity.price)) * 100;
          const duration = Math.round((new Date(activity.transaction_time) - new Date(buyActivity.transaction_time)) / (1000 * 60 * 60 * 24));

          // Determine color based on PnL and status
          const color = assignColor(pnl, 'Closed');

          tradesArray.push({
            symbol: symbol,
            buyPrice: parseFloat(buyActivity.price),
            sellPrice: parseFloat(activity.price),
            pnl: pnl.toFixed(2),
            duration: duration,
            buyDate: formatDate(buyActivity.transaction_time),
            sellDate: activity.transaction_time, // Keep as a Date string for Plotly X-axis positioning
            status: 'Closed',
            color: color,
            size: calculateDotSize(pnl), // Calculate dot size
          });

          buyActivity = null; // Reset for next pair
        }
      });

      // If there's an open position (buy without a sell)
      if (buyActivity) {
        const color = assignColor(null, 'Open');

        tradesArray.push({
          symbol: symbol,
          buyPrice: parseFloat(buyActivity.price),
          sellPrice: null,
          pnl: null,
          duration: null,
          buyDate: formatDate(buyActivity.transaction_time),
          sellDate: null,
          status: 'Open',
          color: color,
          size: 25, // Default size for open positions
        });
      }
    }

    setTrades(tradesArray);
  };

  const fetchTradeData = useCallback(async () => {
    if (!alpaca_api_key || !alpaca_api_secret) {
      setApiKeyError(true);
      return;
    }

    setApiKeyError(false);
    setLoading(true);

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

      setActivities(activitiesData);

      // Process trades to calculate PnL and duration
      processTrades(activitiesData);
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
          Bot Performance
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
            {/* Plotly Scatter Plot for Trades */}
            
            <Plot
              style={{ width: '800px', height: '500px' }} // Adjust chart size
              data={[
                {
                  x: trades
                    .filter(trade => trade.status === 'Closed')
                    .map(trade => new Date(trade.sellDate)), // X-axis is actual closing date
                  y: trades
                    .filter(trade => trade.status === 'Closed')
                    .map(trade => parseFloat(trade.pnl)), // Y-axis is percent return (PnL)
                  mode: 'markers',
                  marker: {
                    size: trades
                      .filter(trade => trade.status === 'Closed')
                      .map(trade => trade.size), // Dot size based on return
                    sizemode: 'area',
                    color: trades
                      .filter(trade => trade.status === 'Closed')
                      .map(trade => trade.color), // Colors based on PnL and status
                  },
                  text: trades
                    .filter(trade => trade.status === 'Closed')
                    .map(trade => `${trade.symbol}, ${trade.pnl}% , Closed on: ${formatDate(trade.sellDate)}, Duration: ${trade.duration} days`),
                  hoverinfo: 'text',
                }
              ]}
              layout={{
                title: 'Trades History',
                template: 'plotly_dark',
                paper_bgcolor: '#2f2f2f',
                plot_bgcolor: '#1a1a1a',
                font: { color: 'beige' },
                margin: {
                  l: 60, // Adjust left padding
                  r: 40, // Adjust right padding
                  t: 50, // Adjust top padding
                  b: 50, // Adjust bottom padding
                },
                xaxis: {
                  title: '',
                  type: 'date',
                  gridcolor: 'gray',
                },
                yaxis: {
                  title: 'Return (%)',
                  gridcolor: 'gray',
                  zeroline: true,
                  zerolinewidth: 2, // Emphasize the 0 line with a thicker line
                  zerolinecolor: 'beige', // Use a distinct color for the 0 line
                },
              }}
            />
          </Box>
        )}
      </Box>
    </ThemeProvider>
  );
};

export default BotPerformance;
