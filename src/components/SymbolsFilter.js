import React, { useContext, useState, useEffect } from 'react';
import { SymbolsFilterContext } from '../contexts/SymbolsFilterContext';
import { UserSettingsContext } from '../contexts/UserSettingsContext';
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  Chip,
  TextField,
  Checkbox,
  Autocomplete,
  Typography
} from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

const SymbolsFilter = () => {
  const { sectors, allStocks } = useContext(SymbolsFilterContext);
  const { settings, saveUserSettings } = useContext(UserSettingsContext);

  const [filters, setFilters] = useState({
    sector: settings.filter_sector || [],
    symbol: settings.filter_symbol || [],
  });

  useEffect(() => {
    if (allStocks.length > 0) {
      const matchedSymbols = settings.filter_symbol.map(savedSymbol =>
        allStocks.find(stock => stock.symbol === savedSymbol)
      ).filter(stock => stock !== undefined); // Filter out any undefined values
  
      setFilters({
        sector: settings.filter_sector || [],
        symbol: matchedSymbols, // Array of full stock objects
      });
    }
  }, [settings, allStocks]);

  const handleSymbolChange = (event, newValue) => {
    setFilters((prevState) => ({
      ...prevState,
      symbol: newValue, // Store full stock objects in state
      sector: [], // Clear sector if symbol is selected
    }));
  };

  const handleSectorChange = (event) => {
    setFilters({
      sector: event.target.value,
      symbol: [], // Clear symbol if sector is selected
    });
  };

  const handleSaveFilters = () => {
    const updatedSettings = {
      ...settings,
      filter_sector: filters.sector,
      filter_symbol: filters.symbol.map(stock => stock.symbol), // Save only symbols to the database
    };
    saveUserSettings(updatedSettings);
    console.log("Filters saved to database:"); // Console log to verify saved filters
  };
  
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
      background: {
        default: '#121212',
        paper: '#1e1e1e',
      },
    },
  });

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        border: '2px solid #333333', 
        padding: '20px', 
        borderRadius: '4px',
        backgroundColor: 'background.paper', 
        marginTop: '20px' 
         }}>
          
        {/* Left side: Filters and Save button */}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, flex: 1 }}>
          <FormControl>
            <InputLabel>Sector</InputLabel>
            <Select
              name="sector"
              multiple
              value={filters.sector}
              onChange={handleSectorChange}
              input={<OutlinedInput label="Sector" />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value} label={value} />
                  ))}
                </Box>
              )}
            >
              {sectors && sectors.map((sector) => (
                <MenuItem key={sector} value={sector}>
                  {sector}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
  
          {/* Multi-select with search for stock symbols */}
          <Autocomplete
            multiple
            options={allStocks}
            value={filters.symbol.filter(stock => stock !== undefined)} // Ensure no undefined values
            onChange={handleSymbolChange}
            disableCloseOnSelect
            getOptionLabel={(option) => option ? `${option.symbol} - ${option.company_name}` : ''}
            isOptionEqualToValue={(option, value) => option?.symbol === value?.symbol} // Safely compare option and value by symbol
            renderOption={(props, option, { selected }) => (
              <li {...props} key={option.symbol}>
                <Checkbox
                  icon={<> </>}
                  checkedIcon={<>{selected}</>}
                  checked={selected}
                />
                {option ? `${option.symbol} - ${option.company_name}` : ''}
              </li>
            )}
            
            renderInput={(params) => (
              <TextField {...params} label="Stock Symbols" placeholder="Search and select..." />
            )}
          />
          
          <Button
            variant="contained"
            color="primary"
            sx={{ alignSelf: 'center', width: '35%' }}
            onClick={handleSaveFilters}
            disabled={false}
          >
            Save Filters
          </Button>
        </Box>
  
        {/* Right side: Comment */}
        <Typography sx={{ width: '25%', alignSelf: 'center', marginLeft: 3 }}>
          Optional filters that will be applied to your bot. You can select sectors or specify stock symbols. 
          If left empty, the bot will screen automatically for stocks suitable for the strategy.
        </Typography>
        
      </Box>
    </ThemeProvider>
  );
};

export default SymbolsFilter;
