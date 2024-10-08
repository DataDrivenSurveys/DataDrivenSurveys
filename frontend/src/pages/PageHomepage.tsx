// PageHomepage
import ArticleIcon from '@mui/icons-material/Article';
import LoginIcon from '@mui/icons-material/Login';
import { Button, Divider, Link, Stack, Typography } from '@mui/material';
import React, { JSX } from 'react';
import { useTranslation } from 'react-i18next';
import { NavLink } from 'react-router-dom';

import LayoutMain from '../components/layout/LayoutMain';
import Logo from '../components/Logo';
import { getFrontendBaseURL } from '../components/utils/getURL';

interface AvailableDataProvidersProps {
  dataProviderNames: string[];
}

function AvailableDataProviders({ dataProviderNames }: AvailableDataProvidersProps): JSX.Element | null {
  return (
    dataProviderNames && (
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={{ xs: 1, sm: 2, md: 4 }}
        divider={<Divider orientation="vertical" flexItem />}
        sx={{ marginBottom: '24px' }}
      >
        {dataProviderNames.map((name, index) => (
          <Stack key={index} direction="row" spacing={1} sx={{ alignItems: 'center' }}>
            <Logo name={name} size={18} />
            <Typography variant="body1">{name}</Typography>
          </Stack>
        ))}
      </Stack>
    )
  );
}

function DataProviderUsage({ dataProviderNames }: AvailableDataProvidersProps): JSX.Element | null {
  const { t } = useTranslation();
  return (
    dataProviderNames && (
      <Stack spacing={2} sx={{ marginBottom: '24px' }}>
        {dataProviderNames.map((name, index) => (
          <Stack key={index} direction="row" spacing={1}>
            <Logo name={name} size={18} />
            &nbsp;
            <Typography variant="body1">
              {name}: {t(`homepage.why_we_request_access_to_your_data.${name.toLowerCase()}`)}
            </Typography>
          </Stack>
        ))}
      </Stack>
    )
  );
}

// The main content of the homepage
function HomePageContent(): JSX.Element {
  const { t } = useTranslation();

  const baseUrl = getFrontendBaseURL();

  const dataProviderNames: string[] = ['Fitbit', 'Instagram', 'Github', 'GoogleContacts'];

  return (
    <>
      <Typography variant="h4">{t('homepage.introduction.title')}</Typography>
      <Typography paragraph>{t('homepage.introduction.content')}</Typography>

      <Typography variant="h4">{t('homepage.supported_data_providers.title')}</Typography>
      <Typography paragraph>{t('homepage.supported_data_providers.content')}</Typography>
      <AvailableDataProviders dataProviderNames={dataProviderNames} />

      <Typography variant="h4">{t('homepage.why_we_request_access_to_your_data.title')}</Typography>
      <Typography paragraph>{t('homepage.why_we_request_access_to_your_data.content')}</Typography>
      <DataProviderUsage dataProviderNames={dataProviderNames} />
      <Typography paragraph>{t('homepage.why_we_request_access_to_your_data.content2')}</Typography>

      <Typography variant="h4">{t('homepage.how_we_use_your_data.title')}</Typography>
      <Typography paragraph sx={{ marginBottom: '0px' }}>
        {t('homepage.how_we_use_your_data.content')}
      </Typography>
      <Typography component="div">
        <ol style={{ paddingLeft: '20px', listStyleType: 'decimal' }}>
          {Array.from({ length: 3 }, (_, index) => (
            <li key={index} style={{ marginBottom: '8px' }}>
              {t(`homepage.how_we_use_your_data.step${index + 1}`)}
            </li>
          ))}
        </ol>
      </Typography>

      <Typography variant="h4">{t('homepage.privacy_and_security.title')}</Typography>
      <Typography paragraph>{t('homepage.privacy_and_security.content')}</Typography>

      <Typography variant="h4">{t('homepage.more_information.title')}</Typography>
      <Typography paragraph sx={{ marginBottom: '0px' }}>
        {t('homepage.more_information.content')}
      </Typography>
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={{ xs: 1, sm: 2, md: 4 }}
        divider={<Divider orientation="vertical" flexItem />}
        sx={{ marginBottom: '16px', alignContent: 'center' }}
      >
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
          <Logo name="dds" size={18} />
          <Typography variant="body1" sx={{ alignContent: 'center', display: 'flex' }}>
            <Link href={`${baseUrl}/privacy-policy`} rel="noopener">
              {t('homepage.more_information.privacy_policy')}
            </Link>
          </Typography>
        </Stack>

        <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
          <Logo name="github" size={18} />
          <Typography variant="body1" sx={{ alignContent: 'center', display: 'flex' }}>
            <Link href={t('homepage.more_information.source_code_link')} rel="noopener">
              {t('homepage.more_information.source_code')}
            </Link>
          </Typography>
        </Stack>

        <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
          <ArticleIcon />
          <Typography variant="body1">
            <Link href={t('homepage.more_information.paper_link')} rel="noopener">
              {t('homepage.more_information.paper')}
            </Link>
          </Typography>
        </Stack>
      </Stack>

      <Typography variant="h4">{t('homepage.contact_information.title')}</Typography>
      <Typography paragraph>
        {t('homepage.contact_information.content')}:&nbsp;
        <Link href={`mailto:${t('homepage.contact_information.email')}`} rel="noopener noreferrer" color="primary">
          {t('homepage.contact_information.contact_email')}
        </Link>
      </Typography>
    </>
  );
}

// The main homepage layout
function PageHomepage(): JSX.Element {
  const { t } = useTranslation();

  return (
    <LayoutMain
      header={
        <Stack direction="row" spacing={1} sx={{ marginLeft: 'auto', marginRight: 'auto', alignItems: 'center' }}>
          <Logo name="dds" size={30} />
          <Typography variant="h3">{t('homepage.title')}</Typography>
        </Stack>
      }
      headerRightCorner={
        <>
          <Button
            component={NavLink}
            startIcon={<LoginIcon />}
            variant="contained"
            to="/signin"
            sx={{
              display: 'inline-flex',
              '@media (max-width: 550px)': {
                display: 'none', // Hide text version below 550 px
              },
            }}
          >
            {t('homepage.researcher_login.login_button')}
          </Button>
          <Button
            component={NavLink}
            startIcon={<LoginIcon />}
            variant="contained"
            to="/signin"
            sx={{
              display: 'none',
              '@media (max-width: 550px)': {
                display: 'inline-flex', // Show icon-only version below 550 px
              },
            }} // Show only icon on small screens
          />
        </>
      }
    >
      <HomePageContent />
    </LayoutMain>
  );
}

export default React.memo(PageHomepage);
