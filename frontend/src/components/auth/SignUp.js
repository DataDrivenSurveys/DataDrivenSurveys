import {useAuth} from "../../context/AuthContext";
import {Button, Stack} from "@mui/material";
import {LoadingButton} from '@mui/lab';
import {useCallback, useState} from "react";
import {Link} from 'react-router-dom';

import LoginIcon from '@mui/icons-material/Login';
import useInput from "../../hook/useInput";
import TextInput from "../input/TextInput";
import {useSnackbar} from "../../context/SnackbarContext";
import {useTranslation} from 'react-i18next';
import LayoutMain from "../layout/LayoutMain";
import {Typography} from '@mui/material';


const SignUp = () => {

  const {t} = useTranslation();

  const {signup} = useAuth();

  const {showBottomCenter: showSnackbar} = useSnackbar();

  const [loading, setLoading] = useState(false);

  const {bind: bingFirstName, value: firstName, error: errorFirstName} = useInput({
    label: t('ui.auth.field.firstname'),
    value: '',
    minLength: 3,
    maxLength: 50,
    required: true,
  });

  const {bind: bindLastName, value: lastName, error: errorLastName} = useInput({
    label: t('ui.auth.field.lastname'),
    value: '',
    minLength: 3,
    maxLength: 50,
    required: true,
  });

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


  const handleSignup = useCallback((event) => {
    event.preventDefault();
    if ([errorFirstName, errorLastName, errorEmail, errorPassword].some((error) => error === true)) {
      showSnackbar(t('ui.auth.error.missing_fields'), 'error');
      return;
    }
    setLoading(true);
    signup(firstName, lastName, email, password);
    setLoading(false);
  }, [errorFirstName, errorLastName, errorEmail, errorPassword, signup, showSnackbar, firstName, lastName, email, password, t]);

  return (
    <LayoutMain
      backUrl={-1}
      header={
        <Typography variant="h3">{t('ui.auth.titles.signup')}</Typography>
      }
    >
      <Stack alignItems={"center"} justifyContent={"center"} height={"100vh"} pb={12}>
        <form onSubmit={handleSignup}>
          <Stack spacing={2} alignItems={"center"} width={"400px"}>
            <Stack sx={{width: '60px', height: '60px'}}>
              <img src="/svg/unauthorized.svg" alt="Logo"/>
            </Stack>

            <TextInput
              autoFocus
              showClear
              {...bingFirstName}
              sx={{width: '100%'}}
            />

            <TextInput
              showClear
              {...bindLastName}
              sx={{width: '100%'}}
            />

            <TextInput
              showClear
              {...bindEmail}
              sx={{width: '100%'}}
            />

            <TextInput
              showClear
              {...bindPassword}
              sx={{width: '100%'}}
              type="password"
            />

            <Stack spacing={2} direction={"row"} justifyContent={"space-between"} width={"100%"}>
              <Button component={Link} to="/" variant="text" color="primary">
                Sign in
              </Button>
              <LoadingButton loading={loading} startIcon={<LoginIcon/>} variant="contained" type="submit">Sign
                Up</LoadingButton>
            </Stack>
          </Stack>
        </form>
      </Stack>
    </LayoutMain>
  );
}

export default SignUp;
