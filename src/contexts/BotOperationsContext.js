import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
import axiosInstance from '../utils/axiosInstance';
import { UserContext } from './UserContext';
import { toast } from 'react-toastify';
import { DateTime } from 'luxon'; // Use Luxon for easier time handling

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
  }, [token]);

  // Function to check if the current time is between Mon-Fri, 10:00-11:00 AM US Eastern
  const isWithinPollingTime = () => {
    const now = DateTime.now().setZone('America/New_York'); // Set timezone to US Eastern
    const isWeekday = now.weekday >= 1 && now.weekday <= 5; // Monday to Friday
    const isWithinTime = now.hour === 10; // 10:00 AM to 11:00 AM
    return isWeekday && isWithinTime;
  };

  useEffect(() => {
    if (token) {
      // Fetch the data initially 
      getBotOperations();
      
      // Set up polling
      const intervalId = setInterval(() => {
        if (isWithinPollingTime()) {
          getBotOperations();
        }
      }, 5000); 

      // Clear the interval when the component is unmounted
      return () => clearInterval(intervalId);
    }
  }, [token, getBotOperations]);

  return (
    <BotOperationsContext.Provider value={{ operations, loading, error, getBotOperations }}>
      {children}
    </BotOperationsContext.Provider>
  );
};

export { BotOperationsProvider, BotOperationsContext };
