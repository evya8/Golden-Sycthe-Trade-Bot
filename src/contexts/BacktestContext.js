import React, { createContext, useState } from 'react';
import axiosInstance from '../utils/axiosInstance';

export const BacktestContext = createContext();

export const BacktestProvider = ({ children }) => {
    const [backtestResult, setBacktestResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const runBacktest = async (userId, tradeFrequency, symbol, startDate, endDate, totalCapital, positionSize) => {
        setLoading(true);
        setError(null);

        console.log("Backtest initiated with the following parameters:", {
            userId,
            tradeFrequency,
            symbol,
            startDate,
            endDate,
            totalCapital,
            positionSize,
        });

        try {
            const response = await axiosInstance.post('/backtest/', {
                user_id: userId,
                trade_frequency: tradeFrequency,
                symbol: symbol,
                start_date: startDate,
                end_date: endDate,
                total_capital: totalCapital,
                position_size: positionSize,
            });

            console.log("Backtest response:", response.data);
            setBacktestResult(response.data);
            setLoading(false);
        } catch (err) {
            console.log("Error occurred during backtest:", err.message);
            setError(err.message);
            setLoading(false);
        }
    };

    return (
        <BacktestContext.Provider value={{ backtestResult, loading, error, runBacktest }}>
            {children}
        </BacktestContext.Provider>
    );
};
