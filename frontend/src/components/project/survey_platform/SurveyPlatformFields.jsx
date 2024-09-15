import { useCallback, useEffect, useState } from "react";
import React from 'react';
import { useLocation } from "react-router-dom";

import FormFields from "../../input/FormFields";


const SurveyPlatformFields = ({ selectedSurveyPlatform, surveyPlatformFields:initial, hiddenFields = [], onChange }) => {
  const location = useLocation();

  // Use URLSearchParams to parse the query string
  const searchParams = new URLSearchParams(location.search);
  const access_token = searchParams.get('access_token');

  const [surveyPlatformFields, setSurveyPlatformFields] = useState(initial);

  useEffect(() => {
      setSurveyPlatformFields(initial || []);
      localStorage.setItem('surveyPlatformFields', JSON.stringify(initial || []));
  }, [initial]);

  useEffect(() => {
    if(access_token){
      // set the access_token value
      const newSurveyPlatformFields = surveyPlatformFields.map((field) => {
        if(field.name === "access_token"){
          field.value = access_token;
        }
        return field;
      });

      // save the updated fields to the local storage
      localStorage.setItem('surveyPlatformFields', JSON.stringify(newSurveyPlatformFields));

      setSurveyPlatformFields(newSurveyPlatformFields);
      onChange(newSurveyPlatformFields);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [access_token, onChange]);

  localStorage.setItem('preAuthLocation', JSON.stringify(location));


  const open_authorize_url = useCallback((authorize_url, auth_url) => {
    const url = new URL(authorize_url);    // redirect to the authorization url
    window.location.assign(url.toString());
  }, []);

  const oauth2Reducer = useCallback((action, args) => {
      switch (action) {
        case 'open_authorize_url':
          // save the fields to the local storage
          localStorage.setItem('surveyPlatformFields', JSON.stringify(surveyPlatformFields));
          return open_authorize_url(selectedSurveyPlatform.oauth2.authorize_url);
        case 'clear':
          return undefined;
        default:
          throw new Error();
      }
  }, [surveyPlatformFields, selectedSurveyPlatform, open_authorize_url]);

    const shouldHideField = useCallback(
        (fieldName) => hiddenFields.includes(fieldName),
        [hiddenFields]
    );

    return (
        <FormFields
            buttonActionReducer={oauth2Reducer}
            fields={surveyPlatformFields.filter(f => !shouldHideField(f.name))}
            onChange={(fields) => {
                setSurveyPlatformFields(fields);
                onChange(fields);
            }}
        />
    );
}

export default SurveyPlatformFields;
