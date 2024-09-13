import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../context/AuthContext';
import SignIn from "../auth/SignIn";
import {LoadingPageContent} from "../feedback/Loading";


function PageSignIn(): JSX.Element {
  const { isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && isAuthenticated) {
      // Redirect authenticated users to /projects if they visit the signin page
      navigate('/projects', { replace: true });
    }
  }, [isAuthenticated, loading, navigate]);

  if (loading) {
    // You can render a spinner or nothing while the authentication status is being checked
    return <LoadingPageContent/>;
  }

  return <SignIn/>
}


export default React.memo(PageSignIn);
