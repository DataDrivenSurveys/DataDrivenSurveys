// PrivacyPolicy.js
import React from 'react';
import {useTranslation} from 'react-i18next';
import {Container, Link, Stack, Typography} from '@mui/material';

import LayoutMain from "../layout/LayoutMain";


function PrivacyPolicyContent() {
  const {t} = useTranslation();

  return (
    <Container>
      {/*<Typography variant="h1">{t('privacy_policy.title')}</Typography>*/}

      <Typography variant="h2">{t('privacy_policy.introduction.title')}</Typography>
      <Typography paragraph>{t('privacy_policy.introduction.content')}</Typography>

      <Typography variant="h2">{t('privacy_policy.data_collection_and_use.title')}</Typography>
      <Typography paragraph>
         <span style={{fontWeight: 'bold'}}>
           1. {t('privacy_policy.data_collection_and_use.information_you_provide.title')}
         </span>: {t('privacy_policy.data_collection_and_use.information_you_provide.content')}
      </Typography>
      <Typography paragraph>
         <span style={{fontWeight: 'bold'}}>
           2. {t('privacy_policy.data_collection_and_use.automatically_collected_information.title')}
         </span>: {t('privacy_policy.data_collection_and_use.automatically_collected_information.content')}
      </Typography>

      <Typography variant="h2">{t('privacy_policy.purpose_of_data_collection.title')}</Typography>
      <Typography paragraph>{t('privacy_policy.purpose_of_data_collection.content')}</Typography>

      <Typography variant="h2">{t('privacy_policy.consent.title')}</Typography>
      <Typography paragraph>{t('privacy_policy.consent.content')}</Typography>

      <Typography variant="h2">{t('privacy_policy.data_minimization.title')}</Typography>
      <Typography paragraph>{t('privacy_policy.data_minimization.content')}</Typography>

      <Typography variant="h2">{t('privacy_policy.security.title')}</Typography>
      <Typography paragraph>{t('privacy_policy.security.content')}</Typography>

      <Typography variant="h2">{t('privacy_policy.data_retention_and_deletion.title')}</Typography>
      <Typography paragraph>{t('privacy_policy.data_retention_and_deletion.content')}</Typography>

      <Typography variant="h2">{t('privacy_policy.changes_to_this_privacy_policy.title')}</Typography>
      <Typography paragraph>{t('privacy_policy.changes_to_this_privacy_policy.content')}</Typography>

      <Typography variant="h2">{t('privacy_policy.contact_information.title')}</Typography>
      <Typography paragraph>
        {t('privacy_policy.contact_information.content')}: {
        <Link href={`mailto:${t('privacy_policy.contact_information.email')}`} rel="noopener noreferrer"
              color="primary">
          {t('privacy_policy.contact_information.contact_email')}
        </Link>
      }
      </Typography>
    </Container>
  );
}

function PrivacyPolicy() {
  const {t} = useTranslation();

  return (
    <LayoutMain
      header={<Typography variant="h2">{t('privacy_policy.title')}</Typography>}
      backUrl={-1}
    >
      <Stack spacing={2} width={"80%"}>
        <PrivacyPolicyContent/>
      </Stack>

    </LayoutMain>
  )
}

export default PrivacyPolicy;
