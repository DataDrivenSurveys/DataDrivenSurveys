import EditIcon from '@mui/icons-material/Edit';
import SyncIcon from '@mui/icons-material/Sync';
import {Button, ButtonGroup, Stack, Typography} from "@mui/material";
import {DataGrid} from "@mui/x-data-grid";
import {useCallback, useEffect, useState} from "react";
import React from 'react';
import {useTranslation} from 'react-i18next';
import {useLocation, useParams} from "react-router-dom";

import EditSurveyPlatformDialog from "./survey_platform/EditSurveyPlatformDialog";
import SurveyStatus from "./survey_platform/SurveyStatus";
import {GET, PUT} from "../../../code/http_requests";
import {useSnackbar} from "../../../context/SnackbarContext";
import ConnectedStatus from "../../feedback/ConnectedStatus";
import ConnectionBadge from "../../feedback/ConnectionBadge";


const SurveyPlatformIntegration = ({project}) => {

  const {t} = useTranslation();

  const location = useLocation();

  // Use URLSearchParams to parse the query string
  const searchParams = new URLSearchParams(location.search);
  const survey_platform = searchParams.get('survey_platform'); // When redirected after code exchange, open the survey platform integration dialog

  const {projectId} = useParams();

  const {showBottomCenter: showSnackbar} = useSnackbar();

  const [connected, setConnected] = useState(false);
  const [surveyPlatformInfo, setSurveyPlatformInfo] = useState({
    "survey_name": t('ui.project.survey_platform.not_connected'),
  });
  const [surveyPlatformName, setSurveyPlatformName] = useState(project.survey_platform_name);

  const [editFormOpen, setEditFormOpen] = useState(survey_platform !== null);

  const handleSave = useCallback(async (fields) => {
    const response = await PUT(`/projects/${projectId}`, {
      survey_platform_fields: fields
    });

    response.on('2xx', async (status, data) => {
      if (status === 200) {
        showSnackbar(t(data.message.id), 'success');
      }
    });

    response.on('4xx', (_, data) => {
      showSnackbar(t(data.message.id), 'error');
    });

  }, [projectId, showSnackbar, t]);


  const handleCheckConnection = useCallback(async () => {
    setConnected(undefined);
    setSurveyPlatformInfo({
      "survey_name": t('ui.project.survey_platform.loading'),
      "survey_status": "loading",
    });

    const response = await GET(`/projects/${projectId}/survey_platform/check_connection`);

    response.on('2xx', (status, info) => {
      if (status === 200) {
        setConnected(info.connected);
        setSurveyPlatformInfo(info);
      }
    });

    response.on('4xx', () => {
      setConnected(false);
      setSurveyPlatformInfo({
        "survey_name": t('ui.project.survey_platform.not_connected'),
        "survey_status": "unknown",
      });

    });


  }, [projectId, t]);

  const columns = [
    {
      field: 'connected',
      headerName: t('ui.project.survey_platform.grid.column.connected'),
      width: 90,
      renderCell: (params) => {
        return <ConnectedStatus connected={params.value}/>
      }
    },
    {
      field: 'survey_platform_name',
      headerName: t('ui.project.survey_platform.grid.column.survey_platform_name'),
      width: 120,
      disableClickEventBubbling: true,
      renderCell: (params) => <ConnectionBadge size={18} name={params.value}/>
    },
    {
      field: 'survey_name',
      headerName: t('ui.project.survey_platform.grid.column.survey_name'),
      width: 300,
    },
    {
      field: 'survey_status',
      headerName: t('ui.project.survey_platform.grid.column.survey_status'),
      width: 100,
      renderCell: (params) => {
        return <SurveyStatus status={params.value}/>
      }
    },
    // {
    //     field: 'survey_id',
    //     headerName: t('ui.project.survey_platform.grid.column.survey_id'),
    //     width: 250,
    // },
    // {
    //     field: 'survey_platform_api_key',
    //     headerName: t('ui.project.survey_platform.grid.column.survey_platform_api_key'),
    //     width: 380,
    // },
    {
      field: 'actions',
      headerName: t('ui.project.survey_platform.grid.column.actions'),
      width: 180,
      renderCell: () => {
        return (
          <ButtonGroup disableElevation size="small" variant="outlined" aria-label="Survey Platform Actions">
            <Button
              size={"small"}
              startIcon={<EditIcon/>}
              onClick={() => {
                setEditFormOpen(true);
              }}
            >
              {t('ui.project.survey_platform.grid.button.edit')}
            </Button>
            <Button
              variant="outlined"
              size="small"
              startIcon={<SyncIcon/>}
              onClick={() => {
                handleCheckConnection();
              }
              }>
              {t('ui.project.survey_platform.grid.button.check_connection')}
            </Button>
          </ButtonGroup>
        )
      }
    }
  ];

  useEffect(() => {
    setSurveyPlatformName(project.survey_platform_name);
  }, [project, handleCheckConnection]);

  useEffect(() => {
    handleCheckConnection();
  }, [handleCheckConnection, projectId]);

  return (
    <Stack spacing={2}>
      <Typography variant="h6"> {
        t('ui.project.survey_platform.title')
      }</Typography>
      <Stack spacing={2} direction={"row"} alignItems={"flex-end"}>
        <DataGrid
          rows={[{
            ...surveyPlatformInfo,
            id: 1,
            connected: connected,
            survey_platform_name: surveyPlatformName,
          }]}
          columns={columns}
          pageSize={1}
          disableRowSelectionOnClick
          disableColumnSelectionOnClick
          disableColumnFilter
          disableColumnMenu
          disableColumnSelector
          disableVirtualization
          hideFooter
        />
      </Stack>
      <EditSurveyPlatformDialog
        open={editFormOpen}
        surveyPlatformName={project.survey_platform_name}
        surveyPlatformFields={project.survey_platform_fields}
        onClose={() => {
          setEditFormOpen(false);
        }}
        onConfirm={async (fields) => {
          await handleSave(fields);
          await handleCheckConnection();
          setEditFormOpen(false);
        }}
      />
    </Stack>
  );
}

export default SurveyPlatformIntegration;
