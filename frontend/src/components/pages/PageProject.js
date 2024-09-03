import {useCallback, useEffect, useState} from "react";
import {Button, ButtonGroup, Stack, TextField, Typography} from "@mui/material"

import {useNavigate, useParams} from "react-router-dom";

import Authorization from "../auth/Authorization"
import LayoutMain from "../layout/LayoutMain"
import {useSnackbar} from "../../context/SnackbarContext";

import {GET, POST, POST_BLOB, PUT, DEL} from "../../code/http_requests";
import CopyClipboard from "../input/CopyClipboard";

import SyncIcon from '@mui/icons-material/Sync';
import ScienceIcon from '@mui/icons-material/Science';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import RestoreIcon from '@mui/icons-material/Restore';


import DataProviders from "./project/data_provider/DataProviders";
import SurveyPlatformIntegration from "./project/SurveyPlatformIntegration";

import VariableManagement from "./project/variables/VariableManagement";
import {LoadingButton} from "@mui/lab";
import AuthUser from "../auth/AuthUser";
import {useDebouncedCallback} from "use-debounce";

import {useTranslation} from 'react-i18next';
import DialogFeedback from "../feedback/DialogFeedback";

import {formatDateStringToLocale} from "../utils/FormatDate";

// import ReactTimeAgo from 'react-time-ago';


const ProjectNameField = ({project}) => {

  const {t} = useTranslation();

  const {showBottomCenter: showSnackbar} = useSnackbar();

  const [name, setName] = useState(project.name);

  useEffect(() => {
    setName(project.name)
  }, [project]);


  const handleSave = useDebouncedCallback(useCallback(async (projectName) => {
    const response = await PUT(`/projects/${project.id}`, {
      name: projectName
    });

    response.on('2xx', async (status, data) => {
      if (status === 200) {
        showSnackbar(t(data.message.id), 'success');
      }
    });

    response.on('4xx', (_, data) => {
      showSnackbar(t(data.message.id), 'error');
    });
  }, [project, showSnackbar, t]), 500);

  return <TextField
    label={t('ui.project.field.name.label')}
    value={name}
    variant={"standard"}
    required
    onChange={(ev) => {
      setName(ev.target.value);
      handleSave(ev.target.value);
    }}
  />
}


const PageProject = () => {

  const {t} = useTranslation();

  const navigate = useNavigate();


  const {showBottomCenter: showSnackbar} = useSnackbar();

  const {projectId} = useParams();

  const [ syncLoading, setSyncLoading ] = useState(false);
  const [ downloadLoading, setDownloadLoading ] = useState(false);
  const [ lastSynched, setLastSynched ] = useState(null);
  const [ clearResondentDataDialogOpen, setClearResondentDataDialogOpen ] = useState(false);

  const [ project, setProject ] = useState(null);

  const fetchProject = useCallback(async (projectId) => {
    const response = await GET(`/projects/${projectId}`);

    response.on('2xx', (status, data) => {
      if (status === 200) {
        setProject(data);
        setLastSynched(data.last_synced);
      }
    });

    response.on('4xx', (status, data) => {
      console.log("status", status, "data", data);
      showSnackbar(t(data.message.id), 'error');
      if(status === 404) {
        navigate('/projects');
      }
    });
  }, [showSnackbar, t, navigate]);

  useEffect(() => {
    fetchProject(projectId);
  }, [projectId, fetchProject]);

  const syncVariables = useCallback(async () => {
    setSyncLoading(true);
    const response = await POST(`/projects/${projectId}/sync_variables`);
    setSyncLoading(false);
    const lastSynched = project.last_synced;
    setLastSynched(null);
    response.on('2xx', (status, data) => {
      if (status === 200) {
        showSnackbar(t(data.message.id), 'success');
        setLastSynched((new Date()).toISOString());
      }
    });

    response.on('4xx', (_, data) => {
      showSnackbar(t(data.message.id), 'error')
      setLastSynched(lastSynched);
    });

    response.on('5xx', (_, data) => {
      showSnackbar(data.error, 'error');
      setLastSynched(lastSynched);
    });

  }, [projectId, showSnackbar, t, project]);

  const downloadRespondentResponses = useCallback(async () => {

    setDownloadLoading(true);
    const response = await POST_BLOB(`/projects/${projectId}/export_survey_responses`);
    setDownloadLoading(false);

    response.on('2xx', async (status, blob) => {
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

    response.on('4xx', (_, data) => {
      showSnackbar(t(data.message.id), 'error');
    });

    response.on('5xx', (_, data) => {
      showSnackbar(data.error, 'error');
    });

  }, [projectId, showSnackbar, t]);

  const previewSurvey = useCallback(async () => {
    const response = await GET(`/projects/${projectId}/preview_survey`);

    response.on('2xx', (status, data) => {
      if (status === 200) {
        window.open(data, '_blank');
      }

    });

    response.on('4xx', (_, data) => {
      showSnackbar(t(data.message.id), 'error');
    });

    response.on('5xx', (_, data) => {
      showSnackbar(data.error, 'error');
    });
  }, [projectId, showSnackbar, t]);


  const clearRespondentData = useCallback(async () => {
    const response = await DEL(`/projects/${projectId}/respondents`);

    response.on('2xx', (status, data) => {
      if (status === 200) {
        showSnackbar(t(data.message.id), 'success');
      }
    });

    response.on('4xx', (_, data) => {
      showSnackbar(t(data.message.id), 'error');
    });

    response.on('5xx', (_, data) => {
      showSnackbar(data.error, 'error');
    });

  }, [projectId, showSnackbar, t]);


  const domain = window.location.origin;
  return (
    <Authorization>
      {project &&
        <LayoutMain
          backUrl="/projects"
          header={
            <Stack direction="row" alignItems="center" spacing={2}>
              <Stack flex={1}>
                <ProjectNameField project={project}/>
              </Stack>
              <CopyClipboard
                label={t('ui.project.clipboard.copy.label')}
                what={`${domain}/dist/${project.short_id}`}
              />

              <Stack direction={"column"} alignItems={"flex-start"} spacing={.5}>
                <Stack direction={"row"} alignItems={"flex-start"} spacing={.5}>

                  <LoadingButton
                    variant="contained"
                    size={"small"}
                    loading={syncLoading}
                    color="primary"
                    startIcon={<SyncIcon/>}
                    onClick={syncVariables}>
                    {t('ui.project.button.sync_variables')}
                  </LoadingButton>


                  <ButtonGroup disableElevation size="small" variant="outlined" aria-label="Project Actions">
                    <Stack direction="row" alignItems="flex-start" spacing={1}>

                      <Button
                        size={"small"}
                        color="primary"
                        startIcon={<ScienceIcon/>}
                        onClick={previewSurvey}
                        >
                        {t('ui.project.button.preview_survey')}

                      </Button>
                      <LoadingButton
                        size={"small"}
                        color="primary"
                        loading={downloadLoading}
                        startIcon={<FileDownloadIcon/>}
                        onClick={downloadRespondentResponses}
                        >
                        {t('ui.project.button.download_data')}
                      </LoadingButton>
                      <Button size={"small"}
                              color="error"
                              startIcon={<RestoreIcon/>}
                              onClick={() => setClearResondentDataDialogOpen(true)}>
                        {t('ui.project.button.delete_all_respondents')}
                      </Button>
                    </Stack>
                  </ButtonGroup>
                </Stack>

                {project.last_synced !== null && !syncLoading && (
                  // <Typography variant="caption" color="text.secondary">
                  //     {t('ui.project.label.last_synced')} <ReactTimeAgo date={project.last_synced} locale="en-US" />
                  // </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {`${t('ui.project.label.last_synced')} ${formatDateStringToLocale(lastSynched)}`}
                  </Typography>
                )}
              </Stack>
            </Stack>

          }
          headerRightCorner={<AuthUser/>}
        >
          <Stack spacing={8} width={"100%"} alignItems={"flex-start"} pb={8}>

            <SurveyPlatformIntegration
              project={project}
            />
            <DataProviders
              project={project}
              onChangeDataProviders={async () => {
                await fetchProject(projectId);
              }}
            />
            <VariableManagement
              project={project}
              onChangeBuiltinVariables={(newBuiltinVariables) => {
                // only update by reference, avoid rerendering
                project.variables = newBuiltinVariables;
              }}
              onChangeCustomVariables={(newCustomVariables) => {
                // only update by reference, avoid rerendering
                project.custom_variables = newCustomVariables;
              }}
            />

          </Stack>
          <DialogFeedback
            open={clearResondentDataDialogOpen}
            title={t('ui.project.dialog.delete_respondents.title')}
            content={
              <Stack spacing={2}>
                <Typography variant="body1">
                  {t('ui.project.dialog.delete_respondents.content')}
                </Typography>
              </Stack>
            }
            onClose={() => setClearResondentDataDialogOpen(false)}
            onConfirm={clearRespondentData}
          />
        </LayoutMain>
      }

    </Authorization>

  )
}


export default PageProject
