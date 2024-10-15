import DeleteForeverOutlinedIcon from '@mui/icons-material/DeleteForeverOutlined';
import FileOpenOutlinedIcon from '@mui/icons-material/FileOpenOutlined';
import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import SettingsIcon from '@mui/icons-material/Settings';
import { Box, Button, IconButton, Menu, Stack, Typography } from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridRowParams,
  GridValueGetterParams,
  MuiEvent,
} from '@mui/x-data-grid';
import React, { JSX, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import { DEL, GET } from '../code/http_requests';
import AuthUser from '../components/auth/AuthUser';
import ConnectionBadge from '../components/feedback/ConnectionBadge';
import { Loading } from '../components/feedback/Loading';
import LayoutMain from '../components/layout/LayoutMain';
import SurveyStatus from '../components/project/survey_platform/SurveyStatus';
import { formatDateToLocale } from '../components/utils/FormatDate';
import { useSnackbar } from '../context/SnackbarContext';
import { API, Models } from '../types';

interface CellActionsProps {
  params: GridRenderCellParams<any, API.Projects.Project>;
  onDelete: (id: string) => void;
}

const CellActions = ({ params, onDelete }: CellActionsProps): JSX.Element => {
  const { t } = useTranslation();

  const navigate = useNavigate();

  const { showBottomCenter: showSnackbar } = useSnackbar();

  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const handleOpenContext = (event: React.MouseEvent<HTMLButtonElement>): void => setAnchorEl(event.currentTarget);
  const handleCloseContext = (): void => setAnchorEl(null);

  return (
    <>
      <IconButton onClick={handleOpenContext}>
        <MoreHorizIcon />
      </IconButton>
      <Menu
        sx={{ mt: '40px' }}
        id="menu-appbar"
        anchorEl={anchorEl}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        keepMounted
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        open={Boolean(anchorEl)}
        onClose={handleCloseContext}
      >
        <Stack padding={1} spacing={2} alignItems={'flex-start'}>
          <Button startIcon={<FileOpenOutlinedIcon />} onClick={() => navigate(`/projects/${params.row.id}`)}>
            {t('ui.project.selection.grid.context.open')}
          </Button>
          <Button
            color={'error'}
            startIcon={<DeleteForeverOutlinedIcon />}
            onClick={async () => {
              const response = await DEL(`/projects/${params.row.id}`);
              response.on('2xx', (status: number, data: API.ResponseData) => {
                if (status === 200) {
                  showSnackbar(t(data.message.id, { defaultValue: data.message.text }), 'success');
                  onDelete(params.row.id);
                  navigate('/projects');
                }
              });
            }}
          >
            {t('ui.project.selection.grid.context.delete')}
          </Button>
        </Stack>
      </Menu>
    </>
  );
};

const PageProjectSelection = (): JSX.Element => {
  const { t } = useTranslation();

  const navigate = useNavigate();

  const { showBottomCenter: showSnackbar } = useSnackbar();

  const [projects, setProjects] = useState<Models.Projects.Project[] | undefined>(undefined);

  const deleteRow = (id: string): void =>
    setProjects(prevProjects => prevProjects?.filter(project => project.id !== id));

  const columns: GridColDef<Models.Projects.Project>[] = [
    {
      field: 'name',
      headerName: t('ui.project.selection.grid.column.name'),
      flex: 1,
      minWidth: 250,
      disableColumnMenu: true,
    },
    {
      field: 'survey_platform_fields',
      headerName: t('ui.project.selection.grid.column.status'),
      width: 150,
      renderCell: (params: GridRenderCellParams<any, Models.Projects.Project>): JSX.Element => {
        return <SurveyStatus status={params.value?.survey_status} />;
      },
    },
    {
      field: 'survey_platform_name',
      headerName: t('ui.project.selection.grid.column.survey_platform_name'),
      minWidth: 150,
      maxWidth: 180,
      renderCell: (params: GridRenderCellParams<any, API.Projects.Project['survey_platform_name']>): JSX.Element => {
        return <ConnectionBadge size={18} name={params.value ?? ''} />;
      },
    },
    {
      field: 'last_modified',
      headerName: t('ui.project.selection.grid.column.last_modified'),
      minWidth: 130,
      maxWidth: 170,
      type: 'date',
      valueGetter: params => new Date(params.value),
      renderCell: (params: GridRenderCellParams<any, API.Projects.Project['last_modified']>): string => {
        const dateValue = params.value ? new Date(params.value) : null;
        return dateValue ? formatDateToLocale(dateValue, { dateStyle: 'short' }) : '';
      },
    },
    {
      field: 'creation_date',
      headerName: t('ui.project.selection.grid.column.creation_date'),
      minWidth: 130,
      maxWidth: 170,
      type: 'date',
      valueGetter: (params: GridValueGetterParams<any, API.Projects.Project['creation_date']>): Date | null => {
        return params.value ? new Date(params.value) : null;
      },
      renderCell: (params: GridRenderCellParams<any, API.Projects.Project['creation_date']>): string => {
        const dateValue = params.value ? new Date(params.value) : null;
        return dateValue ? formatDateToLocale(dateValue, { dateStyle: 'short' }) : '';
      },
    },
    {
      field: 'respondents',
      headerName: t('ui.project.selection.grid.column.num_responses'),
      minWidth: 75,
      maxWidth: 100,
      renderCell: (params: GridRenderCellParams<any, API.Projects.Project['respondents']>) => params.value?.length ?? 0,
      type: 'number',
    },
    {
      field: 'actions',
      headerName: 'actions',
      renderHeader: () => <SettingsIcon sx={{ verticalAlign: 'text-bottom' }} />,
      align: 'center',
      minWidth: 30,
      maxWidth: 40,
      disableColumnMenu: true,
      hideSortIcons: true,
      sortable: false,
      renderCell: (params: GridRenderCellParams<any, API.Projects.Project>): JSX.Element => (
        <div className="action-cell">
          <CellActions params={params} onDelete={deleteRow} />
        </div>
      ),
    },
  ];

  useEffect(() => {
    (async (): Promise<void> => {
      const response = await GET('/projects/');

      response.on('2xx', (_: number, data: Models.Projects.Project[]) => {
        setProjects(data);
      });

      response.on('4xx', (status: number, data: API.ResponseData) => {
        if (status === 401) {
          showSnackbar(t(data.message.id, { defaultValue: data.message.text }), 'error');
        }
      });
    })();
  }, [showSnackbar, t]);

  return (
    <>
      <LayoutMain header={<Typography variant="h4">Project Selection</Typography>} headerRightCorner={<AuthUser />}>
        <Stack spacing={2}>
          <Box>
            <Button variant="contained" color="primary" onClick={() => navigate('/projects/create')}>
              {t('ui.project.selection.button.create')}
            </Button>
          </Box>
          <Loading loading={projects === undefined}>
            {projects && projects?.length > 0 ? (
              <DataGrid
                rows={projects}
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
                onRowClick={(
                  params: GridRowParams<API.Projects.Project>,
                  event: MuiEvent<React.MouseEvent<HTMLElement>>
                ) => {
                  // Check if the click was on a cell in the Action column or an element with the 'action-cell' class
                  // or its child
                  const target = event.target as HTMLElement;
                  if (!(target.dataset.field === 'actions' || target.closest('button, .action-cell'))) {
                    navigate(`/projects/${params.row.id}`);
                  }
                }}
                sx={theme => ({
                  '& .MuiDataGrid-cell:focus': {
                    outline: 'none',
                  },
                  '& .MuiDataGrid-cell:focus-within': {
                    outline: 'none',
                  },
                  '& .MuiDataGrid-row:hover': {
                    cursor: 'pointer',
                  },
                  '& .MuiDataGrid-row:focus': {
                    outline: `solid ${theme.palette.primary.main} 1px`, // Use primary color
                    outlineOffset: '-1px',
                  },
                  '& .MuiDataGrid-row:focus-within': {
                    outline: `solid ${theme.palette.primary.main} 1px`, // Use primary color
                    outlineOffset: '-1px',
                  },
                })}
              />
            ) : (
              <Typography variant="body1">{t('ui.project.selection.no_projects')}</Typography>
            )}
          </Loading>
        </Stack>
      </LayoutMain>
    </>
  );
};

export default React.memo(PageProjectSelection);
