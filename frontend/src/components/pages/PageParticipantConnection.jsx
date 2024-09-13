import loadable from '@loadable/component';
import AddIcon from '@mui/icons-material/Add';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {
  Alert,
  AlertTitle,
  Box,
  Button,
  CircularProgress,
  Stack,
  Link,
  Typography,
  Collapse,
  Container,
} from "@mui/material"
import {useCallback, useEffect, useMemo, useState} from "react";
import React from 'react';
import {useTranslation} from 'react-i18next';
import {useParams} from "react-router-dom";

import {PUBLIC_GET, PUBLIC_POST} from "../../code/http_requests";
import {useSnackbar} from "../../context/SnackbarContext";
import ClickTracker from "../events/ClickTracker";
import useEventTracker from "../events/useEventTracker";
import ConnectionBadge from "../feedback/ConnectionBadge";
import LayoutMain from "../layout/LayoutMain"

const UsedVariablesTable = loadable(() => import('./participants/UsedVariablesTable'));

const isDataProviderAlreadyUsed = async (projectShortId, data_provider_name, user_id) => {
  const response = await PUBLIC_POST(`/projects/${projectShortId}/respondent/data-provider/was-used`, {
    data_provider_name: data_provider_name,
    user_id: user_id,
  });

  let was_used = false;

  response.on('2xx', () => {
    was_used = response?.data?.was_used;
  });

  return was_used;
}

const PageParticipantConnection = ({placeholder = false}) => {
  const {t} = useTranslation();

  const {projectShortId} = useParams();

  const {showBottomCenter: showSnackbar} = useSnackbar();

  const {reset: resetEvents, getEvents} = useEventTracker();

  const [project, setProject] = useState(null);

  const [dataProviders, setDataProviders] = useState([]);

  const [expand, setExpand] = useState(false);

  const [preparingSurvey, setPreparingSurvey] = useState(false);
  const [surveyURL, setSurveyURL] = useState(null);
  const [urlParams] = useState("");

  const anyProviderConnected = useMemo(() => dataProviders.some(provider => provider.token), [dataProviders]);
  const allProvidersConnected = useMemo(() => dataProviders.every(provider => provider.token), [dataProviders]);
  const anyProviderAlreadyUsed = useMemo(() => dataProviders.some(provider => provider.was_used), [dataProviders]);
  const allProvidersAlreadyUsed = useMemo(() => dataProviders.every(provider => provider.was_used), [dataProviders]);

  const fetchProject = useCallback(async () => {
    setProject(null);

    const response = await PUBLIC_GET(`/projects/${projectShortId}/respondent/`);

    response.on('2xx', async (status, data) => {
      if (status === 200) {
        setProject(data);
      }
    });

    response.on('4xx', (status, data) => {
      if (status === 400) {
        setProject(data);
      } else {
        showSnackbar(t(data.message.id), 'error');
      }
    });

  }, [projectShortId, showSnackbar, t]);


  const fetchOauthDataProviders = useCallback(async () => {
    const response = await PUBLIC_GET(`/projects/${projectShortId}/respondent/data-providers`);

    response.on('2xx', async (status, data_providers) => {
      const tokens = JSON.parse(localStorage.getItem('RespondentTempTokens')) || [];
      if (status === 200) {
        const providersPromises = data_providers.map(async (data_provider) => {
          const token = tokens.find(token => token.data_provider_name === data_provider.data_provider_name);
          let was_used = false;

          if (token) {
            was_used = await isDataProviderAlreadyUsed(projectShortId, data_provider.data_provider_name, token.user_id);
          }

          return {
            ...data_provider,
            token,
            was_used: was_used
          }
        });
        const providers = await Promise.all(providersPromises);
        setDataProviders(providers);
      }
    });

    response.on('4xx', (_, data) => {
      showSnackbar(t(data.message.id), 'error');
    });

  }, [projectShortId, showSnackbar, t]);

  useEffect(() => {
    if (placeholder) {
      return;
    }

    const params = new URLSearchParams(window.location.search);
    const urlParams = params.toString();

    if (localStorage.getItem('RespondentTempProjectId') !== projectShortId) {
      localStorage.removeItem('RespondentTempTokens');
      localStorage.setItem('urlParams', urlParams);
    } else {
      const storedParams = localStorage.getItem('urlParams');
      if (!storedParams) {
        localStorage.setItem('urlParams', urlParams);
      }
    }

    localStorage.setItem('RespondentTempProjectId', projectShortId);

    fetchProject();

  }, [placeholder, fetchProject, projectShortId, urlParams]);

  useEffect(() => {
    if (project) {
      fetchOauthDataProviders();
    }
  }, [fetchOauthDataProviders, project]);

  const handleConnect = useCallback(async (data_provider_name) => {
    // Find the authorization URL of the data provider and redirect to it.
    const oauth2DataProvider = dataProviders.find(dp => dp.data_provider_name === data_provider_name);

    if (!oauth2DataProvider) {
      showSnackbar(t('ui.respondent.connection.error.data_provider_not_found'), 'error');
      return;
    }

    window.location.assign(oauth2DataProvider.authorize_url);

  }, [dataProviders, showSnackbar, t]);

  const handleDisconnect = useCallback(async (data_provider_name) => {
    // only remove the token from the data provider and from the local storage.
    const tokens = JSON.parse(localStorage.getItem('RespondentTempTokens')) || [];

    localStorage.setItem('RespondentTempTokens', JSON.stringify(tokens.filter(token => token.data_provider_name !== data_provider_name)));

    const providers = dataProviders.map(provider => {
      if (provider.data_provider_name === data_provider_name) {
        return {
          ...provider,
          token: null
        }
      }
      return provider;
    });

    setDataProviders(providers);

  }, [dataProviders]);

  const handleProceed = useCallback(async () => {

    if (anyProviderAlreadyUsed && !allProvidersAlreadyUsed) {
      // allProvidersConnected is already check at the button level
      showSnackbar(t('ui.respondent.connection.error.resume_must_connect_all_previous_data_providers'), 'error');
      return;
    }

    setPreparingSurvey(true);

    // this will persist the data connection access tokens, it will eventually create a respondent and create or update the data connections
    const connect_response = await PUBLIC_POST(`/projects/${projectShortId}/respondent/connect`, {
      data_providers: dataProviders
    });

    connect_response.on('2xx', async (_, data) => {
      const response_prepare = await PUBLIC_POST(`/projects/${projectShortId}/respondent/prepare-survey`, {
        respondent_id: data.entity.id,
        frontend_variables: getEvents()
      });

      setPreparingSurvey(false);

      showSnackbar(t(data.message.id), 'success');

      response_prepare.on('2xx', (status, data) => {
        if (status === 200) {
          resetEvents();
          setSurveyURL(data.entity.url);
          // wait 2 seconds and then redirect
          showSnackbar(t(data.message.id), 'success');
          setTimeout(() => {
            let separator = '';
            let storedParams = '';
            if (localStorage.getItem('urlParams') !== '') {
              separator = data.entity.url.includes('?') ? '&' : '?';
              storedParams = localStorage.getItem('urlParams') || '';
            }

            // Clear the local storage right before redirecting.
            localStorage.clear();

            window.location.assign(`${data.entity.url}${separator}${storedParams}`);
          }, 3000);
        }
      });

      response_prepare.on('4xx', (_, data) => {
        setPreparingSurvey(false);
        showSnackbar(t(data.message.id), 'error');
      });
    });

    connect_response.on('4xx', (_, data) => {
      setPreparingSurvey(false);
      showSnackbar(t(data.message.id), 'error');
    });

  }, [anyProviderAlreadyUsed, allProvidersAlreadyUsed, dataProviders, getEvents, projectShortId, resetEvents, showSnackbar, t]);

  return (
    <LayoutMain
      header={
        project && (
          <Stack direction="row" alignItems="center" justifyContent={"center"}>
            <Typography variant="h5" style={{whiteSpace: 'nowrap'}}><b>{project.survey_name}</b></Typography>
          </Stack>
        )
      }
      loading={!project || !dataProviders}
    >
      {project && (
        <CheckProjectReadiness project_ready={project.project_ready}>
          {dataProviders && dataProviders.length > 0 && (
            <Container>
              <Stack spacing={4}>
                <Box>
                  <Typography variant="body1">
                    <b>{t('ui.respondent.connection.info')}</b>
                  </Typography>
                  <Typography variant="body1">
                    <Link href={"/privacy-policy"} rel="noopener">
                      {t('ui.respondent.connection.click_here')}
                    </Link>
                    {t('ui.respondent.connection.click_here_to_read_privacy_policy')}
                  </Typography>
                </Box>

                {project?.used_variables && (
                  <Box>
                    <ClickTracker details={{
                      type: 'click',
                      id: "dds.dds.builtin.frontendactivity.open_transparency_table",
                      time: new Date().toISOString()
                    }}>
                      <Stack direction="row" alignItems="center" onClick={() => setExpand(!expand)}
                             sx={{cursor: 'pointer'}}>
                        {expand ? <ExpandLessIcon/> : <ExpandMoreIcon/>}
                        <Typography variant="body1">
                          {t('ui.respondent.connection.click_here_to_see_the_data_that_this_survey_will_collect_from_your_accounts')}
                        </Typography>
                      </Stack>
                    </ClickTracker>
                    <Collapse in={expand}>
                      <UsedVariablesTable
                        used_variables={project.used_variables}
                      />
                    </Collapse>
                  </Box>
                )}

                <Box>
                  <Typography variant="body1">
                    <b>{
                      t('ui.respondent.connection.connect_to_data_providers')
                    }</b>
                  </Typography>
                </Box>
                <Stack spacing={1}>
                  {
                    dataProviders.map((data_provider, index) => {
                      return (
                        <Stack direction={"row"} key={index} spacing={2} alignItems={"center"}
                               justifyContent={"space-between"}>
                          <ConnectionBadge name={data_provider.data_provider_name}/>
                          {data_provider.token ?
                            <Stack direction={"row"} alignItems={"center"}>
                              <Typography variant="body1">Connected
                                as {data_provider.token.user_name}</Typography>
                              <Button
                                variant={"text"}
                                color={"primary"}
                                onClick={() => handleDisconnect(data_provider.data_provider_name)}
                                disabled={preparingSurvey || surveyURL}
                              >{
                                t('ui.respondent.connection.button.disconnect')
                              }</Button>
                              <DataProviderConnectionStatus
                                was_used={data_provider.was_used}
                                anyProviderAlreadyUsed={anyProviderAlreadyUsed}
                                allProvidersAlreadyUsed={allProvidersAlreadyUsed}
                              />
                            </Stack>
                            :
                            <Button
                              variant={"contained"}
                              color={"primary"}
                              startIcon={<AddIcon/>}
                              onClick={() => handleConnect(data_provider.data_provider_name)}
                            >{
                              t('ui.respondent.connection.button.connect')
                            }</Button>
                          }
                        </Stack>
                      )
                    })
                  }
                </Stack>
                {
                  preparingSurvey &&
                  <Stack direction={"row"} spacing={2} alignItems={"center"} justifyContent={"center"}>
                    <CircularProgress
                      size={24}
                      value={100}
                    />
                    <Alert severity="info">{
                      t('ui.respondent.connection.alert.preparing_survey')
                    }</Alert>
                  </Stack>
                }
                {
                  surveyURL &&
                  <Stack direction={"row"} spacing={2} alignItems={"center"} justifyContent={"center"}>
                    <Alert severity="success">
                      <AlertTitle>{
                        t('ui.respondent.connection.alert.survey_ready.title')
                      }</AlertTitle>

                      <Typography variant="body1">{
                        t('ui.respondent.connection.alert.survey_ready.message.will_be_redirected')
                      }</Typography>
                      <a href={surveyURL} target={"_blank"} rel="noreferrer">
                        {t('ui.respondent.connection.click_here')}
                      </a> {t('ui.respondent.connection.if_not_redirected_automatically')}

                    </Alert>
                  </Stack>
                }
                {
                  !preparingSurvey && !surveyURL &&
                  <ConnectionStatus
                    allProvidersConnected={allProvidersConnected}
                    anyProviderConnected={anyProviderConnected}
                    anyProviderAlreadyUsed={anyProviderAlreadyUsed}
                    allProvidersAlreadyUsed={allProvidersAlreadyUsed}
                  />
                }

                <Stack spacing={2} alignItems={"center"}>
                  <Button
                    variant={"contained"}
                    color={"primary"}
                    disabled={!allProvidersConnected || preparingSurvey || surveyURL}
                    onClick={handleProceed}
                  >
                    {allProvidersConnected && allProvidersAlreadyUsed ? 'Resume' : 'Proceed'}
                  </Button>
                </Stack>
              </Stack>
            </Container>
          )}
        </CheckProjectReadiness>
      )}
    </LayoutMain>
  )
}


/**
 * Only used for conditional rendering of the children based on the project readiness
 */
const CheckProjectReadiness = ({children, project_ready}) => {
  const {t} = useTranslation();

  return project_ready ? children :
    <Stack width={"100vw"} height={"100vh"} justifyContent={"center"} alignItems={"center"}>
      <Alert severity="error">
        <Typography variant="body1">
          {t('ui.respondent.connection.project_not_ready')}
        </Typography>
      </Alert>
    </Stack>
}


const DataProviderConnectionStatus = ({
  was_used,
  anyProviderAlreadyUsed,
  allProvidersAlreadyUsed
}) => {

  const {t} = useTranslation();

  const warning = was_used && !allProvidersAlreadyUsed;
  const error = !was_used && anyProviderAlreadyUsed;

  const severity = warning ? 'warning' : error ? 'error' : 'info';

  return (
    (warning || error) &&
    <Alert severity={severity}>
      {
        warning &&
        <Typography variant="body1">
          {t('ui.respondent.connection.data_provider.status.warning')}
        </Typography>
      }
      {
        error &&
        <Typography variant="body1">
          {t('ui.respondent.connection.data_provider.status.error')}
        </Typography>

      }
    </Alert>
  )

}


const ConnectionStatus = ({
  allProvidersConnected,
  anyProviderConnected,
  anyProviderAlreadyUsed,
  allProvidersAlreadyUsed
}) => {

  const {t} = useTranslation();

  const warning = anyProviderConnected && !allProvidersConnected && anyProviderAlreadyUsed;
  const error = allProvidersConnected && anyProviderAlreadyUsed && !allProvidersAlreadyUsed;
  const success = allProvidersConnected && anyProviderAlreadyUsed;

  const severity = warning ? 'warning' : error ? 'error' : success ? 'success' : 'info';

  return (
    (warning || error || success) &&
    <Alert severity={severity}>
      {
        warning &&
        <Typography variant="body1">
          {t('ui.respondent.connection.status.warning')}
        </Typography>
      }
      {
        error &&
        <Typography variant="body1">
          {t('ui.respondent.connection.status.error')}
        </Typography>
      }
      {
        success &&
        <Typography variant="body1">
          {t('ui.respondent.connection.status.success')}
        </Typography>
      }
    </Alert>
  )
}


export default PageParticipantConnection;
