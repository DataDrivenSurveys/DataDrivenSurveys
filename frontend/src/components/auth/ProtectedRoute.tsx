import React, { JSX, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import { useAuth } from '../../context/AuthContext';
import { LoadingPageContent } from '../feedback/Loading'; // Full page loader

interface ProtectedRouteProps {
  children: React.ReactNode;
  loading?: boolean; // Additional loading for child components
}

const ProtectedRoute = ({ children, loading = false }: ProtectedRouteProps): JSX.Element => {
  const { isAuthenticated, loading: authLoading } = useAuth(); // Get auth states from context
  const location = useLocation();
  const navigate = useNavigate();

  // Redirect to /signin if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/signin', { state: { from: location }, replace: true });
    }
  }, [authLoading, isAuthenticated, navigate, location]);

  // Show full-page loader when authentication or the page is loading
  if (authLoading || loading) {
    return <LoadingPageContent />;
  }

  // Render child components once authentication and loading are done
  return <>{children}</>;
};

export default ProtectedRoute;
