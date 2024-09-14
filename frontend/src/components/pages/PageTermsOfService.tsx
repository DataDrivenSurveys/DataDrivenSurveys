import {Link, Typography} from '@mui/material';
import React from 'react';
import {useTranslation} from 'react-i18next';

import LayoutMain from "../layout/LayoutMain";

function TermsOfServiceContent() {
  const {t} = useTranslation();

  return (
    <>
      <Typography variant="h4">{t('terms_of_service.introduction.title')}</Typography>
      <Typography paragraph>{t('terms_of_service.introduction.content')}</Typography>

      <Typography variant="h4">{t('terms_of_service.definitions.title')}</Typography>
      <Typography paragraph>
         <span style={{fontWeight: 'bold'}}>
           1. {t('terms_of_service.definitions.dds.title')}
         </span>: {t('terms_of_service.definitions.dds.content')}
      </Typography>
      <Typography paragraph>
         <span style={{fontWeight: 'bold'}}>
           2. {t('terms_of_service.definitions.dp.title')}
         </span>: {t('terms_of_service.definitions.dp.content')}
      </Typography>
      <Typography paragraph>
         <span style={{fontWeight: 'bold'}}>
           3. {t('terms_of_service.definitions.users.title')}
         </span>: {t('terms_of_service.definitions.users.content')}
      </Typography>
      <Typography paragraph>
         <span style={{fontWeight: 'bold'}}>
           4. {t('terms_of_service.definitions.content.title')}
         </span>: {t('terms_of_service.definitions.content.content')}
      </Typography>


      <Typography variant="h4">{t('terms_of_service.user_accounts.title')}</Typography>
      <Typography paragraph>{t('terms_of_service.user_accounts.content1')}</Typography>
      <Typography paragraph>{t('terms_of_service.user_accounts.content2')}</Typography>

      <Typography variant="h4">{t('terms_of_service.use_of_the_service.title')}</Typography>
      <Typography paragraph>{t('terms_of_service.use_of_the_service.content')}</Typography>

      <Typography variant="h4">{t('terms_of_service.data_integration.title')}</Typography>
      <Typography paragraph>{t('terms_of_service.data_integration.content1')}</Typography>
      <Typography paragraph>{t('terms_of_service.data_integration.content2')}</Typography>

      <Typography variant="h4">{t('terms_of_service.intellectual_property.title')}</Typography>
      <Typography paragraph>{t('terms_of_service.intellectual_property.content')}</Typography>

      <Typography variant="h4">{t('terms_of_service.privacy.title')}</Typography>
      <Typography paragraph>{t('terms_of_service.privacy.content')}</Typography>

      <Typography variant="h4">{t('terms_of_service.termination.title')}</Typography>
      <Typography paragraph>{t('terms_of_service.termination.content')}</Typography>

      <Typography variant="h4">{t('terms_of_service.disclaimers.title')}</Typography>
      <Typography paragraph>{t('terms_of_service.disclaimers.content1')}</Typography>
      <Typography paragraph>{t('terms_of_service.disclaimers.content2')}</Typography>

      <Typography variant="h4">{t('terms_of_service.limitation_of_liability.title')}</Typography>
      <Typography paragraph>{t('terms_of_service.limitation_of_liability.content')}</Typography>

      <Typography variant="h4">{t('terms_of_service.general_representation_and_warranty.title')}</Typography>
      <Typography paragraph>{t('terms_of_service.general_representation_and_warranty.content')}</Typography>

      <Typography variant="h4">{t('terms_of_service.limitation_of_liability.title')}</Typography>
      <Typography paragraph>{t('terms_of_service.limitation_of_liability.content')}</Typography>

      <Typography variant="h4">{t('terms_of_service.changes.title')}</Typography>
      <Typography paragraph>{t('terms_of_service.changes.content')}</Typography>

      <Typography variant="h4">{t('terms_of_service.contact_information.title')}</Typography>
      <Typography paragraph>
        {t('terms_of_service.contact_information.content')}: {
        <Link href={`mailto:${t('terms_of_service.contact_information.email')}`} rel="noopener noreferrer"
              color="primary">
          {t('terms_of_service.contact_information.contact_email')}
        </Link>
      }
      </Typography>
    </>
  );
}

function PageTermsOfService() {
  const {t} = useTranslation();

  return (
    <LayoutMain
      header={<Typography variant="h3">{t('terms_of_service.title')}</Typography>}
      backUrl={-1}
    >
      <TermsOfServiceContent/>
    </LayoutMain>
  )
}

export default React.memo(PageTermsOfService);
