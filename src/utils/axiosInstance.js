import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',  // Your API base URL
  timeout: 200000,
  headers: {
    'Content-Type': 'application/json',
    accept: 'application/json',
  },
});

// Authorization header to requests if token is available
axiosInstance.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Store navigate function
let navigateFn = null;
export const setNavigate = (navigateFunction) => {
  navigateFn = navigateFunction;
};

// Response interceptor to refresh tokens
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Prevent retrying the refresh token request itself
    if (originalRequest.url.includes('/token/refresh/')) {
      // If refreshing token fails, log out the user
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');

      if (navigateFn) {
        navigateFn('/login');  // Redirect to login page
      }
      return Promise.reject(error);  // Stop retrying
    }

    // Handle 401 error for regular requests
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // Refresh the access token
        const response = await axiosInstance.post('/token/refresh/', { refresh: refreshToken });
        const newAccessToken = response.data.access;

        // Save new access token and refresh token (if provided)
        localStorage.setItem('access_token', newAccessToken);

        // Check if the response contains a new refresh token and save it
        if (response.data.refresh) {
          localStorage.setItem('refresh_token', response.data.refresh);  // Save the new refresh token
        }

        // Retry the original request with the new access token
        axiosInstance.defaults.headers['Authorization'] = `Bearer ${newAccessToken}`;
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;

        return axiosInstance(originalRequest);  // Retry original request with new token
      } catch (err) {
        console.error('Token refresh failed:', err);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');

        if (navigateFn) {
          navigateFn('/login');  // Redirect to login page
        }

        return Promise.reject(err);  // Stop retrying
      }
    }

    return Promise.reject(error);
  }
);

export default axiosInstance;
