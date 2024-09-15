import React, {createContext, useState, useEffect, useContext} from 'react';
import {useTranslation} from 'react-i18next';
import {useNavigate} from "react-router-dom";

import {API} from "../types";
import {useSnackbar} from './SnackbarContext';
import {GET, POST} from '../code/http_requests';

interface AuthContextType {
  isAuthenticated: boolean;
  signin: (email: string, password: string) => Promise<void>;
  signout: () => void;
  signup: (
    firstname: string,
    lastname: string,
    email: string,
    password: string
  ) => Promise<void>;
  user: API.Auth.User | null;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};


interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider = ({children}: AuthProviderProps): JSX.Element => {
  const {t} = useTranslation();
  const {showBottomCenter: showSnackbar} = useSnackbar();
  const navigate = useNavigate();

  const [user, setUser] = useState<API.Auth.User | null>(null);
  const [loading, setLoading] = useState<boolean>(true); // Default to true to indicate that the token check is happening
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [token, setToken] = useState<string | null>(localStorage.getItem('tokenDDS'));

  // Effect to check if a token exists and validate it
  useEffect(() => {
    const validateToken = async (): Promise<void> => {
      if (token) {
        try {
          setLoading(true); // Start the loading spinner
          const response = await GET('/auth/me'); // Verify token

          response.on('2xx', (status: number, data: API.Auth.ResponseSession) => {
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
  const signin = async (email: string, password: string): Promise<void> => {
    const response = await POST('/auth/signin', {email, password}, false);

    response.on('2xx', (status: number, data: API.Auth.ResponseSignIn) => {
      if (status === 200) {
        // setUser(data.logged_in_as);
        setIsAuthenticated(true);
        const token = data.token;
        localStorage.setItem('tokenDDS', token); // Store token in localStorage
        setToken(token);
      }
    });

    response.on('4xx', (status: number, data: API.ResponseData) => {
      if (status === 401) {
        showSnackbar(t(data.message.id), "error");
      }
    });
  };

  const signout = (): void => {
    localStorage.removeItem('tokenDDS');
    setToken(null);
    setIsAuthenticated(false);
  };

  const signup = async (
    firstname: string,
    lastname: string,
    email: string,
    password: string
  ): Promise<void> => {
    const response = await POST('/auth/signup', {
      firstname,
      lastname,
      email,
      password
    }, false);

    response.on('2xx', (status: number, data: API.ResponseData) => {
      if (status === 200) {
        showSnackbar(t(data.message.id), "success");
        navigate('/projects');
      }
    });

    response.on('4xx', (_: number, data: API.ResponseData) => {
      showSnackbar(t(data.message.id), "error");
    });
  };

  return (
    <AuthContext.Provider value={{isAuthenticated, signin, signout, signup, user, loading}}>
      {children}
    </AuthContext.Provider>
  );
};
