// Homepage
import LoginIcon from '@mui/icons-material/Login';
import {Container, Link, Stack, Typography, Divider, Button, List, ListItem, ListItemText} from '@mui/material';
import React from 'react';
import {useTranslation} from 'react-i18next';
import {NavLink} from 'react-router-dom';

import LayoutMain from "../layout/LayoutMain";
import Logo from "../Logo";


interface AvailableDataProvidersProps {
  dataProviderNames: string[];
}


function AvailableDataProviders({dataProviderNames}: AvailableDataProvidersProps): JSX.Element | null {
  return dataProviderNames && (
    <Stack
      direction="row"
      spacing={2}
      divider={<Divider orientation="vertical" flexItem/>}
      sx={{marginBottom: '24px'}}
    >
      {dataProviderNames.map((name, index) => (
        <Stack
          key={index}
          direction="row"
          spacing={1}
        >
          <Logo name={name} size={18}/>
          <Typography variant="body1">
            {name}
          </Typography>
        </Stack>
      ))}
    </Stack>
  )
}

function DataProviderUsage({dataProviderNames}: AvailableDataProvidersProps): JSX.Element | null {
  const {t} = useTranslation();
  return dataProviderNames && (
    <Stack
      spacing={2}
      sx={{marginBottom: '24px'}}
    >
      {dataProviderNames.map((name, index) => (
        <Stack
          key={index}
          direction="row"
          spacing={1}
        >
          <Logo name={name} size={18}/>
          <Typography variant="body1">
            {name}: {t(`homepage.why_we_request_access_to_your_data.${name.toLowerCase()}`)}
          </Typography>
        </Stack>
      ))}
    </Stack>
  )
}

// The main content of the homepage
function HomePageContent(): JSX.Element {
  const {t} = useTranslation();

  const dataProviderNames: string[] = [
    "Fitbit",
    "Instagram",
    "Github",
    "GoogleContacts"
  ];

  return (
    <Container>
      <Typography variant="h4">{t('homepage.introduction.title')}</Typography>
      <Typography paragraph>{t('homepage.introduction.content')}</Typography>

      <Typography variant="h4">{t('homepage.supported_data_providers.title')}</Typography>
      <Typography paragraph>{t('homepage.supported_data_providers.content')}</Typography>
      <AvailableDataProviders dataProviderNames={dataProviderNames}/>

      <Typography variant="h4">{t('homepage.why_we_request_access_to_your_data.title')}</Typography>
      <Typography paragraph>{t('homepage.why_we_request_access_to_your_data.content')}</Typography>
      <DataProviderUsage dataProviderNames={dataProviderNames}/>
      <Typography paragraph>{t('homepage.why_we_request_access_to_your_data.content2')}</Typography>

      <Typography variant="h4">{t('homepage.how_we_use_your_data.title')}</Typography>
      <Typography paragraph sx={{marginBottom: "0px"}}>{t('homepage.how_we_use_your_data.content')}</Typography>
      {/*<Typography paragraph>{t('homepage.how_we_use_your_data.content2')}</Typography>*/}
      <Typography component="div">
        <ol style={{ paddingLeft: '20px', listStyleType: 'decimal' }}>
          {Array.from({length: 3}, (_, index) => (
            <li key={index} style={{marginBottom: '8px'}}>
              {t(`homepage.how_we_use_your_data.step${index + 1}`)}
            </li>
          ))}
        </ol>
      </Typography>


      <Typography variant="h4">{t('homepage.privacy_and_security.title')}</Typography>
      <Typography paragraph>{t('homepage.privacy_and_security.content')}</Typography>

      <Typography variant="h4">{t('homepage.more_information.title')}</Typography>
      <Typography paragraph sx={{marginBottom: '0px'}}>
        {t('homepage.more_information.content')}
      </Typography>
      <Stack
        direction="row"
        spacing={2}
        divider={<Divider orientation="vertical" flexItem/>}
        sx={{marginBottom: '16px', alignContent: 'center'}}
      >
        <Typography variant="body1" sx={{alignContent: 'center', display: 'flex'}}>
          <Logo name="github" size={18}/>&nbsp;
          <Link href={t('homepage.more_information.source_code_link')} rel="noopener">
            {t('homepage.more_information.source_code')}
          </Link>
        </Typography>
        <Typography variant="body1">
          <Link href={t('homepage.more_information.paper_link')} rel="noopener">
            {t('homepage.more_information.paper')}
          </Link>
        </Typography>
      </Stack>

      <Typography variant="h4">{t('homepage.contact_information.title')}</Typography>
      <Typography paragraph>
        {t('homepage.contact_information.content')}:&nbsp;
        <Link
          href={`mailto:${t('homepage.contact_information.email')}`}
          rel="noopener noreferrer"
          color="primary"
        >
          {t('homepage.contact_information.contact_email')}
        </Link>
      </Typography>
    </Container>
  );
}

// The main homepage layout
function Homepage(): JSX.Element {
  const {t} = useTranslation();

  return (
    <LayoutMain
      header={
        <Typography variant="h3" sx={{marginLeft: 'auto', marginRight: 'auto'}}>
          {t('homepage.title')}
        </Typography>
      }
      headerRightCorner={
        <Stack direction="row" justifyContent="space-between">
          <Button component={NavLink} startIcon={<LoginIcon/>} variant="contained" to="/projects">
            {t('homepage.researcher_login.login_button')}
          </Button>
        </Stack>
      }
    >
      <Stack spacing={2} width="80%">
        <HomePageContent/>
      </Stack>
    </LayoutMain>
  );
}

export default Homepage;
