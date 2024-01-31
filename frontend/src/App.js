import {ThemeProvider, createTheme} from '@mui/material/styles';
import {AuthProvider} from './context/AuthContext';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';

import PageProjectSelection from './components/pages/PageProjectSelection';
import PageProject from './components/pages/PageProject';
import PageCreateProject from './components/pages/PageCreateProject';
import SignUp from './components/auth/SignUp';


import {SnackbarProvider} from './context/SnackbarContext';

import './styles/normalize.css'
import PageParticipantConnection from './components/pages/PageParticipantConnection';
import PageParticipantOauth2Redirect from './components/pages/PageParticipantOauth2Redirect';

import {LocalizationProvider} from '@mui/x-date-pickers';
import {AdapterDayjs} from '@mui/x-date-pickers/AdapterDayjs'
import PageSurveyPlatformOauth2Redirect from './components/pages/PageSurveyPlatformOauth2Redirect';


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
                    <PageProjectSelection/>
                  </AuthProvider>
                }
              />
              <Route
                path="/create"
                element={
                  <AuthProvider>
                    <PageCreateProject/>
                  </AuthProvider>
                }
              />
              <Route
                path="/:projectId"
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


            </Routes>
          </SnackbarProvider>
        </ThemeProvider>
      </Router>
    </LocalizationProvider>
  );
}


export default App;
