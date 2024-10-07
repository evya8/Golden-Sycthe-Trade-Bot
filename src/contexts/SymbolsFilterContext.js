import React, { createContext, useState, useEffect, useContext } from 'react';
import axiosInstance from '../utils/axiosInstance';
import { UserContext } from './UserContext';

const SymbolsFilterContext = createContext();

export const SymbolsFilterProvider = ({ children }) => {
  const { token } = useContext(UserContext);
  const [allStocks, setAllStocks] = useState([]);
  const [filteredStocks, setFilteredStocks] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (token) {
      axiosInstance.get('/symbols/')
      .then(response => {
        const data = response.data.symbols || [];
        if (!Array.isArray(data)) {
          console.error('Expected symbols to be an array, but got:', typeof data, data);
          return;
        }

        setAllStocks(data);
        setFilteredStocks(data); // Initially set filteredStocks to allStocks

        const uniqueSectors = [...new Set(data.map(stock => stock.sector).filter(Boolean))];
        setSectors(uniqueSectors);

        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
    }
  }, [token]);

  const filterStocks = (filters) => {
    let stocks = allStocks;

    // Prioritize symbol filtering over sector filtering
    if (filters.symbol.length > 0) {
      stocks = stocks.filter(stock => filters.symbol.some(symbol => symbol.symbol === stock.symbol));
    } else if (filters.sector.length > 0) {
      stocks = stocks.filter(stock => filters.sector.includes(stock.sector));
    }

    setFilteredStocks(stocks);
  };

  return (
    <SymbolsFilterContext.Provider value={{
      allStocks,
      sectors,
      filteredStocks,
      filterStocks,
      loading,
      error
    }}>
      {children}
    </SymbolsFilterContext.Provider>
  );
};

export { SymbolsFilterContext };
