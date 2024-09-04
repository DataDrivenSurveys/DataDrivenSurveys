// // Homepage
//
// import React from 'react';
// import {useTranslation} from 'react-i18next';
// import {Container, Link, Stack, Typography} from '@mui/material';
// import Divider from '@mui/material/Divider';
// import {Button} from "@mui/material";
// import LoginIcon from '@mui/icons-material/Login';
// import { NavLink } from 'react-router-dom';
//
//
// import LayoutMain from "../layout/LayoutMain";
//
//
// function HomePageContent() {
//   const {t} = useTranslation();
//
//   return (
//     <Container>
//       {/*<Typography variant="h1">{t('privacy_policy.title')}</Typography>*/}
//
//       <Typography variant="h4">{t('homepage.introduction.title')}</Typography>
//       <Typography paragraph>{t('homepage.introduction.content')}</Typography>
//
//       <Typography variant="h4">{t('homepage.when_using_dds.title')}</Typography>
//       <Typography paragraph>{t('homepage.when_using_dds.content')}</Typography>
//
//       <Typography variant="h4">{t('homepage.more_information.title')}</Typography>
//       <Typography paragraph sx={{"margin-bottom": "0px"}}>{t('homepage.more_information.content')}</Typography>
//       <Stack
//         direction="row"
//         spacing={2}
//         divider={<Divider orientation="vertical" flexItem/>}
//         sx={{"margin-bottom": "16px"}}
//       >
//         <Typography variant="body1">
//           <Link href={"/privacy-policy"} rel="noopener">
//             {t('homepage.more_information.privacy_policy')}
//           </Link>
//         </Typography>
//         <Typography variant="body1">
//           <Link href={"/privacy-policy"} rel="noopener">
//             {t('homepage.more_information.terms_of_service')}
//           </Link>
//         </Typography>
//       </Stack>
//
//       <Typography variant="h4">{t('homepage.contact_information.title')}</Typography>
//       <Typography paragraph>
//         {t('homepage.contact_information.content')}: {
//         <Link href={`mailto:${t('homepage.contact_information.email')}`} rel="noopener noreferrer"
//               color="primary">
//           {t('homepage.contact_information.contact_email')}
//         </Link>
//       }
//       </Typography>
//     </Container>
//   );
// }
//
// function Homepage() {
//   const {t} = useTranslation();
//
//   return (
//     <LayoutMain
//       // backUrl={-1}
//       header={<Typography variant="h3" sx={{
//         "margin-left": "auto",
//         "margin-right": "auto"
//       }}>{t('homepage.title')}</Typography>}
//       headerRightCorner={
//         <Stack direction={"row"} justifyContent={"space-between"} >
//           <Button component={NavLink} startIcon={<LoginIcon/>} variant="contained" to="/projects">
//             {t('homepage.researcher_login.login_button')}
//           </Button>
//         </Stack>
//       }
//     >
//       <Stack spacing={2} width={"80%"}>
//         <HomePageContent/>
//       </Stack>
//
//     </LayoutMain>
//   )
// }
//
// export default Homepage;
import LoginIcon from '@mui/icons-material/Login';
import { Container, Link, Stack, Typography, Divider, Button } from '@mui/material';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { NavLink } from 'react-router-dom';

import LayoutMain from "../layout/LayoutMain";

// The main content of the homepage
function HomePageContent(): JSX.Element {
  const { t } = useTranslation();

  return (
    <Container>
      {/*<Typography variant="h1">{t('privacy_policy.title')}</Typography>*/}

      <Typography variant="h4">{t('homepage.introduction.title')}</Typography>
      <Typography paragraph>{t('homepage.introduction.content')}</Typography>

      <Typography variant="h4">{t('homepage.when_using_dds.title')}</Typography>
      <Typography paragraph>{t('homepage.when_using_dds.content')}</Typography>

      <Typography variant="h4">{t('homepage.more_information.title')}</Typography>
      <Typography paragraph sx={{ marginBottom: '0px' }}>
        {t('homepage.more_information.content')}
      </Typography>
      <Stack
        direction="row"
        spacing={2}
        divider={<Divider orientation="vertical" flexItem />}
        sx={{ marginBottom: '16px' }}
      >
        <Typography variant="body1">
          <Link href="/privacy-policy" rel="noopener">
            {t('homepage.more_information.privacy_policy')}
          </Link>
        </Typography>
        <Typography variant="body1">
          <Link href="/privacy-policy" rel="noopener">
            {t('homepage.more_information.terms_of_service')}
          </Link>
        </Typography>
      </Stack>

      <Typography variant="h4">{t('homepage.contact_information.title')}</Typography>
      <Typography paragraph>
        {t('homepage.contact_information.content')}:
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
  const { t } = useTranslation();

  return (
    <LayoutMain
      header={
        <Typography variant="h3" sx={{ marginLeft: 'auto', marginRight: 'auto' }}>
          {t('homepage.title')}
        </Typography>
      }
      headerRightCorner={
        <Stack direction="row" justifyContent="space-between">
          <Button component={NavLink} startIcon={<LoginIcon />} variant="contained" to="/projects">
            {t('homepage.researcher_login.login_button')}
          </Button>
        </Stack>
      }
    >
      <Stack spacing={2} width="80%">
        <HomePageContent />
      </Stack>
    </LayoutMain>
  );
}

export default Homepage;
