import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
import axiosInstance from '../utils/axiosInstance';
import { UserContext } from './UserContext';
import { toast } from 'react-toastify';

const BotOperationsContext = createContext();

const BotOperationsProvider = ({ children }) => {
  const { token } = useContext(UserContext);
  const [operations, setOperations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Wrap getBotOperations with useCallback
  const getBotOperations = useCallback(async () => {
    if (!token) return; // Only fetch if the user is authenticated
    setLoading(true);
    setError(null);
    try {
      const response = await axiosInstance.get('/bot-operations/');
      setOperations(response.data);
      setLoading(false);
    } catch (error) {
      setError(error.response?.data || 'Failed to fetch bot operations');
      toast.error(error.response?.data || 'Failed to fetch bot operations');
      setLoading(false);
    }
  }, [token]); // Add token as a dependency to useCallback

  useEffect(() => {
    if (token) {
      getBotOperations();
    }
  }, [token, getBotOperations]); // Include getBotOperations in the dependency array

  return (
    <BotOperationsContext.Provider value={{ operations, loading, error, getBotOperations }}>
      {children}
    </BotOperationsContext.Provider>
  );
};

export { BotOperationsProvider, BotOperationsContext };
