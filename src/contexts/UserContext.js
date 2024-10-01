import React, { createContext, useState, useEffect, useRef, useCallback } from 'react';
import axiosInstance from '../utils/axiosInstance';
import {  toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { setNavigate } from '../utils/axiosInstance';


const UserContext = createContext();

const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access_token'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const isRefreshing = useRef(false);  // Use ref to persist across re-renders
  const refreshSubscribers = useRef([]);  // Use ref for subscribers
  

  // Notify all subscribers when token is refreshed
  const onRefreshed = (newToken) => {
    refreshSubscribers.current.forEach((callback) => callback(newToken));
    refreshSubscribers.current = [];
  };

  const subscribeTokenRefresh = (callback) => {
    refreshSubscribers.current.push(callback);
  };

  // Refresh the access token
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
        // If token refresh fails, log out user and redirect
        toast.error('Session expired. Please log in again.');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
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

  // Axios interceptor to handle token expiration
  useEffect(() => {
    const responseInterceptor = axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Only refresh token if it's a 401 error and the request hasn't been retried yet
        if (error.response && error.response.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            const newAccessToken = await refreshToken();  // Refresh token and retry request

            // Set new token in the original request and retry it
            originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
            return axiosInstance(originalRequest);
          } catch (err) {
            return Promise.reject(err);  // Propagate the error if token refresh fails
          }
        }

        return Promise.reject(error);  // Propagate other errors
      }
    );

    // Eject the interceptor when the component unmounts
    return () => {
      axiosInstance.interceptors.response.eject(responseInterceptor);
    };
  }, [refreshToken]);

  useEffect(() => {
    setNavigate(navigate);  // Set navigate function for axios
  }, [navigate]);

  // Listen for changes in token or user and update state accordingly
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
     
      // Fetch user data after getting the token
      const userResponse = await axiosInstance.get('/user/', {
        headers: { Authorization: `Bearer ${response.data.access}` },
      });
      
      setUser(userResponse.data);  // Set user in state only
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
      // Handle logout failure (if the token is invalid or logout request fails)
      toast.error('Logout failed');
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
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
