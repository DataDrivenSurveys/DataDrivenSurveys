import React, { createContext, useState, useEffect, useContext } from 'react';
import { useTranslation } from 'react-i18next';

import { useSnackbar } from './SnackbarContext';
import { GET, POST } from '../code/http_requests';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const { t } = useTranslation();
  const { showBottomCenter: showSnackbar } = useSnackbar();

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // Default to true to indicate that the token check is happening
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('tokenDDS'));

  // Effect to check if a token exists and validate it
  useEffect(() => {
    const validateToken = async () => {
      if (token) {
        try {
          setLoading(true); // Start the loading spinner
          const response = await GET('/auth/me'); // Verify token

          response.on('2xx', (status, data) => {
            if (status === 200) {
              setUser(data.logged_in_as); // Set the user
              setIsAuthenticated(true);  // Mark user as authenticated
            }
          });

          response.on('4xx', () => {
            // Token invalid, remove it
            localStorage.removeItem('tokenDDS');
            setToken(null);
            setIsAuthenticated(false);
          });
        } catch (error) {
          console.error("Error verifying token:", error);
        } finally {
          setLoading(false);  // End the loading spinner once request completes
        }
      } else {
        setLoading(false);  // No token, stop loading
      }
    };

    validateToken();
  }, [token]);

  // Sign in method
  const signin = async (email, password) => {
    const response = await POST('/auth/signin', { email, password }, false);

    response.on('2xx', (status, data) => {
      if (status === 200) {
        setUser(data.logged_in_as);
        setIsAuthenticated(true);
        const token = data.token;
        localStorage.setItem('tokenDDS', token); // Store token in localStorage
        setToken(token);
      }
    });

    response.on('4xx', (status, data) => {
      if (status === 401) {
        showSnackbar(t(data.message.id), "error");
      }
    });
  };

  const signout = () => {
    localStorage.removeItem('tokenDDS');
    setToken(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, signin, signout, user, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
