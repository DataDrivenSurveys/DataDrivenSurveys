import { Alert, Button, Stack, Typography } from '@mui/material';
import React, { JSX, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate, useParams } from 'react-router-dom';

import { PUBLIC_POST } from '../code/http_requests';
import { useSnackbar } from '../context/SnackbarContext';
import { InterpolateContent } from '../i18n/i18n';
import { API, Models } from '../types';

type URLParams = Record<string, string>;

interface Status {
  failed: boolean;
  id: string;
  text: string;
  data_provider_name: string;
}

interface Scopes {
  required: string[];
  accepted: string[];
}

const ScopesComponent = ({ required, accepted }: Scopes): JSX.Element => {
  const { t } = useTranslation();

  const missingScopes = required.filter(scope => !accepted.includes(scope));

  return (
    <>
      {required.length > 0 && (
        <>
          <Typography variant="h6">
            {t('api.data_provider.exchange_code_error.required_scopes_details.required_scopes_header')}
          </Typography>
          {required.map(scope => (
            <Typography key={scope} variant="body1" sx={{ paddingLeft: 1 }}>
              {'-'} {scope}
            </Typography>
          ))}
        </>
      )}

      {accepted.length > 0 && (
        <>
          <Typography variant="h6">
            {t('api.data_provider.exchange_code_error.required_scopes_details.accepted_scopes_header')}
          </Typography>
          {accepted.map(scope => (
            <Typography key={scope} variant="body1" sx={{ paddingLeft: 1 }}>
              {'-'} {scope}
            </Typography>
          ))}
        </>
      )}

      {missingScopes.length > 0 && (
        <>
          <Typography variant="h6">
            {t('api.data_provider.exchange_code_error.required_scopes_details.missing_scopes_header')}
          </Typography>
          {missingScopes.map(scope => (
            <Typography key={scope} variant="body1" sx={{ paddingLeft: 1 }}>
              {'-'} {scope}
            </Typography>
          ))}
        </>
      )}
    </>
  );
};

/**
 * Landing page to receive the oauth2 code grant from the data provider
 * This page will be redirected to by the data provider after the participant has logged in and authorized the application
 * This page will then send the code grant to the backend to be exchanged for an access token
 * The access tokens are stored in local storage as an array of objects
 */
const PageParticipantOauth2Redirect = (): JSX.Element => {
  const { t } = useTranslation();

  const { provider: data_provider_name } = useParams<string>();

  const [status, setStatus] = useState<Status>({
    failed: false,
    id: 'ui.respondent.code_exchange.redirecting',
    text: '',
    data_provider_name: data_provider_name as string,
  });
  const [scopes, setScopes] = useState<Scopes>({ accepted: [], required: [] } as Scopes);

  const { showBottomCenter: showSnackbar } = useSnackbar();

  const location = useLocation();
  const navigate = useNavigate();

  const projectId = localStorage.getItem('RespondentTempProjectId');

  const exchangeCode = useCallback(async (): Promise<void> => {
    // Extract the code grant from the url
    const urlSearchParams = new URLSearchParams(location.search);
    const postFullParams: URLParams = {};
    urlSearchParams.forEach((value, key) => {
      postFullParams[key] = value;
    });

    // Send the code grant to the backend
    const response = await PUBLIC_POST(`/projects/${projectId}/respondent/exchange-code`, {
      // code: code,
      data_provider_name: data_provider_name,
      url_params: postFullParams,
    });

    response.on('2xx', async (status: number, data: API.Respondent.ResponseExchangeCodeSuccess) => {
      if (status === 200) {
        // Check if the data provider was already used
        showSnackbar(t(data.message.id, { data_provider_name: data.data_provider_name }), 'success');
        // Save the access token in local storage as array
        let tokens: Models.Dist.RespondentTempTokens[] = JSON.parse(
          localStorage.getItem('RespondentTempTokens') || '[]'
        );

        tokens = tokens.filter(token => token.data_provider_name !== data_provider_name);

        tokens.push({
          data_provider_name: data_provider_name as string,
          ...data.tokens,
        });

        localStorage.setItem('RespondentTempTokens', JSON.stringify(tokens));

        // Redirect to the project page
        navigate(`/dist/${projectId}`);
      }
    });

    response.on('4xx', (_: number, data: API.Respondent.ResponseExchangeCodeFailure) => {
      setStatus({
        failed: true,
        id: data.message.id,
        text: data.message.text,
        data_provider_name: data.message.data_provider_name,
      });
      setScopes({
        accepted: data.message.accepted_scopes,
        required: data.message.required_scopes,
      });
    });

    response.on('5xx', (_: number, data: API.Respondent.ResponseExchangeCodeFailure) => {
      setStatus({
        failed: true,
        id: data.message.id,
        text: data.message.text,
        data_provider_name: data.message.data_provider_name,
      });
    });
  }, [data_provider_name, location.search, navigate, projectId, showSnackbar, t]);

  useEffect(() => {
    setStatus({
      failed: false,
      id: 'ui.respondent.code_exchange.redirecting',
      text: '',
      data_provider_name: data_provider_name as string,
    });

    exchangeCode();
  }, [data_provider_name, exchangeCode]);

  return (
    <Stack sx={{ width: '100%', height: '100vh', justifyContent: 'center', alignItems: 'center' }}>
      <Stack spacing={1}>
        <Alert severity={status.failed ? 'error' : 'info'} sx={{ width: '100%' }}>
          <InterpolateContent
            i18nKey={status.id}
            values={{ data_provider_name: status.data_provider_name as string }}
          />
          {status.id === 'api.data_provider.exchange_code_error.unexpected_error' && (
            <Typography variant="body1">{status.text}</Typography>
          )}
          {status.failed && <ScopesComponent required={scopes.required} accepted={scopes.accepted} />}
        </Alert>
        {status.failed && (
          <Button onClick={() => navigate(`/dist/${projectId}`)}>{t('ui.respondent.connection.button.go_back')}</Button>
        )}
      </Stack>
    </Stack>
  );
};

export default PageParticipantOauth2Redirect;
