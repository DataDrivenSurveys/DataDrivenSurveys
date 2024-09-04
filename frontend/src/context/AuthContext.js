import React, { createContext, useState, useEffect, useContext } from 'react';
import { GET, POST } from '../code/http_requests';
import { useSnackbar } from './SnackbarContext';
import { Stack } from '@mui/material';
import LoadingAnimation from '../components/feedback/LoadingAnimation';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext)

export const AuthProvider = ({ children }) => {

    const { t } = useTranslation();

    const navigate = useNavigate();

    const { showBottomCenter: showSnackbar } = useSnackbar();

    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(false);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [token, setToken] = useState(localStorage.getItem('token'));

    useEffect(() => {
        if(token) {
            (async () => {
                setLoading(true);
                const response = await GET('/auth/me');
                setLoading(false);

                response.on('2xx', (status, data) => {
                    if(status === 200) {
                        setUser(data.logged_in_as);
                        setIsAuthenticated(true);
                    }
                });

                response.on('4xx', (status, _) => {
                    localStorage.removeItem('token');
                    setToken(null);
                    setIsAuthenticated(false);
                });

            })();
        }
    }, [token]);

    const signin = async (email, password) => {
        const response = await POST('/auth/signin', {
            email,
            password
        }, false);

        response.on('2xx', (status, data) => {
            if(status === 200) {
                setUser(data.logged_in_as);
                setIsAuthenticated(true);
                const token = response.data.token;
                localStorage.setItem('token', token);
                setToken(token);
            }
        });

        response.on('4xx', (status, data) => {
            if(status === 401) {
               showSnackbar(t(data.message.id), "error");
            }
        }); // 4xx
    };

    const signup = async (firstname, lastname, email, password) => {
        const response = await POST('/auth/signup', {
            firstname,
            lastname,
            email,
            password
        }, false);

        response.on('2xx', (status, data) => {
            if(status === 200) {
                showSnackbar(t(data.message.id), "success");
                navigate('/projects');
            }
        });

        response.on('4xx', (status, data) => {
            showSnackbar(t(data.message.id), "error");
        });


    };

    const signout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setIsAuthenticated(false);
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, signin, signup, signout, user }}>
            { loading &&
                <Stack width={"100vw"} height={"100vh"} border={"1px solid red"}>
                    <LoadingAnimation />
                </Stack>
            }

            {!loading && children}
        </AuthContext.Provider>
    );
}

