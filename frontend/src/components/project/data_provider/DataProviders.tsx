import AddIcon from '@mui/icons-material/Add';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import EditIcon from '@mui/icons-material/Edit';
import SyncIcon from '@mui/icons-material/Sync';
import { Button, ButtonGroup, Stack, Typography } from '@mui/material';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import React, { JSX, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';

import AddDataProviderDialog from './AddDataProviderDialog';
import EditDataProviderDialog from './EditDataProviderDialog';
import { DEL, GET } from '../../../code/http_requests';
import { useSnackbar } from '../../../context/SnackbarContext';
import { API, Models } from '../../../types';
import ConfirmationDialog from '../../feedback/ConfirmationDialog';
import ConnectedStatus from '../../feedback/ConnectedStatus';
import ConnectionBadge from '../../feedback/ConnectionBadge';

const handleCheckConnection = async (
  projectId: string,
  data_provider_name: string,
  api_key?: string
): Promise<boolean> => {
  const response = await GET(
    `/projects/${projectId}/data-providers/${data_provider_name}/check-connection`,
    api_key ? api_key.length > 0 : true
  );

  return (response as unknown as Response).status === 200;
};

type DataProviderTableGridRenderCellParams = GridRenderCellParams<Models.Projects.DataProvider>;

interface DataProvidersProps {
  project: Models.Projects.Project;
  onChangeDataProviders: CallableFunction;
}

const DataProviders = ({ project, onChangeDataProviders }: DataProvidersProps): JSX.Element => {
  // console.log("DataProviders: project", project)

  const { t } = useTranslation();

  const { showBottomCenter: showSnackbar } = useSnackbar();

  const { projectId } = useParams<{ projectId: string }>();

  const [dataProviders, setDataProviders] = useState<Models.Projects.DataProvider[]>([]);
  const [addDialogOpen, setAddDialogOpen] = useState<boolean>(false);

  const [openEditDataProviderDialog, setOpenEditDataProviderDialog] = useState<boolean>(false);
  const [openDeleteDataProviderDialog, setOpenDeleteDataProviderDialog] = useState<boolean>(false);
  const [selected, setSelected] = useState<Models.Projects.DataProvider | null>(null);

  if (!projectId) {
    throw new Error('projectId should always be defined.');
  }

  useEffect(() => {
    setDataProviders(
      project.data_connections.map(
        (dc: Models.Projects.DataConnection, index: number) =>
          ({
            id: index,
            project_id: dc.project_id,
            connected: undefined,
            name: dc.data_provider.name,
            data_provider_name: dc.data_provider.data_provider_name,
            data_provider_type: dc.data_provider.data_provider_type,
            fields: dc.fields,
          }) as unknown as Models.Projects.DataProvider
      )
    );

    Promise.all(
      project.data_connections.map(async (dc: Models.Projects.DataConnection, index: number) => ({
        id: index,
        project_id: dc.project_id,
        connected: await handleCheckConnection(projectId, dc.data_provider.data_provider_name, dc.api_key),
        name: dc.data_provider.name,
        data_provider_name: dc.data_provider.data_provider_name,
        data_provider_type: dc.data_provider.data_provider_type,
        fields: dc.fields,
        app_required: dc.data_provider.app_required,
      }))
    ).then(newData => setDataProviders(newData as unknown as Models.Projects.DataProvider[]));
  }, [project.data_connections, projectId]);

  const handleDelete = useCallback(() => {
    if (!selected) return;
    (async (): Promise<void> => {
      const response = await DEL(`/projects/${projectId}/data-providers/${selected.data_provider_name}`);

      response.on('2xx', (status: number, data: API.ResponseData) => {
        if (status === 200) {
          showSnackbar(t(data.message.id), 'success');
          setSelected(null);
          onChangeDataProviders();
        }
      });

      response.on('4xx', (_: number, data: API.ResponseData) => {
        showSnackbar(t(data.message.id), 'error');
      });
    })();
  }, [selected, projectId, showSnackbar, t, onChangeDataProviders]);

  const columns: GridColDef<Models.Projects.DataProvider>[] = [
    {
      field: 'connected',
      headerName: t('ui.project.data_providers.grid.column.connected'),
      width: 90,
      renderCell: (params: DataProviderTableGridRenderCellParams): JSX.Element => {
        return <ConnectedStatus connected={params.value} />;
      },
    },
    {
      field: 'name',
      headerName: t('ui.project.data_providers.grid.column.name'),
      width: 200,
      renderCell: (params: DataProviderTableGridRenderCellParams): JSX.Element => (
        <ConnectionBadge size={18} name={params.row.data_provider_name as string} />
      ),
    },
    {
      field: 'actions',
      headerName: t('ui.project.data_providers.grid.column.actions'),
      width: 250,
      align: 'right',
      renderCell: (params: DataProviderTableGridRenderCellParams): JSX.Element => {
        return (
          <ButtonGroup disableElevation size="small" variant="outlined" aria-label="Project Actions">
            {params.row.data_provider_type === 'oauth' && (
              <>
                <Button
                  size={'small'}
                  startIcon={<EditIcon />}
                  onClick={ev => {
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
                  onClick={ev => {
                    ev.stopPropagation();
                    // show the loading icon by setting the connected status to undefined
                    setDataProviders(
                      dataProviders.map(dp =>
                        dp.id === params.row.id
                          ? {
                              ...dp,
                              connected: undefined,
                            }
                          : dp
                      )
                    );
                    (async (): Promise<void> => {
                      const connected = await handleCheckConnection(
                        projectId || '',
                        params.row.data_provider_name || '',
                        params.row.api_key
                      );
                      setDataProviders(
                        dataProviders.map(dp =>
                          dp.id === params.row.id
                            ? {
                                ...dp,
                                connected: connected,
                              }
                            : dp
                        )
                      );
                    })();
                  }}
                >
                  {t('ui.project.data_providers.grid.button.check_connection')}
                </Button>
              </>
            )}

            <Button
              size={'small'}
              color="error"
              startIcon={<DeleteForeverIcon />}
              onClick={ev => {
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
          disableElevation={true}
          variant={'contained'}
          size={'small'}
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setAddDialogOpen(true)}
        >
          {t('ui.project.data_providers.button.add')}
        </Button>
      </Stack>
      {dataProviders.length > 0 ? (
        <DataGrid
          rows={dataProviders}
          columns={columns}
          initialState={{
            pagination: {
              paginationModel: {
                pageSize: 5,
              },
            },
          }}
          pageSizeOptions={[5]}
          disableRowSelectionOnClick
          hideFooter
        />
      ) : (
        <Typography variant="body1">{t('ui.project.data_providers.no_data_providers')}</Typography>
      )}
      <AddDataProviderDialog
        projectId={projectId || ''}
        existingProviders={dataProviders}
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
        projectId={projectId || ''}
        data={selected as Models.Projects.DataProvider}
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
            <Typography variant="body1">{t('ui.project.data_providers.delete.content')}</Typography>
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
