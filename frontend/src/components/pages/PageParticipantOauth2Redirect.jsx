import {Alert, Button, Stack} from "@mui/material";
import {useEffect, useState} from "react";
import React from 'react';
import {useTranslation} from 'react-i18next';
import {useLocation, useNavigate, useParams} from "react-router-dom";

import {PUBLIC_POST} from "../../code/http_requests";
import {useSnackbar} from "../../context/SnackbarContext";
import LoadingAnimation from "../feedback/LoadingAnimation"


/**
 * Landing page to receive the oauth2 code grant from the data provider
 * This page will be redirected to by the data provider after the participant has logged in and authorized the application
 * This page will then send the code grant to the backend to be exchanged for an access token
 * The access tokens are stored in local storage as an array of objects
*/
const PageParticipantOauth2Redirect = () => {

  const {t} = useTranslation();

  const {provider: data_provider_name} = useParams();

  const [status, setStatus] = useState({
    failed: false,
    message: t('ui.respondent.code_exchange.redirecting')
  });

  const {showBottomCenter: showSnackbar} = useSnackbar();

  const location = useLocation();
  const navigate = useNavigate();

  const projectId = localStorage.getItem('RespondentTempProjectId');

  useEffect(() => {
    setStatus({
      failed: false,
      message: t('ui.respondent.code_exchange.redirecting')
    });

    // Extract the code grant from the url
    const urlSearchParams = new URLSearchParams(location.search);
    // const code = urlSearchParams.get("code");
    const postFullParams = {};
    urlSearchParams.forEach((value, key) => {
      postFullParams[key] = value;
    });

    (async () => {
      // Send the code grant to the backend
      const response = await PUBLIC_POST(`/projects/${projectId}/respondent/exchange-code`, {
        // code: code,
        data_provider_name: data_provider_name,
        url_params: postFullParams
      });

      response.on('2xx', async (status, data) => {
        if (status === 200) {
          // Check if the data provider was already used

          showSnackbar(t(data.message.id), 'success');
          // Save the access token in local storage as array
          let tokens = JSON.parse(localStorage.getItem('RespondentTempTokens')) || [];

          tokens = tokens.filter((token) => token.data_provider_name !== data_provider_name)

          tokens.push({
            data_provider_name: data_provider_name,
            ...data.entity
          });

          localStorage.setItem('RespondentTempTokens', JSON.stringify(tokens));
          // Redirect to the project page
          navigate(`/dist/${projectId}`);
        }
      });

      response.on('4xx', (_, data) => {
        setStatus({
          failed: true,
          message: t(data.message.id)
        });
      });

      response.on('5xx', (_, data) => {
        setStatus({
          failed: true,
          message: t(data.message.id)
        });
      });
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <Stack sx={{width: '100%', height: '100vh', justifyContent: 'center', alignItems: 'center'}}>
      <LoadingAnimation
        content={
          <Stack spacing={1}>
            <Alert severity={status.failed ? 'error' : 'info'} sx={{width: '100%'}}>
              {status.message}
            </Alert>
            {
              status.failed &&
              <Button onClick={() => navigate(`/dist/${projectId}`)}>{t('ui.respondent.connection.button.go_back')}</Button>
            }
          </Stack>
        }
        failed={status.failed}
      />
    </Stack>
  )
}

export default PageParticipantOauth2Redirect
