import React, { useEffect, useState, useContext, useCallback } from 'react';
import { UserSettingsContext } from '../contexts/UserSettingsContext'; // Import the context where the API keys are stored

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
      backgroundColor: '#333',
      color: '#fff',
      overflowY: 'auto',
      padding: '10px',
      boxShadow: '-3px 0 5px rgba(0, 0, 0, 0.5)',
      zIndex: 1000,
    },
    newsContainer: {
      display: 'flex',
      flexDirection: 'column',
      width: '100%',
    },
    newsItem: {
      padding: '5px', // Reduced padding
      marginBottom: '10px', // Reduced margin
      borderRadius: '5px',
      backgroundColor: '#444',
    },
    headline: {
      color: '#0099cc',
      fontSize: '0.85rem', // Reduced font size for the headline
      textDecoration: 'none',
    },
    summary: {
      fontSize: '0.75rem', // Smaller font for the summary
      marginTop: '3px', // Reduced margin
    },
    source: {
      fontStyle: 'italic',
      color: '#ccc',
      fontSize: '0.7rem', // Smaller font for the source
      marginTop: '3px',
    },
    thumbnail: {
      width: '100%', // Full width
      height: 'auto',
      borderRadius: '3px', // Smaller border radius
    },
    hr: {
      borderTop: '1px solid #555',
      marginTop: '5px', // Reduced margin
    },
  };

  return (
    <div style={styles.newsFeed}>
      <div className="news-container" style={styles.newsContainer}>
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
