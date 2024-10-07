import React, { useEffect } from 'react';
import { Box, Typography, Grid, Paper, Divider } from '@mui/material';
import Plot from 'react-plotly.js';

const BacktestResult = ({ result }) => {
  const { stats, plot_data } = result;

  // Debugging: Check if plot_data is being received
  useEffect(() => {
    console.log('Received result:', result);  // Logs the entire result object
    console.log('Plot Data:', plot_data);     // Logs the plot_data specifically
  }, [result, plot_data]);

  
  // Define the stats to display
  const displayedStats = [
    { key: 'Total Return [%]', label: 'Total Return %' },
    { key: 'Benchmark Return [%]', label: 'Benchmark Return %' },
    { key: 'Start Value', label: 'Start Value' },
    { key: 'End Value', label: 'End Value' },
    { key: 'Win Rate [%]', label: 'Win Rate %' },
    { key: 'Best Trade [%]', label: 'Best Trade %' },
    { key: 'Worst Trade [%]', label: 'Worst Trade %' },
    { key: 'Total Trades', label: 'Total Trades' },
    { key: 'Total Closed Trades', label: 'Total Closed Trades' },
    { key: 'Total Open Trades', label: 'Total Open Trades' },
    { key: 'Open Trade PnL', label: 'Open Trade PnL' },
    { key: 'Avg Winning Trade [%]', label: 'Avg Winning Trade %' },
    { key: 'Avg Losing Trade [%]', label: 'Avg Losing Trade %' },
    { key: 'Avg Winning Trade Duration', label: 'Avg Winning Trade Duration' },
    { key: 'Avg Losing Trade Duration', label: 'Avg Losing Trade Duration' },
    { key: 'Max Drawdown [%]', label: 'Max Drawdown %' },
    { key: 'Max Drawdown Duration', label: 'Max Drawdown Duration' },
    { key: 'Max Gross Exposure [%]', label: 'Max Gross Exposure %' },
  ];

  return (
    <Box sx={{ padding: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ color: '#c9a243' }}>Backtest Result</Typography>

      <Divider sx={{ marginBottom: 4 }} />

      {/* Check if plot_data is present and properly formatted before rendering the Plot */}
      {plot_data && plot_data.data && plot_data.layout ? (
        <Box sx={{ paddingTop: 2 , paddingBottom: 75 }}>
          <Plot
            data={plot_data.data}    // Plot data must be an array of datasets
            layout={plot_data.layout} // Plot layout must contain chart configuration
            style={{ width: '100%', height: '400px' }} // Adjust the size of the chart
          />
        </Box>
      ) : (
        <Typography variant="body1" color="error">
          No data available to display the chart. Please check backend response or Plotly configuration.
        </Typography>
      )}
      
      {/* Display Stats - 4 items per row */}
      <Grid container spacing={2}>
        {displayedStats.map(({ key, label }) => (
          stats[key] !== undefined && (
            <Grid item xs={12} sm={6} md={3} key={key}> {/* 3 columns on medium, 4 columns on large */}
              <Paper elevation={2} sx={{ padding: 2 }}>
                <Typography variant="subtitle1" fontWeight="bold">{label}</Typography>
                <Typography variant="body1">
                  {typeof stats[key] === 'number' ? stats[key].toLocaleString(undefined, { maximumFractionDigits: 2 }) : stats[key]}
                </Typography>
              </Paper>
            </Grid>
          )
        ))}
      </Grid>

      
    </Box>
  );
};

export default BacktestResult;
