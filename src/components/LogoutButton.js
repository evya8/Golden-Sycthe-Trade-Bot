import React, { useContext } from 'react';
import { UserContext } from '../contexts/UserContext';
import { useNavigate } from 'react-router-dom';
import Button from '@mui/material/Button';

const LogoutButton = () => {
  const { logout } = useContext(UserContext);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <Button color="inherit"  onClick={handleLogout}>
      Logout
    </Button>
  );
};

export default LogoutButton;
