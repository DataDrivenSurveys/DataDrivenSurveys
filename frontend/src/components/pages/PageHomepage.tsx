// Homepage
import LoginIcon from '@mui/icons-material/Login';
import {Container, Link, Stack, Typography, Divider, Button} from '@mui/material';
import React from 'react';
import {useTranslation} from 'react-i18next';
import {NavLink} from 'react-router-dom';

import LayoutMain from "../layout/LayoutMain";
import Logo from "../Logo";


interface AvailableDataProvidersProps {
  dataProviderNames: string[];
}


function AvailableDataProviders({ dataProviderNames }: AvailableDataProvidersProps): JSX.Element | null {
  return dataProviderNames && (
    <Stack
      direction="row"
      spacing={2}
      divider={<Divider orientation="vertical" flexItem/>}
      sx={{marginBottom: '24px'}}
    >
      {dataProviderNames.map((name, index) => (
        <Stack
          direction="row"
          spacing={1}
        >
          <Logo name={name} size={18}/>
          <Typography key={index} variant="body1">
            {name}
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

      <Typography variant="h4">{t('homepage.when_using_dds.title')}</Typography>
      <Typography paragraph>{t('homepage.when_using_dds.content')}</Typography>

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
