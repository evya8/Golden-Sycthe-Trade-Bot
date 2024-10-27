import React, { createContext, useState, useEffect, useRef, useCallback } from 'react';
import axiosInstance from '../utils/axiosInstance';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { setNavigate } from '../utils/axiosInstance';

const UserContext = createContext();

const UserProvider = ({ children }) => {
  // Persist the user data in localStorage and restore on refresh (NEW)
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')) || null); // Change: Load user from localStorage
  const [token, setToken] = useState(localStorage.getItem('access_token'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const isRefreshing = useRef(false);
  const refreshSubscribers = useRef([]);

  const onRefreshed = (newToken) => {
    refreshSubscribers.current.forEach((callback) => callback(newToken));
    refreshSubscribers.current = [];
  };

  const subscribeTokenRefresh = (callback) => {
    refreshSubscribers.current.push(callback);
  };

  const refreshToken = useCallback(async () => {
    const refreshToken = localStorage.getItem('refresh_token');

    if (!refreshToken) {
      toast.error('Session expired. Please log in again.');
      navigate('/login');
      return Promise.reject('No refresh token available');
    }

    if (!isRefreshing.current) {
      isRefreshing.current = true;
      try {
        const response = await axiosInstance.post('/token/refresh/', { refresh: refreshToken });
        const newAccessToken = response.data.access;

        localStorage.setItem('access_token', newAccessToken);
        setToken(newAccessToken);
        axiosInstance.defaults.headers['Authorization'] = `Bearer ${newAccessToken}`;
        onRefreshed(newAccessToken);
        return newAccessToken;
      } catch (err) {
        toast.error('Session expired. Please log in again.');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');  // NEW: Clear user from localStorage on logout
        setUser(null);
        setToken(null);
        navigate('/login');
        return Promise.reject(err);
      } finally {
        isRefreshing.current = false;
      }
    }

    return new Promise((resolve) => {
      subscribeTokenRefresh((newToken) => resolve(newToken));
    });
  }, [navigate]);

  useEffect(() => {
    const responseInterceptor = axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response && error.response.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            const newAccessToken = await refreshToken();

            originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
            return axiosInstance(originalRequest);
          } catch (err) {
            return Promise.reject(err);
          }
        }

        return Promise.reject(error);
      }
    );

    return () => {
      axiosInstance.interceptors.response.eject(responseInterceptor);
    };
  }, [refreshToken]);

  useEffect(() => {
    setNavigate(navigate);
  }, [navigate]);

  useEffect(() => {
    const handleStorageChange = (event) => {
      if (event.key === 'access_token') {
        setToken(localStorage.getItem('access_token'));
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  // User registration
  const register = async (userData) => {
    setLoading(true);
    setError(null);
    try {
      await axiosInstance.post('/register/', userData);
      setLoading(false);
      toast.success('Registered successfully');
      navigate('/login');
    } catch (error) {
      setError(error.response?.data || 'Registration failed');
      toast.error('Registration failed');
      setLoading(false);
    }
  };

  // User login
  const login = async (userData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axiosInstance.post('/token/', userData);
      setToken(response.data.access);
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      
      // Fetch user data after login
      const userResponse = await axiosInstance.get('/user/', {
        headers: { Authorization: `Bearer ${response.data.access}` },
      });

      setUser(userResponse.data);  // Save user data in state
      localStorage.setItem('user', JSON.stringify(userResponse.data));  // NEW: Persist user in localStorage
      setLoading(false);
      toast.success('Logged in successfully');
      navigate('/user-dashboard');
    } catch (error) {
      const errMsg = error.response?.data?.error || 'Login failed';
      setError(errMsg);
      toast.error(errMsg);
      setLoading(false);
    }
  };

  // User logout
  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    try {
      await axiosInstance.post('/logout/', { refresh: refreshToken });
    } catch (error) {
      toast.error('Logout failed');
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');  // NEW: Clear user from localStorage on logout
      setUser(null);
      setToken(null);
      toast.success('You have logged out');
      navigate('/login');
    }
  };

  return (
    <UserContext.Provider value={{ user, token, loading, error, register, login, logout, setUser, setToken, isAuthenticated: !!token }}>
      {children}
    </UserContext.Provider>
  );
};

export { UserProvider, UserContext };
