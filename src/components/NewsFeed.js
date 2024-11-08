import React, { useEffect, useState, useContext, useCallback } from 'react';
import { UserSettingsContext } from '../contexts/UserSettingsContext'; // Import the context where the API keys are stored
import { Typography } from '@mui/material';

const NewsFeed = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiKeyError, setApiKeyError] = useState(false); // State to track missing API key

  // Get Alpaca API keys from the user settings context
  const { settings } = useContext(UserSettingsContext);
  const { alpaca_api_key, alpaca_api_secret } = settings;

  // Function to fetch the latest 20 news articles
  const fetchLatestNews = useCallback(async () => {
    if (!alpaca_api_key || !alpaca_api_secret) {
      setApiKeyError(true); // Set the error flag if API key is missing
      return;
    }

    setApiKeyError(false); // Reset error if keys are available
    setLoading(true);

    try {
      const response = await fetch(
        `https://data.alpaca.markets/v1beta1/news?limit=20&include_content=true`,
        {
          headers: {
            'APCA-API-KEY-ID': alpaca_api_key,
            'APCA-API-SECRET-KEY': alpaca_api_secret,
          },
        }
      );
      const data = await response.json();
      setNews(data.news);
    } catch (error) {
      console.error('Error fetching news:', error);
    } finally {
      setLoading(false); // Ensure loading is stopped after fetch completes
    }
  }, [alpaca_api_key, alpaca_api_secret]); // Memoize function based on API keys

  useEffect(() => {
    if (alpaca_api_key && alpaca_api_secret) {
      fetchLatestNews();
    }
  }, [alpaca_api_key, alpaca_api_secret, fetchLatestNews]); // Include fetchLatestNews in the dependencies array

  const styles = {
    newsFeed: {
      position: 'fixed',
      right: 0,
      top: '60px',
      width: '240px',
      height: '100vh',
      backgroundColor: '#333', // Dark background
      color: '#fff',
      overflowY: 'auto',
      padding: '8px', // Reduced padding for the entire feed
      boxShadow: '-3px 0 5px rgba(0, 0, 0, 0.5)',
      zIndex: 1000,
    },
    newsContainer: {
      display: 'flex',
      flexDirection: 'column',
      width: '100%',
    },
    newsItem: {
      padding: '4px', // Further reduced padding for news items
      borderRadius: '4px', // Slightly smaller border radius
      backgroundColor: '#444', // Darker news item background
    },
    headline: {
      color: '#4da6ff', // Lighter blue for headlines for better readability
      fontSize: '0.8rem', // Slightly smaller font size for the headline
      textDecoration: 'none',
      fontWeight: 'bold', // Bold text to make the headline stand out
    },
    summary: {
      fontSize: '0.7rem', // Further reduced font for the summary
      color: '#e0e0e0', // Light text for readability
    },
    source: {
      fontStyle: 'italic',
      color: '#ccc', // Lighter gray for source text
      fontSize: '0.65rem', // Smaller font for the source
    },
    thumbnail: {
      width: '100%', // Full width for the thumbnail
      height: 'auto',
      borderRadius: '2px', // Smaller border radius for the thumbnail
    },
    hr: {
      borderTop: '1px solid #555',
      marginTop: '4px', // Further reduced margin for hr
    },
  };
  

  return (
    <div style={styles.newsFeed}>
      <div className="news-container" style={styles.newsContainer}>
        <Typography variant="subtitle" textAlign={"center"} gutterBottom color="#f0a500" sx={{ marginBottom: 1, marginTop: 1 }}>
          News Feed
        </Typography>
        {apiKeyError ? (
          <p>Error: Missing Alpaca API key or secret.</p>
        ) : loading ? (
          <p>Loading news...</p>
        ) : news.length > 0 ? (
          news.map((item, index) => (
            <div key={index} style={styles.newsItem}>
              <img
                src={item.images?.[0]?.url || "https://img.freepik.com/free-vector/people-analyzing-growth-charts_23-2148866843.jpg?t=st=1725960038~exp=1725963638~hmac=ad330f60d343b3e28a42ed2b472e88a6847818422e38d6489c1f7836184d7eef&w=1480"}
                alt="thumbnail"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = "https://img.freepik.com/free-vector/people-analyzing-growth-charts_23-2148866843.jpg?t=st=1725960038~exp=1725963638~hmac=ad330f60d343b3e28a42ed2b472e88a6847818422e38d6489c1f7836184d7eef&w=1480";
                }}
                style={styles.thumbnail}
              />
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                style={styles.headline}
              >
                <h4>{item.headline}</h4>
              </a>
              <p style={styles.summary}>{item.summary}</p>
              <small style={styles.source}>Source: {item.source}</small>
              <hr style={styles.hr} />
            </div>
          ))
        ) : (
          <p>No news available.</p>
        )}
      </div>
    </div>
  );
};

export default NewsFeed;
