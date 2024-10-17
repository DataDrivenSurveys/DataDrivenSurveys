import LoginIcon from '@mui/icons-material/Login';
import { LoadingButton } from '@mui/lab';
import { Button, Stack, Typography } from '@mui/material';
import type { JSX } from 'react';
import React, { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

import TextInput from '../components/input/TextInput';
import LayoutMain from '../components/layout/LayoutMain';
import { useAuth } from '../context/AuthContext';
import { useSnackbar } from '../context/SnackbarContext';
import useInput from '../hook/useInput';

const PageSignUp = (): JSX.Element => {
  const { t } = useTranslation();

  const { signup } = useAuth();

  const { showBottomCenter: showSnackbar } = useSnackbar();

  const [loading, setLoading] = useState(false);

  const {
    bind: bingFirstName,
    error: errorFirstName,
    value: firstName,
  } = useInput({
    label: t('ui.auth.field.firstname'),
    maxLength: 50,
    minLength: 3,
    required: true,
    value: '',
  });

  const {
    bind: bindLastName,
    error: errorLastName,
    value: lastName,
  } = useInput({
    label: t('ui.auth.field.lastname'),
    maxLength: 50,
    minLength: 3,
    required: true,
    value: '',
  });

  const {
    bind: bindEmail,
    error: errorEmail,
    value: email,
  } = useInput({
    label: t('ui.auth.field.email'),
    maxLength: 50,
    minLength: 3,
    required: true,
    value: '',
  });

  const {
    bind: bindPassword,
    error: errorPassword,
    value: password,
  } = useInput({
    label: t('ui.auth.field.password'),
    maxLength: 50,
    minLength: 3,
    required: true,
    value: '',
  });

  const handleSignup = useCallback(
    (event: { preventDefault: () => void }) => {
      event.preventDefault();
      if ([errorFirstName, errorLastName, errorEmail, errorPassword].some(error => error)) {
        showSnackbar(t('ui.auth.error.missing_fields'), 'error');
        return;
      }
      setLoading(true);
      signup(firstName, lastName, email, password);
      setLoading(false);
    },
    [
      errorFirstName,
      errorLastName,
      errorEmail,
      errorPassword,
      signup,
      showSnackbar,
      firstName,
      lastName,
      email,
      password,
      t,
    ]
  );

  return (
    <LayoutMain backUrl={-1} header={<Typography variant="h3">{t('ui.auth.titles.signup')}</Typography>}>
      <Stack alignItems={'center'} height={'100vh'} justifyContent={'center'} pb={12}>
        <form onSubmit={handleSignup}>
          <Stack alignItems={'center'} spacing={2} width={'400px'}>
            <Stack sx={{ height: '60px', width: '60px' }}>
              <img alt="Logo" src="/svg/unauthorized.svg" />
            </Stack>

            <TextInput autoFocus showClear {...bingFirstName} sxStack={{ width: '100%' }} />

            <TextInput showClear {...bindLastName} sxStack={{ width: '100%' }} />

            <TextInput showClear {...bindEmail} sxStack={{ width: '100%' }} />

            <TextInput showClear {...bindPassword} sxStack={{ width: '100%' }} type="password" />

            <Stack direction={'row'} justifyContent={'space-between'} spacing={2} width={'100%'}>
              <Button color="primary" component={Link} to="/signin" variant="text">
                {t('ui.auth.button.signin')}
              </Button>
              <LoadingButton loading={loading} startIcon={<LoginIcon />} type="submit" variant="contained">
                {t('ui.auth.button.signup')}
              </LoadingButton>
            </Stack>
          </Stack>
        </form>
      </Stack>
    </LayoutMain>
  );
};

export default React.memo(PageSignUp);
