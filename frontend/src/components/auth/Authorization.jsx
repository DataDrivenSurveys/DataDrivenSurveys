import React from 'react';
import { useAuth } from '../../context/AuthContext';
import SignIn from './SignIn';


function Authorization({ children }) {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return children;
  } else {
    return <SignIn />;
  }
}

export default Authorization;
