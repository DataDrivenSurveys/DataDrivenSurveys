import React from 'react';

import SignIn from './SignIn';
import { useAuth } from '../../context/AuthContext';


function Authorization({ children }) {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return children;
  } else {
    return <SignIn />;
  }
}

export default Authorization;
