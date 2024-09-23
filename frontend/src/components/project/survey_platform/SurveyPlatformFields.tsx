import React, { useCallback, useEffect, useState, JSX } from 'react';
import { useLocation } from 'react-router-dom';

import { API } from '../../../types';
import FormFields, { Field } from '../../input/FormFields';

interface SurveyPlatformFieldsProps {
  selectedSurveyPlatform: API.SurveyPlatforms.SurveyPlatform;
  surveyPlatformFields: Field[];
  hiddenFields?: string[];
  onChange: (fields: Field[]) => void;
}

const SurveyPlatformFields = ({
  selectedSurveyPlatform,
  surveyPlatformFields: initial,
  hiddenFields = [],
  onChange,
}: SurveyPlatformFieldsProps): JSX.Element => {
  const location = useLocation();

  // Use URLSearchParams to parse the query string
  const searchParams = new URLSearchParams(location.search);
  const access_token = searchParams.get('access_token');

  const [surveyPlatformFields, setSurveyPlatformFields] = useState<Field[]>(initial);

  useEffect(() => {
    setSurveyPlatformFields(initial || []);
    localStorage.setItem('surveyPlatformFields', JSON.stringify(initial || []));
  }, [initial]);

  useEffect(() => {
    if (access_token) {
      // set the access_token value
      const newSurveyPlatformFields = surveyPlatformFields.map(field => {
        if (field.name === 'access_token') {
          field.value = access_token;
        }
        return field;
      });

      // save the updated fields to the local storage
      localStorage.setItem('surveyPlatformFields', JSON.stringify(newSurveyPlatformFields));

      setSurveyPlatformFields(newSurveyPlatformFields);
      onChange(newSurveyPlatformFields);
    }
  }, [access_token, onChange, setSurveyPlatformFields, surveyPlatformFields]);

  localStorage.setItem('preAuthLocation', JSON.stringify(location));

  const openAuthorizeUrl = useCallback((authorize_url: string, _: string) => {
    // redirect to the authorization url
    const url = new URL(authorize_url);
    window.location.assign(url.toString());
  }, []);

  const oauth2Reducer = useCallback(
    (action: string, _: Record<string, string>) => {
      switch (action) {
        case 'open_authorize_url':
          // save the fields to the local storage
          localStorage.setItem('surveyPlatformFields', JSON.stringify(surveyPlatformFields));
          return openAuthorizeUrl(selectedSurveyPlatform.oauth2?.authorize_url as string, '');
        case 'clear':
          return undefined;
        default:
          throw new Error();
      }
    },
    [surveyPlatformFields, selectedSurveyPlatform, openAuthorizeUrl]
  );

  const shouldHideField = useCallback((fieldName: string) => hiddenFields.includes(fieldName), [hiddenFields]);

  return (
    <FormFields
      buttonActionReducer={oauth2Reducer}
      fields={surveyPlatformFields.filter(f => !shouldHideField(f.name))}
      onChange={(fields: Field[]) => {
        setSurveyPlatformFields(fields);
        onChange(fields);
      }}
    />
  );
};

export default SurveyPlatformFields;
