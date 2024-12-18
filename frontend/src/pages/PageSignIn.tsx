import LoginIcon from '@mui/icons-material/Login';
import { LoadingButton } from '@mui/lab';
import { Button, Stack, Typography } from '@mui/material';
import React, { JSX, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useNavigate } from 'react-router-dom';

import { LoadingPageContent } from '../components/feedback/Loading';
import TextInput from '../components/input/TextInput';
import LayoutMain from '../components/layout/LayoutMain';
import { useAuth } from '../context/AuthContext';
import { useSnackbar } from '../context/SnackbarContext';
import useInput from '../hook/useInput';

const SignIn = (): JSX.Element => {
  const { t } = useTranslation();
  const { signin } = useAuth();
  const { showBottomCenter: showSnackbar } = useSnackbar();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const {
    bind: bindEmail,
    value: email,
    error: errorEmail,
  } = useInput({
    label: t('ui.auth.field.email'),
    value: '',
    minLength: 3,

    maxLength: 50,
    required: true,
  });

  const {
    bind: bindPassword,
    value: password,
    error: errorPassword,
  } = useInput({
    label: t('ui.auth.field.password'),
    value: '',
    minLength: 3,
    maxLength: 50,
    required: true,
  });

  const handleSignIn = useCallback(
    async (event: { preventDefault: () => void }) => {
      event.preventDefault();
      if ([errorEmail, errorPassword].some(error => error)) {
        showSnackbar(t('ui.auth.error.missing_fields'), 'error');
        return;
      }
      setLoading(true);
      try {
        await signin(email, password);
        // Redirect to the page the user tried to access, or default to /projects
        const from = location.state?.from?.pathname || '/projects';
        navigate(from, { replace: true });
      } finally {
        setLoading(false);
      }
    },
    [errorEmail, errorPassword, signin, showSnackbar, email, password, t, navigate, location.state]
  );

  return (
    <LayoutMain
      backUrl={-1}
      header={<Typography variant="h3">{t('ui.auth.titles.signin')}</Typography>}
      horizontalContainerProps={{
        sx: {
          marginTop: 'auto',
          marginBottom: 'auto',
        },
      }}
    >
      <Stack alignItems="center">
        <form onSubmit={handleSignIn}>
          <Stack spacing={2} alignItems="center" width="400px">
            <Stack sx={{ width: '60px', height: '60px' }}>
              <img src="/svg/unauthorized.svg" alt="Logo" />
            </Stack>

            <TextInput showClear {...bindEmail} sxStack={{ width: '100%' }} />
            <TextInput showClear {...bindPassword} type="password" sxStack={{ width: '100%' }} />

            <Stack direction="row" justifyContent="space-between" width="100%">
              <Button component={Link} to="/signup" variant="text" color="primary">
                {t('ui.auth.button.signup')}
              </Button>
              <LoadingButton loading={loading} startIcon={<LoginIcon />} variant="contained" type="submit">
                {t('ui.auth.button.signin')}
              </LoadingButton>
            </Stack>
          </Stack>
        </form>
      </Stack>
    </LayoutMain>
  );
};

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
    return <LoadingPageContent />;
  }

  return <SignIn />;
}

export default React.memo(PageSignIn);
