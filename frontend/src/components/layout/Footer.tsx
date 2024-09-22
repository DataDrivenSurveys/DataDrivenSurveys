import { BottomNavigation, Link, Stack, Typography } from '@mui/material';
import React, { JSX } from 'react';
import { useTranslation } from 'react-i18next';

import { getFrontendBaseURL } from '../utils/getURL';

const FooterComponent = (): JSX.Element => {
  const { t } = useTranslation();
  const baseUrl: string = getFrontendBaseURL();

  return (
    <BottomNavigation>
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
        <Link href={`${baseUrl}/`} variant="body1" color="primary">
          {t('ui.footer.homepage')}
        </Link>

        <Link href={`${baseUrl}/privacy-policy`} variant="body1" color="primary">
          {t('ui.footer.privacy_policy')}
        </Link>

        <Link href={`${baseUrl}/terms-of-service`} variant="body1" color="primary">
          {t('ui.footer.terms_of_service')}
        </Link>

        <Typography variant="body1" align="center">
          {t('ui.footer.copyright')}
        </Typography>
      </Stack>
    </BottomNavigation>
  );
};

export const Footer = React.memo(FooterComponent);

export default Footer;
