import {Box, Button, IconButton, Stack, Typography, Menu} from "@mui/material"
import Authorization from "../auth/Authorization"
import LayoutMain from "../layout/LayoutMain"

import {DataGrid} from "@mui/x-data-grid";
import {useEffect, useState} from "react";
import {GET, DEL} from "../../code/http_requests";
import {useNavigate} from 'react-router-dom';

// import AddIcon from '@mui/icons-material/Add';
import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import SettingsIcon from '@mui/icons-material/Settings';
import {useSnackbar} from "../../context/SnackbarContext";

import FileOpenOutlinedIcon from '@mui/icons-material/FileOpenOutlined';
import DeleteForeverOutlinedIcon from '@mui/icons-material/DeleteForeverOutlined';
import AuthUser from "../auth/AuthUser";

import {useTranslation} from 'react-i18next';
import Loading from "../feedback/Loading";
import SurveyStatus from "./project/survey_platform/SurveyStatus";
import ConnectionBadge from "../feedback/ConnectionBadge";
import {formatDateStringToLocale} from "../utils/FormatDate";


const CellActions = ({params, onDelete}) => {

  const {t} = useTranslation();

  const navigate = useNavigate();

  const {showBottomCenter: showSnackbar} = useSnackbar();

  const [anchorEl, setAnchorEl] = useState(null);
  const handleOpenContext = (event) => setAnchorEl(event.currentTarget)
  const handleCloseContext = () => setAnchorEl(null)

  return (
    <>
      <IconButton onClick={handleOpenContext}>
        <MoreHorizIcon/>
      </IconButton>
      <Menu
        sx={{mt: '40px'}}
        id="menu-appbar"
        anchorEl={anchorEl}
        anchorOrigin={{vertical: 'top', horizontal: 'right'}}
        keepMounted
        transformOrigin={{vertical: 'top', horizontal: 'right'}}
        open={Boolean(anchorEl)}
        onClose={handleCloseContext}
      >
        <Stack padding={1} spacing={2} alignItems={'flex-start'}>
          <Button startIcon={<FileOpenOutlinedIcon/>} onClick={() => navigate(`/${params.row.id}`)}>
            {t('ui.project.selection.grid.context.open')}
          </Button>
          <Button color={"error"} startIcon={<DeleteForeverOutlinedIcon/>} onClick={
            async () => {
              const response = await DEL(`/projects/${params.row.id}`)

              response.on('2xx', (status, data) => {
                if (status === 200) {
                  showSnackbar(t(data.message.id), 'success');
                  onDelete(params.row.id);
                  navigate('/');
                }
              });
            }
          }>
            {t('ui.project.selection.grid.context.delete')}
          </Button>
        </Stack>

      </Menu>
    </>
  )
}

const PageProjectSelection = () => {

  const {t} = useTranslation();

  const navigate = useNavigate();

  const {showBottomCenter: showSnackbar} = useSnackbar();

  const [projects, setProjects] = useState(undefined);

  const deleteRow = (id) => setProjects(prevProjects => prevProjects.filter(project => project.id !== id));

  const columns = [
    {
      field: 'name',
      headerName: t('ui.project.selection.grid.column.name'),
      flex: 1,
      disableColumnMenu: true
    },
    {
      field: 'survey_platform_fields', headerName: t('ui.project.selection.grid.column.status'), width: 150,
      renderCell: (params) => {
        return <SurveyStatus status={params.value["survey_status"]} />
      }
    },
    {
      field: 'survey_platform_name',
      headerName: t('ui.project.selection.grid.column.survey_platform_name'),
      minWidth: 150,
      maxWidth: 180,
      renderCell: (params) => <ConnectionBadge size={18} name={params.value}/>
    },
    {
      field: 'last_modified',
      headerName: t('ui.project.selection.grid.column.last_modified'),
      minWidth: 130,
      maxWidth: 170,
      type: 'date',
      valueGetter: (params) => new Date(params.value),
      renderCell: (params) => formatDateStringToLocale(new Date(params.value), {dateStyle: "short"})
    },
    {
      field: 'creation_date',
      headerName: t('ui.project.selection.grid.column.creation_date'),
      minWidth: 130,
      maxWidth: 170,
      type: 'date',
      valueGetter: (params) => new Date(params.value),
      renderCell: (params) => formatDateStringToLocale(new Date(params.value), {dateStyle: "short"})
    },
    {
      field: 'respondents',
      headerName: t('ui.project.selection.grid.column.num_responses'),
      minWidth: 75,
      maxWidth: 100,
      renderCell: (params) => params.value?.length ?? 0,
      type: 'number'
    },
    {
      field: 'actions',
      // headerName: t('ui.project.selection.grid.column.actions'),
      headerName: <SettingsIcon/>,
      align: 'center',
      minWidth: 30,
      maxWidth: 40,
      disableColumnMenu: true,
      hideSortIcons: true,
      sortable: false,
      renderCell: (params) => (
        <div className="action-cell">
          <CellActions params={params} onDelete={deleteRow}/>
        </div>
      )
    },
  ];

  useEffect(() => {
    (async () => {
      const response = await GET('/projects/');

      response.on('2xx', (_, data) => {
        setProjects(data);
      });

      response.on('4xx', (status, data) => {
        if (status === 401) {
          showSnackbar(t(data.message.id), 'error');
        }
      });

    })();
  }, [showSnackbar, t]);

  return (
    <Authorization>
      <LayoutMain
        header={
          <Typography variant="h6">Project Selection</Typography>
        }
        headerRightCorner={<AuthUser/>}
      >
        <Stack spacing={2} width={"80%"}>
          <Box>
            <Button
              // startIcon={<AddIcon />}
              variant="contained"
              color="primary"
              onClick={() => navigate('/create')}
            >
              {t('ui.project.selection.button.create')}
            </Button>
          </Box>
          <Loading loading={projects === undefined}>
            {projects?.length > 0 ? (
              <DataGrid
                rows={projects}
                columns={columns}
                pageSize={5}
                rowsPerPageOptions={[5]}
                disableRowSelectionOnClick
                onRowClick={(params, event) => {
                  // Check if the click was on a cell in the Action column or an element with the 'action-cell' class
                  // or its child
                  if (event.target.dataset.field !== "actions" && !event.target.closest('button, .action-cell')) {
                    navigate(`/${params.row.id}`);
                  }
                }}
                sx={(theme) => ({
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
                    'outline-offset': '-1px',
                  },
                  '& .MuiDataGrid-row:focus-within': {
                    outline: `solid ${theme.palette.primary.main} 1px`, // Use primary color
                    'outline-offset': '-1px',
                  },
                })}
              />
            ) : (
              <Typography variant="body1">{
                t('ui.project.selection.no_projects')
              }</Typography>
            )}
          </Loading>

        </Stack>
      </LayoutMain>
    </Authorization>
  )
}

export default PageProjectSelection
