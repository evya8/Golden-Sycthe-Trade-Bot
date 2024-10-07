import React, { useEffect, useState, useContext, useRef, useCallback } from 'react';
import axios from 'axios';
import { UserSettingsContext } from '../contexts/UserSettingsContext';

const TopMarketMovers = ({ top = 10 }) => {
  const [gainers, setGainers] = useState([]);
  const [losers, setLosers] = useState([]);
  const [mostActives, setMostActives] = useState([]);
  const [loading, setLoading] = useState(true);
  const { settings } = useContext(UserSettingsContext);
  const { alpaca_api_key, alpaca_api_secret } = settings;
  const contentRef = useRef(null);

  // Memoized fetch function using useCallback to avoid recreating it on every render
  const fetchTopMovers = useCallback(async () => {
    if (!alpaca_api_key || !alpaca_api_secret) {
      console.error('Missing Alpaca API key or secret');
      return;
    }

    try {
      // Fetch gainers and losers
      const moversResponse = await axios.get(
        `https://data.alpaca.markets/v1beta1/screener/stocks/movers`,
        {
          params: { top },
          headers: {
            'APCA-API-KEY-ID': alpaca_api_key,
            'APCA-API-SECRET-KEY': alpaca_api_secret,
          },
        }
      );
      setGainers(moversResponse.data.gainers || []);
      setLosers(moversResponse.data.losers || []);

      // Fetch most active stocks
      const mostActivesResponse = await axios.get(
        `https://data.alpaca.markets/v1beta1/screener/stocks/most-actives`,
        {
          headers: {
            'APCA-API-KEY-ID': alpaca_api_key,
            'APCA-API-SECRET-KEY': alpaca_api_secret,
          },
        }
      );

      const mostActivesSymbols = mostActivesResponse.data.most_actives.map(stock => stock.symbol);

      // Fetch snapshot for the most active symbols
      const snapshotResponse = await axios.get(
        `https://data.alpaca.markets/v2/stocks/snapshots`,
        {
          params: { symbols: mostActivesSymbols.join(',') },
          headers: {
            'APCA-API-KEY-ID': alpaca_api_key,
            'APCA-API-SECRET-KEY': alpaca_api_secret,
          },
        }
      );

      const mostActivesWithChange = mostActivesSymbols.map(symbol => {
        const stockData = snapshotResponse.data[symbol];
        if (!stockData || !stockData.prevDailyBar || !stockData.dailyBar) {
          return {
            symbol,
            percent_change: 'N/A',
            arrow: '',
          };
        }

        const previousClose = stockData.prevDailyBar.c || 0;
        const latestClose = stockData.dailyBar.c || 0;
        const percentChange = ((latestClose - previousClose) / previousClose) * 100;

        return {
          symbol,
          percent_change: percentChange.toFixed(2),
          arrow: percentChange >= 0 ? '▲' : '▼'
        };
      });

      setMostActives(mostActivesWithChange);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching market data:', error);
      setLoading(false);
    }
  }, [alpaca_api_key, alpaca_api_secret, top]); // Dependencies for useCallback

  // Fetch top movers on API key and secret changes
  useEffect(() => {
    if (alpaca_api_key && alpaca_api_secret) {
      fetchTopMovers();
    }
  }, [fetchTopMovers, alpaca_api_key, alpaca_api_secret]); 

  useEffect(() => {
    const calculateAnimationSpeed = () => {
      if (contentRef.current) {
        const contentWidth = contentRef.current.scrollWidth;
        const multiplier = 30; // Adjust the multiplier for speed control
        const animationDuration = (contentWidth / multiplier) + 's';
        contentRef.current.style.animationDuration = animationDuration;
      }
    };

    calculateAnimationSpeed();
    window.addEventListener('resize', calculateAnimationSpeed);
    return () => window.removeEventListener('resize', calculateAnimationSpeed);
  }, [gainers, losers, mostActives]);

  if (loading) {
    return <div>Loading...</div>;
  }

  const renderMoverGroup = (type, movers) => (
    <>
      <span style={{ margin: '0 10px', fontWeight: 'bold' }}>{type}:</span>
      {movers.map((mover, index) => (
        <span key={index} style={{ margin: '0 7px', color: mover.color }}>
          {mover.symbol}: {mover.percent_change}%{mover.arrow}
        </span>
      ))}
    </>
  );

  return (
    <div
      style={{
        width: '100%',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        backgroundColor: '#333',
        color: '#fff',
        padding: '10px 0',
        position: 'relative',
      }}
    >
      <div
        ref={contentRef}
        style={{
          display: 'inline-block',
          whiteSpace: 'nowrap',
          animation: 'scroll-left linear infinite',
        }}
      >
        {/* Render the groups of movers by type */}
        {[...Array(2)].map((_, i) => (
          <React.Fragment key={i}>
            {renderMoverGroup(
              'Most Actives',
              mostActives.map(mover => ({
                ...mover,
                color: mover.percent_change >= 0 ? 'green' : 'red',
              }))
            )}
            {renderMoverGroup(
              'Gainers',
              gainers.map(mover => ({ ...mover, color: 'green', arrow: '▲' }))
            )}
            {renderMoverGroup(
              'Losers',
              losers.map(mover => ({ ...mover, color: 'red', arrow: '▼' }))
            )}
          </React.Fragment>
        ))}
      </div>
      <style>
        {`
          @keyframes scroll-left {
            0% {
              transform: translateX(100%);
            }
            100% {
              transform: translateX(-100%);
            }
          }
        `}
      </style>
    </div>
  );
};

export default TopMarketMovers;
