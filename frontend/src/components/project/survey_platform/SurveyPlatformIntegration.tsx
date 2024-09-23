import EditIcon from '@mui/icons-material/Edit';
import SyncIcon from '@mui/icons-material/Sync';
import { Button, ButtonGroup, Stack } from '@mui/material';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import React, { JSX, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useParams } from 'react-router-dom';

import EditSurveyPlatformDialog from './EditSurveyPlatformDialog';
import SurveyStatus from './SurveyStatus';
import { GET, PUT } from '../../../code/http_requests';
import { useSnackbar } from '../../../context/SnackbarContext';
import { API, Shared } from '../../../types';
import ConnectedStatus from '../../feedback/ConnectedStatus';
import ConnectionBadge from '../../feedback/ConnectionBadge';

interface SurveyPlatformInformation {
  connected?: boolean;
  active?: boolean;
  exists?: boolean;
  survey_name: string;
  survey_status?: Shared.SurveyStatus;
  survey_platform_name?: string;
  id?: number | null;
}

type SurveyPlatformIntegrationGridRenderCellParams = GridRenderCellParams<SurveyPlatformInformation>;

interface SurveyPlatformIntegrationProps {
  project: API.Projects.Project;
}

const SurveyPlatformIntegration = ({ project }: SurveyPlatformIntegrationProps): JSX.Element => {
  const { t } = useTranslation();

  const location = useLocation();

  // Use URLSearchParams to parse the query string
  const searchParams = new URLSearchParams(location.search);

  // When redirected after code exchange, open the survey platform integration dialog
  const survey_platform = searchParams.get('survey_platform');

  const { projectId } = useParams<{ projectId: string }>();

  const { showBottomCenter: showSnackbar } = useSnackbar();

  const [connected, setConnected] = useState<boolean>(false);
  const [surveyPlatformInfo, setSurveyPlatformInfo] = useState<SurveyPlatformInformation>({
    survey_name: t('ui.project.survey_platform.not_connected'),
  });
  const [surveyPlatformName, setSurveyPlatformName] = useState<string>(project.survey_platform_name);

  const [editFormOpen, setEditFormOpen] = useState<boolean>(survey_platform !== null);

  const handleSave = useCallback(
    async (fields: API.Projects.SurveyPlatformFields): Promise<void> => {
      const response = await PUT(`/projects/${projectId}`, {
        survey_platform_fields: fields,
      });

      response.on('2xx', async (status: number, data: API.ResponseData) => {
        if (status === 200) {
          showSnackbar(t(data.message.id), 'success');
        }
      });

      response.on('4xx', (_: number, data: API.ResponseData) => {
        showSnackbar(t(data.message.id), 'error');
      });
    },
    [projectId, showSnackbar, t]
  );

  const handleCheckConnection = useCallback(async () => {
    setConnected(false);
    setSurveyPlatformInfo({
      survey_name: t('ui.project.survey_platform.loading'),
      survey_status: 'loading',
    });

    const response = await GET(`/projects/${projectId}/survey_platform/check_connection`);

    response.on('2xx', (status: number, info: API.Projects.SurveyPlatformCheckConnectionSuccess) => {
      if (status === 200) {
        setConnected(info.connected);
        setSurveyPlatformInfo(info);
      }
    });

    response.on('4xx', () => {
      setConnected(false);
      setSurveyPlatformInfo({
        survey_name: t('ui.project.survey_platform.not_connected'),
        survey_status: 'unknown',
      });
    });
  }, [projectId, t]);

  const columns: GridColDef<SurveyPlatformInformation>[] = [
    {
      field: 'connected',
      headerName: t('ui.project.survey_platform.grid.column.connected'),
      width: 90,
      renderCell: (params: SurveyPlatformIntegrationGridRenderCellParams): JSX.Element => {
        return <ConnectedStatus connected={params.value} />;
      },
    },
    {
      field: 'survey_platform_name',
      headerName: t('ui.project.survey_platform.grid.column.survey_platform_name'),
      width: 120,
      renderCell: (params: SurveyPlatformIntegrationGridRenderCellParams): JSX.Element => (
        <ConnectionBadge size={18} name={params.value} />
      ),
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
      renderCell: (params: SurveyPlatformIntegrationGridRenderCellParams): JSX.Element => {
        return <SurveyStatus status={params.value} />;
      },
    },
    {
      field: 'actions',
      headerName: t('ui.project.survey_platform.grid.column.actions'),
      width: 180,
      renderCell: (): JSX.Element => {
        return (
          <ButtonGroup disableElevation size="small" variant="outlined" aria-label="Survey Platform Actions">
            <Button
              size={'small'}
              startIcon={<EditIcon />}
              onClick={() => {
                setEditFormOpen(true);
              }}
            >
              {t('ui.project.survey_platform.grid.button.edit')}
            </Button>
            <Button
              variant="outlined"
              size="small"
              startIcon={<SyncIcon />}
              onClick={() => {
                handleCheckConnection();
              }}
            >
              {t('ui.project.survey_platform.grid.button.check_connection')}
            </Button>
          </ButtonGroup>
        );
      },
    },
  ];

  useEffect(() => {
    setSurveyPlatformName(project.survey_platform_name);
  }, [project, handleCheckConnection]);

  useEffect(() => {
    handleCheckConnection();
  }, [handleCheckConnection, projectId]);

  return (
    <>
      <Stack spacing={2} direction={'row'} alignItems={'flex-end'}>
        <DataGrid
          rows={[
            {
              ...surveyPlatformInfo,
              id: 1,
              connected: connected,
              survey_platform_name: surveyPlatformName,
            },
          ]}
          columns={columns}
          pageSizeOptions={[1]}
          disableRowSelectionOnClick
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
        initialFields={project.survey_platform_fields}
        onClose={() => {
          setEditFormOpen(false);
        }}
        onConfirm={async (fields: API.Projects.SurveyPlatformFields): Promise<void> => {
          await handleSave(fields);
          await handleCheckConnection();
          setEditFormOpen(false);
        }}
      />
    </>
  );
};

export default SurveyPlatformIntegration;
