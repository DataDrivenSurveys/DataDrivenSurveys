import LoginIcon from '@mui/icons-material/Login';
import { LoadingButton } from '@mui/lab';
import { Button, Stack, Typography } from '@mui/material';
import React, { JSX, useCallback, useState } from 'react';
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
    value: firstName,
    error: errorFirstName,
  } = useInput({
    label: t('ui.auth.field.firstname'),
    value: '',
    minLength: 3,
    maxLength: 50,
    required: true,
  });

  const {
    bind: bindLastName,
    value: lastName,
    error: errorLastName,
  } = useInput({
    label: t('ui.auth.field.lastname'),
    value: '',
    minLength: 3,
    maxLength: 50,
    required: true,
  });

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

  const handleSignup = useCallback(
    (event: { preventDefault: () => void }) => {
      event.preventDefault();
      if ([errorFirstName, errorLastName, errorEmail, errorPassword].some(error => error === true)) {
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
      <Stack alignItems={'center'} justifyContent={'center'} height={'100vh'} pb={12}>
        <form onSubmit={handleSignup}>
          <Stack spacing={2} alignItems={'center'} width={'400px'}>
            <Stack sx={{ width: '60px', height: '60px' }}>
              <img src="/svg/unauthorized.svg" alt="Logo" />
            </Stack>

            <TextInput autoFocus showClear {...bingFirstName} sxStack={{ width: '100%' }} />

            <TextInput showClear {...bindLastName} sxStack={{ width: '100%' }} />

            <TextInput showClear {...bindEmail} sxStack={{ width: '100%' }} />

            <TextInput showClear {...bindPassword} sxStack={{ width: '100%' }} type="password" />

            <Stack spacing={2} direction={'row'} justifyContent={'space-between'} width={'100%'}>
              <Button component={Link} to="/signin" variant="text" color="primary">
                {t('ui.auth.button.signin')}
              </Button>
              <LoadingButton loading={loading} startIcon={<LoginIcon />} variant="contained" type="submit">
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
