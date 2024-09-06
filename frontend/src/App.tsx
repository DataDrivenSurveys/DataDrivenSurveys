import {ThemeProvider, createTheme} from '@mui/material/styles';
import './styles/normalize.css'
import {LocalizationProvider} from '@mui/x-date-pickers';
import {AdapterDayjs} from '@mui/x-date-pickers/AdapterDayjs'
import React from 'react';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';

import SignUp from './components/auth/SignUp';
import PageCreateProject from './components/pages/PageCreateProject';
import Homepage from "./components/pages/PageHomepage";
import PageParticipantConnection from './components/pages/PageParticipantConnection';
import PageParticipantOauth2Redirect from './components/pages/PageParticipantOauth2Redirect';
import PrivacyPolicy from "./components/pages/PagePrivacyPolicy";
import PageProject from './components/pages/PageProject';
import PageProjectSelection from './components/pages/PageProjectSelection';
import PageSurveyPlatformOauth2Redirect from './components/pages/PageSurveyPlatformOauth2Redirect';
import TermsOfService from "./components/pages/PageTermsOfService";
import {AuthProvider} from './context/AuthContext';
import {SnackbarProvider} from './context/SnackbarContext';


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
      fontSize: '1rem'
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
}


const theme = createTheme(themeOptions);


function App() {
  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Router>
        <ThemeProvider theme={theme}>
          <SnackbarProvider>
            <Routes>
              <Route
                path="/"
                element={
                  <AuthProvider>
                    <Homepage/>
                  </AuthProvider>
                }
              />
              <Route
                path="/projects"
                element={
                  <AuthProvider>
                    <PageProjectSelection/>
                  </AuthProvider>
                }
              />
              <Route
                path="/projects/create"
                element={
                  <AuthProvider>
                    <PageCreateProject/>
                  </AuthProvider>
                }
              />
              <Route
                path="/projects/:projectId"
                element={
                  <AuthProvider>
                    <PageProject/>
                  </AuthProvider>
                }
              />

              <Route
                path="/signup"
                element={
                  <AuthProvider>
                    <SignUp/>
                  </AuthProvider>
                }
              />
              <Route
                path="/dist/:projectShortId"
                element={
                  <PageParticipantConnection/>
                }
              />
              <Route
                path="/dist/redirect/:provider"
                element={
                  <PageParticipantOauth2Redirect/>
                }
              />

              <Route
                path="/survey_platform/redirect/:surveyPlatform"
                element={
                  <AuthProvider>
                    <PageSurveyPlatformOauth2Redirect/>
                  </AuthProvider>
                }
              />

              <Route
                path="/privacy-policy"
                element={
                  <PrivacyPolicy/>
                }
              />

              <Route
                path="/terms-of-service"
                element={
                  <TermsOfService/>
                }
              />

            </Routes>
          </SnackbarProvider>
        </ThemeProvider>
      </Router>
    </LocalizationProvider>
  );
}


export default App;
