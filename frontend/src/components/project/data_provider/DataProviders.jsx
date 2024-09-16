import AddIcon from '@mui/icons-material/Add';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import EditIcon from '@mui/icons-material/Edit';
import SyncIcon from '@mui/icons-material/Sync';
import { Button, ButtonGroup, Stack, Typography } from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import React, { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';

import AddDataProviderDialog from './AddDataProviderDialog';
import EditDataProviderDialog from './EditDataProviderDialog';
import { DEL, GET } from '../../../code/http_requests';
import { useSnackbar } from '../../../context/SnackbarContext';
import ConfirmationDialog from '../../feedback/ConfirmationDialog';
import ConnectedStatus from '../../feedback/ConnectedStatus';
import ConnectionBadge from '../../feedback/ConnectionBadge';


const handleCheckConnection = async (projectId, data_provider_name, api_key) => {
  const response = await GET(`/projects/${projectId}/data-providers/${data_provider_name}/check-connection`, {
    api_key,
  });

  return response.status === 200;
};

const DataProviders = ({ project, onChangeDataProviders }) => {

  // console.log("DataProviders: project", project)

  const { t } = useTranslation();

  const { showBottomCenter: showSnackbar } = useSnackbar();

  const { projectId } = useParams();

  const [dataProviders, setDataProviders] = useState([]);
  const [addDialogOpen, setAddDialogOpen] = useState(false);

  const [openEditDataProviderDialog, setOpenEditDataProviderDialog] = useState(false);
  const [openDeleteDataProviderDialog, setOpenDeleteDataProviderDialog] = useState(false);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    setDataProviders(project.data_connections.map((dc, index) => ({
      id: index,
      project_id: dc.project_id,
      connected: undefined,
      name: dc.data_provider.name,
      data_provider_name: dc.data_provider.data_provider_name,
      data_provider_type: dc.data_provider.data_provider_type,
      fields: dc.fields,
    })));

    Promise.all(project.data_connections.map(async (dc, index) => ({
      id: index,
      project_id: dc.project_id,
      connected: await handleCheckConnection(projectId, dc.data_provider.data_provider_name, dc.api_key),
      name: dc.data_provider.name,
      data_provider_name: dc.data_provider.data_provider_name,
      data_provider_type: dc.data_provider.data_provider_type,
      fields: dc.fields,
      app_required: dc.data_provider.app_required,
    }))).then(newData => setDataProviders(newData));

  }, [project.data_connections, projectId]);

  const handleDelete = useCallback(() => {
    if (!selected) return;
    (async () => {
      const response = await DEL(`/projects/${projectId}/data-providers/${selected.data_provider_name}`);

      response.on('2xx', (status, data) => {
        if (status === 200) {
          showSnackbar(t(data.message.id), 'success');
          setSelected(null);
          onChangeDataProviders();
        }
      });

      response.on('4xx', (_, data) => {
        showSnackbar(t(data.message.id), 'error');
      });
    })();
  }, [selected, projectId, showSnackbar, t, onChangeDataProviders]);

  const columns = [
    {
      field: 'connected',
      headerName: t('ui.project.data_providers.grid.column.connected'),
      width: 90,
      renderCell: (params) => {
        return <ConnectedStatus connected={params.value} />;
      },
    },
    {
      field: 'name',
      headerName: t('ui.project.data_providers.grid.column.name'),
      width: 200,
      renderCell: (params) => <ConnectionBadge size={18} name={params.row.data_provider_name} />,
    },
    {
      field: 'actions',
      headerName: t('ui.project.data_providers.grid.column.actions'),
      width: 250,
      align: 'right',
      renderCell: (params) => {

        return (
          <ButtonGroup disableElevation size="small" variant="outlined" aria-label="Project Actions">
            {
              params.row.data_provider_type === 'oauth' && (
                <>
                  <Button
                    size={'small'}
                    startIcon={<EditIcon />}
                    onClick={(ev) => {
                      ev.stopPropagation();
                      setSelected(params.row);
                      setOpenEditDataProviderDialog(true);
                    }}
                  >
                    {t('ui.project.data_providers.grid.button.edit')}
                  </Button>
                  <Button
                    size={'small'}
                    startIcon={<SyncIcon />}
                    onClick={(ev) => {
                      ev.stopPropagation();
                      // set the connected status to undefined to show the loading icon
                      setDataProviders(dataProviders.map(dp => dp.id === params.row.id ? {
                        ...dp,
                        connected: undefined,
                      } : dp));
                      (async () => {
                        const connected = await handleCheckConnection(projectId, params.row.data_provider_name, params.row.api_key);
                        setDataProviders(dataProviders.map(dp => dp.id === params.row.id ? {
                          ...dp,
                          connected: connected,
                        } : dp));
                      })();
                    }}
                  >
                    {t('ui.project.data_providers.grid.button.check_connection')}
                  </Button>
                </>
              )
            }

            <Button
              size={'small'}
              color="error"
              startIcon={<DeleteForeverIcon />}
              onClick={(ev) => {
                ev.stopPropagation();
                setSelected(params.row);
                setOpenDeleteDataProviderDialog(true);
              }}
            >
              {t('ui.project.data_providers.grid.button.delete')}
            </Button>

          </ButtonGroup>
        );
      },
    },
  ];

  // console.log("DataProviders: dataProviders", dataProviders);

  return (
    <Stack spacing={2} alignItems={'flex-start'}>
      <Stack direction="row" alignItems="center" spacing={2} justifyContent={'space-between'} width={'100%'}>
        <Typography variant="h6">{t('ui.project.data_providers.title')} </Typography>
        <Button
          disableElevation={'true'}
          variant={'contained'}
          size={'small'}
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setAddDialogOpen(true)}>
          {t('ui.project.data_providers.button.add')}
        </Button>
      </Stack>
      {dataProviders.length > 0 ? (
        <DataGrid
          rows={dataProviders}
          columns={columns}
          pageSize={5}
          rowsPerPageOptions={[5]}
          disableRowSelectionOnClick
          hideFooter
        />
      ) : (
        <Typography variant="body1">
          {t('ui.project.data_providers.no_data_providers')}
        </Typography>
      )}
      <AddDataProviderDialog
        projectId={projectId}
        exitingProviders={dataProviders}
        open={addDialogOpen}
        onClose={() => {
          setAddDialogOpen(false);
        }}
        onAdd={() => {
          setAddDialogOpen(false);
          onChangeDataProviders();
        }}
        projectName={project.name}
      />

      <EditDataProviderDialog
        projectId={projectId}
        data={selected}
        open={openEditDataProviderDialog}
        onClose={() => {
          setSelected(null);
          setOpenEditDataProviderDialog(false);
        }}
        onEdit={() => {
          setSelected(null);
          onChangeDataProviders();
        }}
      />

      <ConfirmationDialog
        open={openDeleteDataProviderDialog}
        title={t('ui.project.data_providers.delete.title')}
        content={
          <Stack spacing={2}>
            <Typography variant="body1">
              {t('ui.project.data_providers.delete.content')}
            </Typography>
          </Stack>
        }
        onClose={() => setOpenDeleteDataProviderDialog(false)}
        onConfirm={handleDelete}
        confirmProps={{ color: 'error' }}
        confirmText={t('ui.dialog.delete')}
      />
    </Stack>
  );
};

export default DataProviders;
