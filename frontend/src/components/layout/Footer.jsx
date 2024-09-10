import {Typography, Link, Stack, AppBar} from '@mui/material';
import React from 'react';
import {useTranslation} from 'react-i18next';

function Footer() {
  const {t} = useTranslation();

  return (
    <AppBar position="static" color="transparent">
      <Stack
        direction="row"
        justifyContent="center"
        alignItems="center"
        spacing={4}
        pl={1}
        pr={1}
        height="100%"
        padding={2}
      >
        <Link href="/" variant="body1" color="primary">{t('ui.footer.homepage')}</Link>

        <Link href="/privacy-policy" variant="body1" color="primary">{t('ui.footer.privacy_policy')}</Link>

        <Link href="/terms-of-service" variant="body1" color="primary">{t('ui.footer.terms_of_service')}</Link>

        <Typography variant="body1" align="center">
          {t('ui.footer.copyright')}
        </Typography>
      </Stack>
    </AppBar>
  );
}

export default Footer;
