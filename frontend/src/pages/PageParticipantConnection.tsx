import loadable from '@loadable/component';
import AddIcon from '@mui/icons-material/Add';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Alert, AlertTitle, Box, Button, CircularProgress, Collapse, Link, Stack, Typography } from '@mui/material';
import type { JSX } from 'react';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';

import { PUBLIC_GET, PUBLIC_POST } from '../code/http_requests';
import ClickTracker from '../components/events/ClickTracker';
import useEventTracker from '../components/events/useEventTracker';
import ConnectionBadge from '../components/feedback/ConnectionBadge';
import LayoutMain from '../components/layout/LayoutMain';
import { useSnackbar } from '../context/SnackbarContext';
import type { API, Models } from '../types';

const UsedVariablesTable = loadable(() => import('../components/layout/UsedVariablesTable'));

const isDataProviderAlreadyUsed = async function isDataProviderAlreadyUsed(
  projectShortId: string,
  data_provider_name: string,
  user_id: string
): Promise<boolean> {
  const response = await PUBLIC_POST(`/projects/${projectShortId}/respondent/data-provider/was-used`, {
    data_provider_name,
    user_id,
  });

  let was_used = false;

  response.on('2xx', (_: number, data: { was_used: boolean }) => {
    was_used = data.was_used;
  });

  return was_used;
};

interface PageParticipantConnectionProps {
  placeholder?: boolean;
}

const PageParticipantConnection = ({ placeholder = false }: PageParticipantConnectionProps): JSX.Element => {
  const { t } = useTranslation();
  const { showBottomCenter: showSnackbar } = useSnackbar();

  const { projectShortId } = useParams<{ projectShortId: string }>();
  const { getEvents, reset: resetEvents } = useEventTracker();

  const [project, setProject] = useState<API.Respondent.Project | null>(null);
  const [dataProviders, setDataProviders] = useState<Models.Dist.DataProvider[]>([]);
  const [expand, setExpand] = useState(false);

  const [preparingSurvey, setPreparingSurvey] = useState<boolean>(false);
  const [surveyURL, setSurveyURL] = useState<string | null>(null);
  const [urlParams] = useState<string>('');

  const anyProviderConnected = useMemo(() => dataProviders.some(provider => provider.token), [dataProviders]);
  const allProvidersConnected = useMemo(() => dataProviders.every(provider => provider.token), [dataProviders]);
  const anyProviderAlreadyUsed = useMemo(() => dataProviders.some(provider => provider.was_used), [dataProviders]);
  const allProvidersAlreadyUsed = useMemo(() => dataProviders.every(provider => provider.was_used), [dataProviders]);

  const fetchProject = useCallback(async (): Promise<void> => {
    setProject(null);

    const response = await PUBLIC_GET(`/projects/${projectShortId}/respondent/`);

    response.on('2xx', async (status: number, data: API.Respondent.Project) => {
      if (status === 200) {
        setProject(data);
      }
    });

    response.on('4xx', (status: number, data: API.Respondent.Project | API.ResponseData) => {
      if (status === 400) {
        setProject(data as API.Respondent.Project);
      } else {
        showSnackbar(t((data as API.ResponseData).message.id), 'error');
      }
    });
  }, [projectShortId, showSnackbar, t]);

  const fetchOauthDataProviders = useCallback(async () => {
    if (!projectShortId) {
      showSnackbar(t('error.project_not_found'), 'error');
      return;
    }
    const response = await PUBLIC_GET(`/projects/${projectShortId}/respondent/data-providers`);

    response.on('2xx', async (status: number, data_providers: API.Respondent.DataProvider[]): Promise<void> => {
      const tokens: Models.Dist.RespondentTempTokens[] = JSON.parse(
        localStorage.getItem('RespondentTempTokens') || '[]'
      );
      if (status === 200) {
        const providersPromises = data_providers.map(
          async (data_provider: API.Respondent.DataProvider): Promise<Models.Dist.DataProvider> => {
            const token = tokens.find(token => token.data_provider_name === data_provider.data_provider_name);
            let was_used = false;

            if (token) {
              was_used = await isDataProviderAlreadyUsed(
                projectShortId,
                data_provider.data_provider_name,
                token.user_id
              );
            }

            return {
              ...data_provider,
              token,
              was_used,
            };
          }
        );
        const providers = await Promise.all(providersPromises);
        setDataProviders(providers);
      }
    });

    response.on('4xx', (_: number, data: API.ResponseData) => {
      showSnackbar(t(data.message.id, { defaultValue: data.message.text }), 'error');
    });
  }, [projectShortId, showSnackbar, t]);

  useEffect(() => {
    if (placeholder) {
      return;
    }

    if (!projectShortId) {
      showSnackbar(t('error.project_not_found'), 'error');
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
  }, [placeholder, fetchProject, projectShortId, urlParams, showSnackbar, t]);

  useEffect(() => {
    if (project) {
      fetchOauthDataProviders();
    }
  }, [fetchOauthDataProviders, project]);

  const handleConnect = useCallback(
    async (data_provider_name: string) => {
      // Find the authorization URL of the data provider and redirect to it.
      const oauth2DataProvider = dataProviders.find(dp => dp.data_provider_name === data_provider_name);

      if (!oauth2DataProvider) {
        showSnackbar(t('ui.respondent.connection.error.data_provider_not_found'), 'error');
        return;
      }

      window.location.assign(oauth2DataProvider.authorize_url);
    },
    [dataProviders, showSnackbar, t]
  );

  const handleDisconnect = useCallback(
    async (data_provider_name: string) => {
      // only remove the token from the data provider and from the local storage.
      const tokens: Models.Dist.RespondentTempTokens[] = JSON.parse(
        localStorage.getItem('RespondentTempTokens') || '[]'
      );

      localStorage.setItem(
        'RespondentTempTokens',
        JSON.stringify(tokens.filter(token => token.data_provider_name !== data_provider_name))
      );

      const providers = dataProviders.map(provider => {
        if (provider.data_provider_name === data_provider_name) {
          return {
            ...provider,
            token: null,
          };
        }
        return provider;
      });

      setDataProviders(providers);
    },
    [dataProviders]
  );

  const handleProceed = useCallback(async () => {
    if (anyProviderAlreadyUsed && !allProvidersAlreadyUsed) {
      // allProvidersConnected is already check at the button level
      showSnackbar(t('ui.respondent.connection.error.resume_must_connect_all_previous_data_providers'), 'error');
      return;
    }

    setPreparingSurvey(true);

    // this will persist the data connection access tokens, it will eventually create a respondent and create or update the data connections
    const connect_response = await PUBLIC_POST(`/projects/${projectShortId}/respondent/connect`, {
      data_providers: dataProviders,
    });

    connect_response.on('2xx', async (_: number, data: API.Respondent.ResponseDataSurveyDistribution) => {
      const response_prepare = await PUBLIC_POST(`/projects/${projectShortId}/respondent/prepare-survey`, {
        frontend_variables: getEvents(),
        respondent_id: data.entity.id,
      });

      setPreparingSurvey(false);

      showSnackbar(t(data.message.id, { defaultValue: data.message.text }), 'success');

      response_prepare.on('2xx', (status: number, data: API.Respondent.ResponseDataSurveyDistribution) => {
        if (status === 200) {
          resetEvents();
          setSurveyURL(data.entity.url);
          // wait 2 seconds and then redirect
          showSnackbar(t(data.message.id, { defaultValue: data.message.text }), 'success');
          setTimeout(() => {
            let separator = '';
            let storedParams = '';
            if (localStorage.getItem('urlParams') !== '') {
              separator = data.entity.url.includes('?') ? '&' : '?';
              storedParams = localStorage.getItem('urlParams') || '';
            }

            // Clear the local storage right before redirecting.
            // localStorage.clear();
            localStorage.removeItem('RespondentTempProjectId');
            localStorage.removeItem('RespondentTempTokens');
            localStorage.removeItem('urlParams');

            window.location.assign(`${data.entity.url}${separator}${storedParams}`);
          }, 2000);
        }
      });

      response_prepare.on('4xx', (_: number, data: API.ResponseData) => {
        setPreparingSurvey(false);
        showSnackbar(t(data.message.id, { defaultValue: data.message.text }), 'error');
      });
    });

    connect_response.on('4xx', (_: number, data: API.ResponseData) => {
      setPreparingSurvey(false);
      showSnackbar(t(data.message.id, { defaultValue: data.message.text }), 'error');
    });
  }, [
    anyProviderAlreadyUsed,
    allProvidersAlreadyUsed,
    dataProviders,
    getEvents,
    projectShortId,
    resetEvents,
    showSnackbar,
    t,
  ]);

  return (
    <LayoutMain
      header={
        project && (
          <Stack alignItems="center" direction="row" justifyContent={'center'}>
            <Typography style={{ whiteSpace: 'nowrap' }} variant="h5">
              <b>{project.survey_name}</b>
            </Typography>
          </Stack>
        )
      }
      loading={!project || !dataProviders}
    >
      {project && (
        <CheckProjectReadiness project_ready={project.project_ready}>
          {dataProviders && dataProviders.length > 0 && (
            <Stack spacing={4}>
              <Box>
                <Typography variant="body1">
                  <b>{t('ui.respondent.connection.info')}</b>
                </Typography>
                <Typography variant="body1">
                  <Link href={'/privacy-policy'} rel="noopener">
                    {t('ui.respondent.connection.click_here')}
                  </Link>
                  {t('ui.respondent.connection.click_here_to_read_privacy_policy')}
                </Typography>
              </Box>

              {project.used_variables && (
                <Box>
                  <ClickTracker
                    details={{
                      id: 'dds.dds.builtin.frontendactivity.open_transparency_table',
                      time: new Date().toISOString(),
                      type: 'click',
                    }}
                  >
                    <Stack
                      alignItems="center"
                      direction="row"
                      onClick={() => setExpand(!expand)}
                      sx={{ cursor: 'pointer' }}
                    >
                      {expand ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      <Typography variant="body1">
                        {t(
                          'ui.respondent.connection.click_here_to_see_the_data_that_this_survey_will_collect_from_your_accounts'
                        )}
                      </Typography>
                    </Stack>
                  </ClickTracker>
                  <Collapse in={expand}>
                    <UsedVariablesTable used_variables={project.used_variables} />
                  </Collapse>
                </Box>
              )}

              <Box>
                <Typography variant="body1">
                  <b>{t('ui.respondent.connection.connect_to_data_providers')}</b>
                </Typography>
              </Box>
              <Stack spacing={1}>
                {dataProviders.map((data_provider, index) => {
                  return (
                    <Stack
                      alignItems={'center'}
                      direction={'row'}
                      justifyContent={'space-between'}
                      key={index}
                      spacing={2}
                    >
                      <ConnectionBadge name={data_provider.data_provider_name} />
                      {data_provider.token ? (
                        <Stack alignItems={'center'} direction={'row'}>
                          <Typography variant="body1">Connected as {data_provider.token.user_name}</Typography>
                          <Button
                            color={'primary'}
                            disabled={preparingSurvey || surveyURL !== null}
                            onClick={() => handleDisconnect(data_provider.data_provider_name)}
                            variant={'text'}
                          >
                            {t('ui.respondent.connection.button.disconnect')}
                          </Button>
                          <DataProviderConnectionStatus
                            allProvidersAlreadyUsed={allProvidersAlreadyUsed}
                            anyProviderAlreadyUsed={anyProviderAlreadyUsed}
                            was_used={data_provider.was_used}
                          />
                        </Stack>
                      ) : (
                        <Button
                          color={'primary'}
                          onClick={() => handleConnect(data_provider.data_provider_name)}
                          startIcon={<AddIcon />}
                          variant={'contained'}
                        >
                          {t('ui.respondent.connection.button.connect')}
                        </Button>
                      )}
                    </Stack>
                  );
                })}
              </Stack>
              {preparingSurvey && (
                <Stack alignItems={'center'} direction={'row'} justifyContent={'center'} spacing={2}>
                  <CircularProgress size={24} value={100} />
                  <Alert severity="info">{t('ui.respondent.connection.alert.preparing_survey')}</Alert>
                </Stack>
              )}
              {surveyURL && (
                <Stack alignItems={'center'} direction={'row'} justifyContent={'center'} spacing={2}>
                  <Alert severity="success">
                    <AlertTitle>{t('ui.respondent.connection.alert.survey_ready.title')}</AlertTitle>
                    <Typography variant="body1">
                      {t('ui.respondent.connection.alert.survey_ready.message.will_be_redirected')}
                    </Typography>
                    <Link color="primary" href={surveyURL} rel="noreferrer" target={'_blank'} variant="body1">
                      {t('ui.respondent.connection.click_here')}
                    </Link>{' '}
                    {t('ui.respondent.connection.if_not_redirected_automatically')}
                  </Alert>
                </Stack>
              )}
              {!preparingSurvey && !surveyURL && (
                <ConnectionStatus
                  allProvidersAlreadyUsed={allProvidersAlreadyUsed}
                  allProvidersConnected={allProvidersConnected}
                  anyProviderAlreadyUsed={anyProviderAlreadyUsed}
                  anyProviderConnected={anyProviderConnected}
                />
              )}

              <Stack alignItems={'center'} spacing={2}>
                <Button
                  color={'primary'}
                  disabled={!allProvidersConnected || preparingSurvey || surveyURL !== null}
                  onClick={handleProceed}
                  variant={'contained'}
                >
                  {allProvidersConnected && allProvidersAlreadyUsed ? 'Resume' : 'Proceed'}
                </Button>
              </Stack>
            </Stack>
          )}
        </CheckProjectReadiness>
      )}
    </LayoutMain>
  );
};

interface CheckProjectReadinessProps {
  children: React.ReactNode;
  project_ready: boolean;
}

/**
 * Only used for conditional rendering of the children based on the project readiness
 */
const CheckProjectReadiness = ({ children, project_ready }: CheckProjectReadinessProps): React.ReactNode => {
  const { t } = useTranslation();

  return project_ready ? (
    children
  ) : (
    <Stack alignItems={'center'} height={'100vh'} justifyContent={'center'} width={'100vw'}>
      <Alert severity="error">
        <Typography variant="body1">{t('ui.respondent.connection.project_not_ready')}</Typography>
      </Alert>
    </Stack>
  );
};

interface DataProviderConnectionStatusProps {
  allProvidersAlreadyUsed: boolean;
  anyProviderAlreadyUsed: boolean;
  was_used: boolean;
}

const DataProviderConnectionStatus = ({
  allProvidersAlreadyUsed,
  anyProviderAlreadyUsed,
  was_used,
}: DataProviderConnectionStatusProps): JSX.Element | boolean => {
  const { t } = useTranslation();

  const warning = was_used && !allProvidersAlreadyUsed;
  const error = !was_used && anyProviderAlreadyUsed;

  const severity = warning ? 'warning' : error ? 'error' : 'info';

  return (
    (warning || error) && (
      <Alert severity={severity}>
        {warning && (
          <Typography variant="body1">{t('ui.respondent.connection.data_provider.status.warning')}</Typography>
        )}
        {error && <Typography variant="body1">{t('ui.respondent.connection.data_provider.status.error')}</Typography>}
      </Alert>
    )
  );
};

interface ConnectionStatusProps {
  allProvidersAlreadyUsed: boolean;
  allProvidersConnected: boolean;
  anyProviderAlreadyUsed: boolean;
  anyProviderConnected: boolean;
}

const ConnectionStatus = ({
  allProvidersAlreadyUsed,
  allProvidersConnected,
  anyProviderAlreadyUsed,
  anyProviderConnected,
}: ConnectionStatusProps): JSX.Element | boolean => {
  const { t } = useTranslation();

  const warning = anyProviderConnected && !allProvidersConnected && anyProviderAlreadyUsed;
  const error = allProvidersConnected && anyProviderAlreadyUsed && !allProvidersAlreadyUsed;
  const success = allProvidersConnected && anyProviderAlreadyUsed;

  const severity = warning ? 'warning' : error ? 'error' : success ? 'success' : 'info';

  return (
    (warning || error || success) && (
      <Alert severity={severity}>
        {warning && <Typography variant="body1">{t('ui.respondent.connection.status.warning')}</Typography>}
        {error && <Typography variant="body1">{t('ui.respondent.connection.status.error')}</Typography>}
        {success && <Typography variant="body1">{t('ui.respondent.connection.status.success')}</Typography>}
      </Alert>
    )
  );
};

export default PageParticipantConnection;
