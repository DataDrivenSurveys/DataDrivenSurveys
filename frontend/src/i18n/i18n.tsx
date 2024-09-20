import i18n from 'i18next';
import Backend from 'i18next-http-backend'; // You may need this for loading translation files
import React, { JSX } from 'react';
import { initReactI18next, Trans } from 'react-i18next';

import resources from './resources.json';

// Initialize i18next with react-i18next
i18n
  .use(Backend)
  .use(initReactI18next) // passes i18n down to react-i18next
  .init({
    resources,
    lng: 'en', // detected language to use
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // react already safe from xss
    },
    react: {
      useSuspense: false, // Disable suspense for SSR
    },
  });

// Define the types for the I18Link component props
interface I18LinkProps {
  i18nKey: string;
  url: string;
  link_text?: string | null;
}

export const I18Link = ({ i18nKey, url, link_text = null }: I18LinkProps): JSX.Element => {
  // If no link_text is provided, use the URL as the link text
  if (!link_text) {
    link_text = url;
  }

  return (
    <Trans
      i18nKey={i18nKey}
      values={{ url, link_text }}
      components={[
        <a href={url} target="_blank" rel="noreferrer">
          {link_text}
        </a>,
      ]}
    />
  );
};

interface InterpolateContentProps {
  i18nKey: string;
  values?: Record<string, string>;
}

export function InterpolateContent({ i18nKey, values }: InterpolateContentProps): JSX.Element {
  return (
    <Trans
      i18nKey={i18nKey}
      components={{
        strong: <strong />,
        br: <br />,
      }}
      values={values}
    />
  );
}

export default i18n;
