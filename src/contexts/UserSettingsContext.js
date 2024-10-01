import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import axiosInstance from '../utils/axiosInstance';
import { UserContext } from './UserContext';
import { toast } from 'react-toastify';

const UserSettingsContext = createContext();

const UserSettingsProvider = ({ children }) => {
  const { token } = useContext(UserContext);
  const [settings, setSettings] = useState({
    filter_sector: [],
    filter_symbol: [],
    alpaca_api_key: '',
    alpaca_api_secret: '',
    position_size: 10,
    bot_active: false, 
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getUserSettings = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      
      const response = await axiosInstance.get('/user-settings/');
      const data = response.data;
      data.filter_sector = JSON.parse(data.filter_sector || '[]');
      data.filter_symbol = JSON.parse(data.filter_symbol || '[]');
      data.position_size = parseInt(data.position_size, 10);
      data.bot_active = !!data.bot_active;
      setSettings(data);
      // console.log(data);
      setLoading(false);
    } catch (error) {
      setError(error.response?.data || 'Failed to fetch settings');
      toast.error(error.response?.data || 'Failed to fetch settings');
      setLoading(false);
    }
  }, [token]);

  const saveUserSettings = async (userSettings) => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
    
      const data = {
        ...userSettings,
        filter_sector: JSON.stringify(userSettings.filter_sector),
        filter_symbol: JSON.stringify(userSettings.filter_symbol),
      };
      const response = await axiosInstance.post('/user-settings/', data);
      const updatedData = response.data;
      updatedData.filter_sector = JSON.parse(updatedData.filter_sector || '[]');
      updatedData.filter_symbol = JSON.parse(updatedData.filter_symbol || '[]');
      updatedData.position_size = parseInt(updatedData.position_size, 10);
      setSettings(response.data);
      setLoading(false);
      toast.success('Settings saved successfully');
    } catch (error) {
      setError(error.response?.data || 'Failed to save settings');
      toast.error(error.response?.data || 'Failed to save settings');
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      getUserSettings();
    }
  }, [token, getUserSettings]);

  return (
    <UserSettingsContext.Provider value={{ settings, setSettings, saveUserSettings, loading, error }}>
      {children}
    </UserSettingsContext.Provider>
  );
};

export { UserSettingsProvider, UserSettingsContext };
