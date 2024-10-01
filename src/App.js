import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { UserProvider } from './contexts/UserContext';
import { UserSettingsProvider } from './contexts/UserSettingsContext';
import { SymbolsFilterProvider } from './contexts/SymbolsFilterContext';
import { BotOperationsProvider } from './contexts/BotOperationsContext';
import { BacktestProvider } from './contexts/BacktestContext';
import Home from './components/Home';
import Register from './components/Register';
import Login from './components/Login';
import UserSettings from './components/UserSettings';
import UserDashboard from './components/UserDashboard';
import Nav from './components/Nav';
import SideNav from './components/SideNav';
import Footer from './components/Footer';
import Backtesting from './components/Backtesting';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const App = () => {
  const location = useLocation();

  // Check if the current route is Home, Login, or Register
  const isHiddenPage = ['/','/login', '/register'].includes(location.pathname);

  return (
    <UserProvider>
      <SymbolsFilterProvider>
        <UserSettingsProvider>
          <BotOperationsProvider>
            <BacktestProvider> 
             {/* Flexbox wrapper to ensure footer sticks to bottom */}
             <div style={{
              display: 'flex',
              flexDirection: 'column',
              minHeight: '100vh',
            }}>
              {/* Nav at the top */}
              <Nav isHomePage={isHiddenPage} />

              <div style={{ flex: 1, display: 'flex' }}>
                {/* Conditionally render SideNav if not on Home, Login, or Register */}
                {!isHiddenPage && (
                  <div style={{
                    width: '180px',
                    position: 'fixed',
                    top: '64px',
                    bottom: '0',
                    height: 'calc(100vh - 64px)',
                  }}>
                    <SideNav />
                  </div>
                )}

                <div style={{
                  flexGrow: 1,
                  marginLeft: isHiddenPage ? '0' : '180px', // Shift content to right if SideNav is visible
                  padding: '20px',
                  marginTop: '64px', // Keep content below Nav
                }}>
                  {/* Main content */}
                  <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/user-settings" element={<UserSettings />} />
                    <Route path="/user-dashboard" element={<UserDashboard />} />
                    <Route path="/backtest" element={<Backtesting />} />
                  </Routes>
                </div>
              </div>

              {/* Toast notifications */}
              <ToastContainer
                position="top-center"
                autoClose={4000}
                hideProgressBar={true}
                closeOnClick
                pauseOnHover
                draggable
                theme="dark"
              />

              {/* Footer */}
              <Footer />
            </div>
            </BacktestProvider>
          </BotOperationsProvider>
        </UserSettingsProvider>
      </SymbolsFilterProvider>
    </UserProvider>
  );
};

export default App;
