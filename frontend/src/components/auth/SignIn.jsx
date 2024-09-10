import LoginIcon from '@mui/icons-material/Login';
import {LoadingButton} from '@mui/lab';
import {Button, Stack} from "@mui/material";
import {Typography} from '@mui/material';
import React from 'react';
import {useCallback, useState} from "react";
import {useTranslation} from 'react-i18next';
import {Link} from 'react-router-dom';

import {useAuth} from "../../context/AuthContext";
import {useSnackbar} from "../../context/SnackbarContext";
import useInput from "../../hook/useInput";
import TextInput from "../input/TextInput";
import Footer from "../layout/Footer";
import LayoutMain from "../layout/LayoutMain";



const SignIn = () => {

  const {t} = useTranslation();

  const {signin} = useAuth();

  const {showBottomCenter: showSnackbar} = useSnackbar();

  const [loading, setLoading] = useState(false);

  const {bind: bindEmail, value: email, error: errorEmail} = useInput({
    label: t('ui.auth.field.email'),
    value: '',
    minLength: 3,
    maxLength: 50,
    required: true,
  });

  const {bind: bindPassword, value: password, error: errorPassword} = useInput({
    label: t('ui.auth.field.password'),
    value: '',
    minLength: 3,
    maxLength: 50,
    required: true,
  });

  const handleSignIn = useCallback(async (event) => {

    event.preventDefault();
    if ([errorEmail, errorPassword].some((error) => error === true)) {
      showSnackbar(t('ui.auth.error.missing_fields'), 'error');
      return;
    }
    setLoading(true);
    await signin(email, password);
    setLoading(false);
  }, [errorEmail, errorPassword, signin, showSnackbar, email, password, t]);

  return (
    <LayoutMain
    backUrl={-1}
    header={<Typography variant="h3">{t('ui.auth.titles.signin')}</Typography>}
    >
      <Stack height={'100vh'} width={'100vw'}>
        <Stack alignItems={"center"} justifyContent={"center"} height={"100vh"} pb={12}>
          <form onSubmit={handleSignIn}>
            <Stack spacing={2} alignItems={"center"} width={"400px"}>
              <Stack sx={{width: '60px', height: '60px'}}>
                <img src="/svg/unauthorized.svg" alt="Logo"/>
              </Stack>

              <TextInput
                autoFocus
                showClear
                {...bindEmail}
                sx={{width: '100%'}}
              />
              <TextInput
                showClear
                {...bindPassword}
                type={"password"}
                sx={{width: '100%'}}
              />

              <Stack direction={"row"} justifyContent={"space-between"} width={"100%"}>
                <Button component={Link} to="/signup" variant="text" color="primary">
                  {t('ui.auth.button.signup')}
                </Button>
                <LoadingButton loading={loading} startIcon={<LoginIcon/>} variant="contained" type="submit">
                  {t('ui.auth.button.signin')}
                </LoadingButton>
              </Stack>
            </Stack>
          </form>
        </Stack>
        <Footer/>
      </Stack>
    </LayoutMain>
  );
}

export default SignIn;
