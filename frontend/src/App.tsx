// import loadable from '@loadable/component';
import './styles/normalize.css';

import { createTheme, ThemeProvider } from '@mui/material/styles';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import ProtectedRoute from './components/auth/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import { SnackbarProvider } from './context/SnackbarContext';
import PageCreateProject from './pages/PageCreateProject';
import PageHomepage from './pages/PageHomepage';
import PageParticipantConnection from './pages/PageParticipantConnection';
import PageParticipantOauth2Redirect from './pages/PageParticipantOauth2Redirect';
import PagePrivacyPolicy from './pages/PagePrivacyPolicy';
import PageProject from './pages/PageProject';
import PageProjectSelection from './pages/PageProjectSelection';
import PageSignIn from './pages/PageSignIn';
import PageSignUp from './pages/PageSignUp';
import PageSurveyPlatformOauth2Redirect from './pages/PageSurveyPlatformOauth2Redirect';
import PageTermsOfService from './pages/PageTermsOfService';

// const PagePrivacyPolicy = loadable(() => import('./pages/PagePrivacyPolicy'));
// const PageTermsOfService = loadable(() => import('./pages/PageTermsOfService'));

export const themeOptions = {
  typography: {
    fontWeightLight: 400,
    fontWeightRegular: 400,
    fontWeightMedium: 500,
    fontWeightBold: 700,
    h1: {
      fontSize: '2rem',
    },
    h2: {
      fontSize: '1.8rem',
    },
    h3: {
      fontSize: '1.6rem',
    },
    h4: {
      fontSize: '1.4rem',
    },
    h5: {
      fontSize: '1.2rem',
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
    },
    body1: {
      fontSize: '1rem',
      letterSpacing: 'normal',
    },
    body2: {
      fontSize: '1rem',
      fontWeight: 500,
    },
    button: {
      fontSize: '1rem',
    },
    caption: {
      fontSize: '0.9rem',
    },
  },
  // palette: {
  //   mode: 'light',
  //   primary: {
  //     main: '#008CCC',
  //   },
  //   secondary: {
  //     main: '#cc4100',
  //   },
  //   error: {
  //     main: '#CC142D',
  //   },
  //   warning: {
  //     main: '#FF5419',
  //   },
  //   success: {
  //     main: '#2E7D32',
  //   },
  //   info: {
  //     main: '#0025cc',
  //   },
  // },
};

const theme = createTheme(themeOptions);

function App(): React.JSX.Element {
  return (
    <React.StrictMode>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <BrowserRouter>
          <ThemeProvider theme={theme}>
            <SnackbarProvider>
              <AuthProvider>
                {/*Static page routes*/}
                <Routes>
                  <Route path="/" element={<PageHomepage />} />

                  <Route path="/privacy-policy" element={<PagePrivacyPolicy />} />

                  <Route path="/terms-of-service" element={<PageTermsOfService />} />

                  {/*Signin and Signup Routes*/}
                  <Route path="/signin" element={<PageSignIn />} />
                  <Route path="/signup" element={<PageSignUp />} />

                  {/*Projects Routes*/}
                  <Route
                    path="/projects"
                    element={
                      <ProtectedRoute>
                        <PageProjectSelection />
                      </ProtectedRoute>
                    }
                  />

                  <Route
                    path="/projects/create"
                    element={
                      <ProtectedRoute>
                        <PageCreateProject />
                      </ProtectedRoute>
                    }
                  />

                  <Route
                    path="/projects/:projectId"
                    element={
                      <ProtectedRoute>
                        <PageProject />
                      </ProtectedRoute>
                    }
                  />

                  {/*Distribution Routes*/}
                  <Route path="/dist" element={<PageParticipantConnection placeholder={true} />} />

                  <Route path="/dist/:projectShortId" element={<PageParticipantConnection />} />

                  <Route path="/dist/redirect/:provider" element={<PageParticipantOauth2Redirect />} />

                  <Route
                    path="/survey_platform/redirect/:surveyPlatform"
                    element={<PageSurveyPlatformOauth2Redirect />}
                  />
                </Routes>
              </AuthProvider>
            </SnackbarProvider>
          </ThemeProvider>
        </BrowserRouter>
      </LocalizationProvider>
    </React.StrictMode>
  );
}

export default App;
