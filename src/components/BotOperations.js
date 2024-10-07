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
  createTheme,
  ThemeProvider,
  CssBaseline,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { subDays } from 'date-fns';

const BotOperations = () => {
  const { operations, loading, error } = useContext(BotOperationsContext);
  const [timeFilter, setTimeFilter] = useState('recent-2days');

  const stages = ['First Screen', 'Indicator', 'Order Status', 'Order Confirmation'];

  const darkTheme = createTheme({
    palette: {
      mode: 'dark',
    },
  });
// Function to filter operations based on selected time filter
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

  // Group operations by stock_symbol
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

  const getBackgroundColor = (status) => {
    return status === 'Passed' ? 'green' : status === 'Failed' ? 'red' : 'inherit';
  };

  // Function to format the timestamp in the user's local timezone
  const formatTimestamp = (timestamp) => {
    return new Intl.DateTimeFormat('en-US', {
      year: '2-digit',
      month: 'numeric',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      timeZoneName: 'shortGeneric'
    }).format(new Date(timestamp));
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{border: '2px solid #333333',padding: '20px',borderRadius: '4px',marginTop: '20px'}}>
        <Typography variant="h4"  gutterBottom color= "#c9a243">
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
          <Paper elevation={3} sx={{ width: '100%', overflow: 'hidden' }}>
            <Table sx={{ minWidth: 650 }} aria-label="bot operations table">
              <TableHead>
                <TableRow>
                  <TableCell>
                    <Typography variant="subtitle1" fontWeight="bold">
                      Stock Symbol
                    </Typography>
                  </TableCell>
                  {stages.map((stage) => (
                    <TableCell key={stage}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {stage}
                      </Typography>
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.values(groupedOperations).map((operation, index) => (
                  <TableRow key={index} hover>
                    <TableCell>
                      <Typography variant="body1">{operation.stock_symbol}</Typography>
                    </TableCell>
                    {stages.map((stage) => (
                      <TableCell
                        key={stage}
                        sx={{
                          backgroundColor:
                            operation.stages[stage] && operation.stages[stage].status
                              ? getBackgroundColor(operation.stages[stage].status)
                              : 'inherit',
                        }}
                      >
                        {operation.stages && operation.stages[stage] ? (
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                            <Typography variant="body2">
                              {operation.stages[stage].reason || 'N/A'}
                            </Typography>
                            <Typography variant="body2">
                            <strong></strong>{' '}
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
