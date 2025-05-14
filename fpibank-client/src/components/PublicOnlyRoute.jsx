import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { CartContext } from '../App';

const PublicOnlyRoute = ({ children }) => {
  useContext(CartContext);

  const access_token = localStorage.getItem('token');
    
  if (access_token != null){
    return <Navigate to="/"/>
  }

  return children;
};

export default PublicOnlyRoute;
