import React, { useContext, useState } from 'react';
import { BotOperationsContext } from '../contexts/BotOperationsContext';
import {
  Box,
  Typography,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Paper,
  CircularProgress,
  Alert,
  Chip, // For status badges
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  createTheme,
  ThemeProvider,
  CssBaseline,
} from '@mui/material';
import { subDays } from 'date-fns';

const BotOperations = () => {
  const { operations, loading, error } = useContext(BotOperationsContext);
  const [timeFilter, setTimeFilter] = useState('recent-2days');

  const stages = ['First Screen', 'Indicator', 'Order Status', 'Order Confirmation'];

  const darkTheme = createTheme({
    palette: {
      mode: 'dark',
      primary: {
        main: '#f0a500', // Gold primary color
      },
      background: {
        default: '#0d0d0d', // Dark background
        paper: '#1a1a1a', // Dark paper background
      },
      text: {
        primary: '#e0e0e0', // Off-white text
        secondary: '#ffffff',
      },
      error: {
        main: '#ff7043', // Orange-red error color
      },
      success: {
        main: '#66bb6a', // Green success color
      },
    },
  });

  const filterOperationsByTime = (operation) => {
    const now = new Date();
    const operationDate = new Date(operation.timestamp);

    if (timeFilter === 'recent-2days') {
      return operationDate >= subDays(now, 2); // Last 2 days
    } else if (timeFilter === 'last week-8days') {
      return operationDate >= subDays(now, 8); // Last 8 days
    } else if (timeFilter === 'last month-30days') {
      return operationDate >= subDays(now, 30); // Last 30 days
    } else if (timeFilter === 'all') {
      return true; // Show all
    } else {
      return false; // Default case if no valid time filter is selected
    }
  };

  const groupedOperations = operations.reduce((acc, operation) => {
    if (!filterOperationsByTime(operation)) {
      return acc;
    }

    const stockSymbol = operation.stock_symbol;
    if (!acc[stockSymbol]) {
      acc[stockSymbol] = { stock_symbol: stockSymbol, stages: {} };
    }
    acc[stockSymbol].stages[operation.stage] = {
      status: operation.status,
      reason: operation.reason,
      timestamp: operation.timestamp,
    };
    return acc;
  }, {});

  const getStatusChip = (status) => {
    if (status === 'Passed') {
      return <Chip label="Passed" sx={{ backgroundColor: '#81c784', color: 'black' }} />;
    } else if (status === 'Failed') {
      return <Chip label="Failed" sx={{ backgroundColor: '#ff8a65', color: 'black' }} />;
    } else {
      return <Chip label="N/A" sx={{ backgroundColor: '#757575', color: 'white' }} />;
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Intl.DateTimeFormat('en-US', {
      year: '2-digit',
      month: 'numeric',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      timeZoneName: 'shortGeneric',
    }).format(new Date(timestamp));
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ border: '2px solid #333333', padding: '20px', borderRadius: '4px', marginTop: '20px' }}>
        <Typography variant="h4" gutterBottom color="primary.main">
          Bot Activity Monitor
        </Typography>

        <FormControl sx={{ mb: 2, minWidth: 200 }}>
          <InputLabel id="time-filter-label">Time Filter</InputLabel>
          <Select
            labelId="time-filter-label"
            value={timeFilter}
            onChange={(e) => setTimeFilter(e.target.value)}
            label="Time Filter"
          >
            <MenuItem value="recent-2days">Recent</MenuItem>
            <MenuItem value="last week-8days">Last Week</MenuItem>
            <MenuItem value="last month-30days">Last Month</MenuItem>
            <MenuItem value="all">All</MenuItem>
          </Select>
        </FormControl>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : (
          <Paper elevation={3} sx={{ width: '100%', overflow: 'hidden', backgroundColor: 'background.paper' }}>
            <Table sx={{ minWidth: 650 }} aria-label="bot operations table">
              <TableHead>
                <TableRow>
                  <TableCell sx={{
                      borderRight: '1px solid',
                      borderLeft: '1px solid',
                      borderColor: '#666666',
                    }}>
                    <Typography variant="subtitle1" fontWeight="bold" color="primary.text">
                      Stock Symbol
                    </Typography>
                  </TableCell>
                  {stages.map((stage) => (
                    <TableCell key={stage} sx={{
                      borderRight: '1px solid',
                      borderLeft: '1px solid',
                      borderColor: '#666666',
                    }}>
                      <Typography variant="subtitle1" fontWeight="bold" color="primary.text">
                        {stage}
                      </Typography>
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.values(groupedOperations).map((operation, index) => (
                  <TableRow key={index} hover>
                    <TableCell sx={{
                                  borderRight: '1px solid',
                                  borderLeft: '1px solid',
                                  borderColor: '#666666',

                                }}>
                      <Typography variant="body1" color="text.secondary">{operation.stock_symbol}</Typography>
                    </TableCell>
                    {stages.map((stage) => (
                      <TableCell key={stage}sx={{
                        borderRight: '1px solid',
                        borderLeft: '1px solid',
                        borderColor: '#666666',

                      }}>
                        {operation.stages && operation.stages[stage] ? (
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                            {getStatusChip(operation.stages[stage].status)}
                            <Typography variant="body2" color="text.secondary">
                              {operation.stages[stage].reason || 'N/A'}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {operation.stages[stage].timestamp
                                ? formatTimestamp(operation.stages[stage].timestamp)
                                : 'N/A'}
                            </Typography>
                          </Box>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            N/A
                          </Typography>
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        )}
      </Box>
    </ThemeProvider>
  );
};

export default BotOperations;
