import loadable from '@loadable/component';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import RestoreIcon from '@mui/icons-material/Restore';
import ScienceIcon from '@mui/icons-material/Science';
import SyncIcon from '@mui/icons-material/Sync';
import { LoadingButton } from '@mui/lab';
import { Button, ButtonGroup, Stack, TextField, Typography } from '@mui/material';
import React, { JSX, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';
import { useDebouncedCallback } from 'use-debounce';

import { DEL, GET, POST, POST_BLOB, PUT } from '../code/http_requests';
import AuthUser from '../components/auth/AuthUser';
import ConfirmationDialog from '../components/feedback/ConfirmationDialog';
import { Loading, LoadingAnimation } from '../components/feedback/Loading';
import CopyClipboard from '../components/input/CopyClipboard';
import LayoutMain from '../components/layout/LayoutMain';
import { formatDateStringToLocale } from '../components/utils/FormatDate';
import { useSnackbar } from '../context/SnackbarContext';
import { API } from '../types';
import { ResponseData, ResponseError } from '../types/api';

const SurveyPlatformIntegration = loadable(
  () => import('../components/project/survey_platform/SurveyPlatformIntegration'),
  {
    fallback: <LoadingAnimation />,
  }
);
const DataProviders = loadable(() => import('../components/project/data_provider/DataProviders'), {
  fallback: <LoadingAnimation />,
});
const VariableManagement = loadable(() => import('../components/project/VariableManagement'), {
  fallback: <LoadingAnimation />,
});

interface ProjectNameFieldProps {
  project: API.Projects.Project;
}

const ProjectNameField = ({ project }: ProjectNameFieldProps): JSX.Element => {
  const { t } = useTranslation();

  const { showBottomCenter: showSnackbar } = useSnackbar();

  const [name, setName] = useState(project.name);

  useEffect(() => {
    setName(project.name);
  }, [project]);

  const handleSave = useDebouncedCallback(
    useCallback(
      async (projectName: string) => {
        const response = await PUT(`/projects/${project.id}`, {
          name: projectName,
        });

        response.on('2xx', async (status: number, data: ResponseData) => {
          if (status === 200) {
            showSnackbar(t(data.message.id), 'success');
          }
        });

        response.on('4xx', (_: number, data: ResponseData) => {
          showSnackbar(t(data.message.id), 'error');
        });
      },
      [project, showSnackbar, t]
    ),
    500
  );

  return (
    <TextField
      label={t('ui.project.field.name.label')}
      value={name}
      variant={'standard'}
      required
      onChange={ev => {
        setName(ev.target.value);
        handleSave(ev.target.value);
      }}
    />
  );
};

const PageProject = (): JSX.Element => {
  const { t } = useTranslation();

  const navigate = useNavigate();

  const { showBottomCenter: showSnackbar } = useSnackbar();

  const { projectId } = useParams<{ projectId: string }>();

  const [loadingSurveyPlatformIntegration, setLoadingSurveyPlatformIntegration] = useState(true); // Loading state for SurveyPlatformIntegration
  const [loadingDataProviders, setLoadingDataProviders] = useState(true); // Loading state for DataProviders
  const [loadingVariables, setLoadingVariables] = useState(true); // Loading state for VariableManagement
  const [syncLoading, setSyncLoading] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const [lastSynced, setlastSynced] = useState<string | null>(null);
  const [clearResondentDataDialogOpen, setClearResondentDataDialogOpen] = useState(false);

  const [project, setProject] = useState<API.Projects.Project | null>(null);

  const fetchProject = useCallback(
    async (projectId: string) => {
      setLoadingSurveyPlatformIntegration(true); // Start loading
      setLoadingDataProviders(true); // Start loading
      setLoadingVariables(true); // Start loading
      const response = await GET(`/projects/${projectId}`);

      response.on('2xx', (status: number, data: API.Projects.Project) => {
        if (status === 200) {
          setProject(data);
          setlastSynced(data.last_synced);
          setLoadingSurveyPlatformIntegration(false); // Stop loading
          setLoadingDataProviders(false); // Stop loading
          setLoadingVariables(false); // Stop loading
        }
      });

      response.on('4xx', (status: number, data: ResponseData) => {
        showSnackbar(t(data.message.id), 'error');
        setLoadingSurveyPlatformIntegration(false); // Stop loading
        setLoadingDataProviders(false); // Stop loading
        setLoadingVariables(false); // Stop loading
        if (status === 404) {
          navigate('/projects');
        }
      });
    },
    [showSnackbar, t, navigate]
  );

  useEffect(() => {
    fetchProject(projectId || '');
  }, [projectId, fetchProject]);

  const syncVariables = useCallback(
    async (project: API.Projects.Project) => {
      setSyncLoading(true);
      const response = await POST(`/projects/${projectId}/sync_variables`);
      setSyncLoading(false);
      const lastSynced = project.last_synced;
      setlastSynced(null);
      response.on('2xx', (status: number, data: ResponseData) => {
        if (status === 200) {
          showSnackbar(t(data.message.id), 'success');
          setlastSynced(new Date().toISOString());
        }
      });

      response.on('4xx', (_: number, data: ResponseData) => {
        showSnackbar(t(data.message.id), 'error');
        setlastSynced(lastSynced);
      });

      response.on('5xx', (_: number, data: ResponseError) => {
        showSnackbar(data.error, 'error');
        setlastSynced(lastSynced);
      });
    },
    [projectId, showSnackbar, t]
  );

  const downloadRespondentResponses = useCallback(async () => {
    setDownloadLoading(true);
    const response = await POST_BLOB(`/projects/${projectId}/export_survey_responses`);
    setDownloadLoading(false);

    response.on('2xx', async (status: number, blob: never) => {
      if (status === 200) {
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.setAttribute('download', 'survey_responses.zip'); // Set the filename for the download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    });

    response.on('4xx', (_: number, data: ResponseData) => {
      showSnackbar(t(data.message.id), 'error');
    });

    response.on('5xx', (_: number, data: ResponseError) => {
      showSnackbar(data.error, 'error');
    });
  }, [projectId, showSnackbar, t]);

  const previewSurvey = useCallback(async () => {
    const response = await GET(`/projects/${projectId}/preview_survey`);

    response.on('2xx', (status: number, data: URL) => {
      if (status === 200) {
        window.open(data, '_blank');
      }
    });

    response.on('4xx', (_: number, data: ResponseData) => {
      showSnackbar(t(data.message.id), 'error');
    });

    response.on('5xx', (_: number, data: ResponseError) => {
      showSnackbar(data.error, 'error');
    });
  }, [projectId, showSnackbar, t]);

  const clearRespondentData = useCallback(async () => {
    const response = await DEL(`/projects/${projectId}/respondents`);

    response.on('2xx', (status: number, data: ResponseData) => {
      if (status === 200) {
        showSnackbar(t(data.message.id), 'success');
      }
    });

    response.on('4xx', (_: number, data: ResponseData) => {
      showSnackbar(t(data.message.id), 'error');
    });

    response.on('5xx', (_: number, data: ResponseError) => {
      showSnackbar(data.error, 'error');
    });
  }, [projectId, showSnackbar, t]);

  const domain = window.location.origin;
  return (
    <>
      <LayoutMain
        backUrl="/projects"
        header={
          project && (
            <Stack direction="row" alignItems="center" spacing={2}>
              <Stack flex={1}>
                <ProjectNameField project={project} />
              </Stack>
              <CopyClipboard label={t('ui.project.clipboard.copy.label')} what={`${domain}/dist/${project.short_id}`} />

              <Stack direction={'column'} alignItems={'flex-start'} spacing={0.5}>
                <Stack direction={'row'} alignItems={'flex-start'} spacing={0.5}>
                  <LoadingButton
                    variant="contained"
                    size={'small'}
                    loading={syncLoading}
                    color="primary"
                    startIcon={<SyncIcon />}
                    onClick={() => {
                      syncVariables(project);
                    }}
                  >
                    {t('ui.project.button.sync_variables')}
                  </LoadingButton>

                  <ButtonGroup disableElevation size="small" variant="outlined" aria-label="Project Actions">
                    <Stack direction="row" alignItems="flex-start" spacing={1}>
                      <Button size={'small'} color="primary" startIcon={<ScienceIcon />} onClick={previewSurvey}>
                        {t('ui.project.button.preview_survey')}
                      </Button>
                      <LoadingButton
                        size={'small'}
                        color="primary"
                        loading={downloadLoading}
                        startIcon={<FileDownloadIcon />}
                        onClick={downloadRespondentResponses}
                      >
                        {t('ui.project.button.download_data')}
                      </LoadingButton>
                      <Button
                        size={'small'}
                        color="error"
                        startIcon={<RestoreIcon />}
                        onClick={() => setClearResondentDataDialogOpen(true)}
                      >
                        {t('ui.project.button.delete_all_respondents')}
                      </Button>
                    </Stack>
                  </ButtonGroup>
                </Stack>

                {project.last_synced !== null && !syncLoading && (
                  <Typography variant="caption" color="text.secondary">
                    {`${t('ui.project.label.last_synced')} ${formatDateStringToLocale(lastSynced as string)}`}
                  </Typography>
                )}
              </Stack>
            </Stack>
          )
        }
        headerRightCorner={<AuthUser />}
        loading={!project}
        horizontalContainerProps={{
          maxWidth: false,
        }}
      >
        <Stack spacing={8} width={'100%'} alignItems={'flex-start'} paddingBottom={8}>
          <Stack spacing={2}>
            <Typography variant="h6"> {t('ui.project.survey_platform.title')}</Typography>
            <Loading loading={loadingSurveyPlatformIntegration}>
              <SurveyPlatformIntegration project={project} />
            </Loading>
          </Stack>

          <Loading loading={loadingDataProviders}>
            <DataProviders
              project={project}
              onChangeDataProviders={async () => {
                await fetchProject(projectId || '');
              }}
            />
          </Loading>

          <Loading loading={loadingVariables}>
            <VariableManagement
              project={project}
              onChangeBuiltinVariables={(newBuiltinVariables: API.Projects.BuiltinVariable[]) => {
                // only update by reference, avoid re-rendering
                if (project) {
                  project.variables = newBuiltinVariables;
                }
              }}
              onChangeCustomVariables={(newCustomVariables: API.Projects.CustomVariable[]) => {
                // only update by reference, avoid re-rendering
                if (project) {
                  project.custom_variables = newCustomVariables;
                }
              }}
            />
          </Loading>
        </Stack>
      </LayoutMain>
      <ConfirmationDialog
        open={clearResondentDataDialogOpen}
        title={t('ui.project.dialog.delete_respondents.title')}
        content={
          <Stack spacing={2}>
            <Typography variant="body1">{t('ui.project.dialog.delete_respondents.content')}</Typography>
          </Stack>
        }
        onClose={() => setClearResondentDataDialogOpen(false)}
        onConfirm={clearRespondentData}
      />
    </>
  );
};

export default PageProject;
