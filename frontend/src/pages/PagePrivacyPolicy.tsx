import { Container, Link, Stack, Typography } from '@mui/material';
import React, { JSX } from 'react';
import { Trans, useTranslation } from 'react-i18next';

import LayoutMain from '../components/layout/LayoutMain';
import { InterpolateContent } from '../i18n/i18n';

interface FormatSectionProps {
  title: string;
  content: string;
  titleVariant?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'subtitle1' | 'subtitle2' | 'body1' | 'body2';
}

interface FormatSubSectionProps {
  title: string;
  content: string;
}

interface FormattedSectionsProps {
  formattedSections: Record<string, Record<string, string[]>>;
}

function FormatSection({ title, content, titleVariant = 'h4' }: FormatSectionProps): JSX.Element {
  return (
    <>
      <Typography variant={titleVariant}>{title}</Typography>
      <Typography paragraph>
        <InterpolateContent i18nKey={content} />
      </Typography>
    </>
  );
}

function FormatSubSection({ title, content }: FormatSubSectionProps): JSX.Element {
  return (
    <>
      <strong>{title}</strong>: <InterpolateContent i18nKey={content} />
    </>
  );
}

function FormattedSections({ formattedSections }: FormattedSectionsProps): JSX.Element | null {
  const { t } = useTranslation();

  return (
    formattedSections && (
      <Stack spacing={0} sx={{ 'margin-top': '0px' }}>
        {Object.keys(formattedSections).map((parentSection, indexParent) => (
          <Container maxWidth={false} disableGutters={true} key={indexParent}>
            <FormatSection title={t(`${parentSection}.title`)} content={t(`${parentSection}.content`)} />

            {Object.keys(formattedSections[parentSection]).length > 0 &&
              Object.keys(formattedSections[parentSection]).map((sectionName, indexSection) => (
                <React.Fragment key={indexSection}>
                  <Typography paragraph>
                    <FormatSubSection
                      title={`${indexSection + 1}. ` + t(`${parentSection}.${sectionName}.title`)}
                      content={t(`${parentSection}.${sectionName}.content`)}
                    />
                    {formattedSections[parentSection][sectionName].length > 0 && (
                      <>
                        <Typography paragraph sx={{ paddingLeft: '8px' }}>
                          {formattedSections[parentSection][sectionName].map((subsection, indexSubsection) => (
                            <Typography key={indexSubsection}>
                              <FormatSubSection
                                title={
                                  `${indexSection + 1}.${indexSubsection + 1}. ` +
                                  t(`${parentSection}.${sectionName}.${subsection}.title`)
                                }
                                content={t(`${parentSection}.${sectionName}.${subsection}.content`)}
                              />
                            </Typography>
                          ))}
                        </Typography>
                      </>
                    )}
                  </Typography>
                </React.Fragment>
              ))}
          </Container>
        ))}
      </Stack>
    )
  );
}

function PrivacyPolicyContent(): JSX.Element {
  const { t } = useTranslation();
  const dataCollectionAndUseSections = {
    'privacy_policy.introduction': {},
    'privacy_policy.data_collection_and_use': {
      information_you_provide: [],
      automatically_collected_information: [],
      google_user_data: ['google_account_information', 'google_contacts_information'],
    },
    'privacy_policy.how_we_use_your_data': {
      dds_user_interface: [],
      survey_personalization: [],
      automated_data_collection: [],
      google_data: ['dds_user_interface', 'survey_personalization', 'automated_data_collection'],
    },
    'privacy_policy.sharing_and_disclosure': {
      survey_platforms: [],
      legal_compliance: [],
      google_data: [],
    },
    'privacy_policy.consent': {},
    'privacy_policy.data_minimization': {},
    'privacy_policy.security': {
      oauth: [],
      automatic_access_token_revocation: [],
    },
    'privacy_policy.data_retention_and_deletion': {},
    'privacy_policy.changes_to_this_privacy_policy': {},
  };

  return (
    <>
      <FormattedSections formattedSections={dataCollectionAndUseSections} />

      <Typography variant="h4">{t('privacy_policy.contact_information.title')}</Typography>
      <Typography paragraph>
        <Trans
          i18nKey="privacy_policy.contact_information.content"
          components={{
            email: (
              <Link
                href={`mailto:${t('privacy_policy.contact_information.contact_email')}`}
                rel="noopener noreferrer"
                color="primary"
              />
            ),
          }}
          values={{ contact_email: t('privacy_policy.contact_information.contact_email') }}
        />
      </Typography>
    </>
  );
}

function PagePrivacyPolicy(): JSX.Element {
  const { t } = useTranslation();

  return (
    <LayoutMain header={<Typography variant="h3">{t('privacy_policy.title')}</Typography>} backUrl={-1}>
      <PrivacyPolicyContent />
    </LayoutMain>
  );
}

export default React.memo(PagePrivacyPolicy);
