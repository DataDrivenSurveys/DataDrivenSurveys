import AddIcon from '@mui/icons-material/Add';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import EditIcon from '@mui/icons-material/Edit';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import {
  Button,
  ButtonGroup,
  Checkbox,
  IconButton,
  Stack,
  Tooltip,
  Typography
} from "@mui/material";
import React, {Children, cloneElement, useCallback, useEffect, useMemo, useState} from 'react';
import {useTranslation} from 'react-i18next';
import {useDebouncedCallback} from "use-debounce";

import AddCustomVariableDialog from "./AddCustomVariableDialog";
import EditCustomVariableDialog from "./EditCustomVariableDialog";
import {DEL, PUT} from "../../../../code/http_requests";
import {useSnackbar} from "../../../../context/SnackbarContext";
import ConnectionBadge from "../../../feedback/ConnectionBadge";
import DialogFeedback from "../../../feedback/DialogFeedback";
import ValueInput from "../../../input/ValueInput";
import DataTable from "../../../layout/DataTable";
import addWBR from "../../../utils/addWBR";


function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

const FieldLayout = ({children, isCustomVariable = false}) => {
  // Clones each child and adds the height style
  if (isCustomVariable) {
    return (
      <Stack spacing={1}>
        {
          Children.map(children, child => {
            return cloneElement(child, {style: {height: '55px'}});
          })
        }
      </Stack>
    )
  }

  return (
    <Stack spacing={1}>
      {children}
    </Stack>
  );
};

const FieldCategory = ({row}) => {

  const variable_type = row.type;

  return (
    (
      variable_type === 'Builtin' &&
      <Stack justifyContent="center">
        <Typography variant="body1">{row.category}</Typography>
      </Stack>
    ) || (
      variable_type === 'Custom' &&
      <Stack justifyContent="center">
        <Typography variant="body1">{`${capitalizeFirstLetter(row.data_category)}:\u00A0${row.variable_name}`}</Typography>
      </Stack>
    )
  )
}

const FieldActions = ({row, onEditClick, onDeleteClick, showLabels = true}) => {
  const {t} = useTranslation();

  const variable_type = row.type;

  if (variable_type === 'Builtin') {
    return (
      <FieldLayout>
        <Typography variant="body1">-</Typography>
      </FieldLayout>
    )
  }

  // Case where variable is a Custom Variable
  return (
    <FieldLayout>
      <Stack alignItems={"center"} justifyContent={"center"}>
        <ButtonGroup disableElevation size="small" variant="outlined" aria-label="Project Actions">
          <Button
            size={"small"}
            color="primary"
            startIcon={<EditIcon/>}
            onClick={() => onEditClick(row.id)}
          >
            {showLabels && t("ui.project.custom_variable.button.edit")}
          </Button>
          <Button
            size={"small"}
            color="error"
            startIcon={<DeleteForeverIcon/>}
            onClick={() => onDeleteClick(row.id)}
          >
            {showLabels && t("ui.project.custom_variable.button.delete")}
          </Button>
        </ButtonGroup>
      </Stack>
    </FieldLayout>
  )
}

const FieldVariableName = ({row, onSelect}) => {
  const variable_type = row.type;

  if (variable_type === 'Builtin') {
    return (
      <FieldLayout>
        <Stack justifyContent="center">
          <Typography variant="body1">{addWBR(row.qualified_name)}</Typography>
        </Stack>
      </FieldLayout>
    )
  }

  // Case where variable is a Custom Variable
  return (
    <FieldLayout isCustomVariable={true}>
      {
        row.cv_attributes?.map((attr, index) => (
          <Stack direction="row" alignItems="center" key={index}>
            <Checkbox
              disabled={!row.enabled}
              checked={attr.enabled}
              onChange={(event) => {
                const checked = event.target.checked;
                onSelect && onSelect(index, checked);
              }}
            />
            <Typography variant="body1" key={index}>{`dds.${row.data_provider}.custom.${row.data_category}.${row.variable_name}.${attr.name}`}</Typography>
          </Stack>
        ))
      }
    </FieldLayout>
  )
}

const FieldDescription = ({row}) => {
  const variable_type = row.type;

  if (variable_type === 'Builtin') {
    return (
      <FieldLayout>
        <Stack justifyContent="center">
          <Typography variant="body1">{row.description}</Typography>
        </Stack>
      </FieldLayout>
    )
  }

  // Case where variable is a Custom Variable
  return (
    <FieldLayout isCustomVariable={true}>
      {
        row.cv_attributes?.map((attr, index) => (
          <Stack justifyContent="center" key={index}>
            <Typography variant="body1" key={index}>{attr.description}</Typography>
          </Stack>
        ))
      }
    </FieldLayout>
  )
}

const FieldDataType = ({row}) => {
  const variable_type = row.type;

  if (variable_type === 'Builtin') {
    return (
      <FieldLayout>
        <Stack justifyContent="center">
          <Typography variant="body1">{row.data_type}</Typography>
        </Stack>
      </FieldLayout>
    )
  }

  // Case where variable is a Custom Variable
  return (
    <FieldLayout isCustomVariable={true}>
      {
        row.cv_attributes?.map((attr, index) => (
          <Stack justifyContent="center" key={index}>
            <Typography variant="body1" key={index}>{attr.data_type}</Typography>
          </Stack>
        ))
      }
    </FieldLayout>
  )
}

const FieldTestValue = ({row, onChange}) => {
  const {t} = useTranslation();

  const variable_type = row.type;

  if (variable_type === 'Builtin') {
    return (
      <FieldLayout>
        <Stack justifyContent="center">
          <ValueInput
            label={t('ui.project.variables.grid.column.test_value')}
            data_type={row.data_type}
            value={row.test_value || row.test_value_placeholder}
            unit={row.unit}
            minWidth={100}
            onChange={(value) => onChange(row, null, value)}
          />
        </Stack>
      </FieldLayout>
    )
  }

  // Case where variable is a Custom Variable
  return (
    <FieldLayout>
      {
        row.cv_attributes?.map((attr, index) => (
          <Stack justifyContent="center" key={index}>
            <ValueInput
              label={t('ui.project.variables.grid.column.test_value')}
              data_type={attr.data_type}
              value={attr.test_value || attr.test_value_placeholder}
              unit={attr.unit}
              minWidth={100}
              onChange={(value) => onChange(row, index, value)}
            />
          </Stack>
        ))
      }
    </FieldLayout>
  )
}


const FieldInfo = ({row}) => {
  const variable_type = row.type;

  if (variable_type === 'Builtin') {
    return (
      <FieldLayout>
        <Tooltip title={
          <Typography variant="body1" color="primary.contrastText">
            {row.info}
          </Typography>
        } placement="left-start">
          <IconButton size="small">
            <InfoOutlinedIcon/>
          </IconButton>
        </Tooltip>
      </FieldLayout>
    )
  }

  // Case where variable is a Custom Variable
  return (
    <FieldLayout isCustomVariable={true}>
      {
        row.cv_attributes?.map((attr, index) => (
          <Tooltip
            key={index}
            title={
              <Typography variant="body1" color="primary.contrastText">
                {attr.info}
              </Typography>
            } placement="left-start"
          >
            <IconButton size="small">
              <InfoOutlinedIcon/>
            </IconButton>
          </Tooltip>
        ))
      }
    </FieldLayout>
  )
}


const VariableManagement = ({project, onChangeBuiltinVariables, onChangeCustomVariables}) => {
  const {t} = useTranslation();

  const {showBottomCenter: showSnackbar} = useSnackbar();

  const [openAddCustomVariableDialog, setOpenAddCustomVariableDialog] = useState(false);
  const [openEditCustomVariableDialog, setOpenEditCustomVariableDialog] = useState(false);
  const [openDeleteCustomVariableDialog, setOpenDeleteCustomVariableDialog] = useState(false);

  const [selectedCustomVariableId, setSelectedCustomVariableId] = useState(null);

  const [builtinVariables, setBuiltinVariables] = useState(project.variables || []);
  const [customVariables, setCustomVariables] = useState(project.custom_variables || []);

  useEffect(() => {
    setBuiltinVariables(project.variables || []);
    setCustomVariables(project.custom_variables || []);
  }, [project]);

  const handleSaveBuiltinVariables = useCallback(async (variables) => {
    // update the project variables
    const response = await PUT(`/projects/${project.id}`, {
      variables
    });

    response.on('2xx', (status, data) => {
      if (status === 200) {
        showSnackbar(t(data.message.id), 'success');
      }
    });

    response.on('4xx', (_, data) => {
      showSnackbar(t(data.message.id), 'error');
    });
  }, [project, showSnackbar, t]);

  const handleDeleteCustomVariable = useCallback(async () => {
    const response = await DEL(`/projects/${project.id}/custom-variables/${selectedCustomVariableId}`);

    response.on('2xx', (status, data) => {
      if (status === 200) {
        showSnackbar(t('ui.project.custom_variable.delete.success'), 'success');
        setCustomVariables(data);
      }

    });

    response.on('4xx', (status, data) => {
      showSnackbar(t(data.message.id), 'error');
    });

    response.on('5xx', (status, data) => {
      showSnackbar(t(data.message.id), 'error');
    });

  }, [showSnackbar, t, project.id, selectedCustomVariableId]);

  const handleSaveCustomVariables = useCallback(async (customVariables) => {
    // update the project variables
    const response = await PUT(`/projects/${project.id}`, {
      custom_variables: customVariables
    });

    response.on('2xx', (status, data) => {
      if (status === 200) {
        showSnackbar(t(data.message.id), 'success');
      }
    });

    response.on('4xx', (_, data) => {
      showSnackbar(t(data.message.id), 'error');
    });
  }, [project, showSnackbar, t]);


  const handleRowSelectChange = useCallback(async (id, rows) => {

    const builtinVariables = rows.filter(v => v.type === 'Builtin');
    const customVariables = rows.filter(v => v.type === 'Custom');

    setBuiltinVariables(builtinVariables);
    setCustomVariables(customVariables);

    onChangeBuiltinVariables(builtinVariables);
    onChangeCustomVariables(customVariables);

    await handleSaveBuiltinVariables(builtinVariables);
    await handleSaveCustomVariables(customVariables);
  }, [handleSaveBuiltinVariables, handleSaveCustomVariables, onChangeBuiltinVariables, onChangeCustomVariables]);

  const debouncedSaveBuiltinVariables = useDebouncedCallback(handleSaveBuiltinVariables, 500);
  const debouncedSaveCustomVariables = useDebouncedCallback(handleSaveCustomVariables, 500);

  /**
   * row: the row object
   * index: the index of the attribute in the attributes array (only for custom variables)
   * newValue: the new value of the test value
   */
  const handleTestValueChange = useCallback(async (row, index, newValue) => {

    if (row.type === 'Builtin') {
      const newVariables = builtinVariables.map((v) => {
        if (v.qualified_name === row.qualified_name) {
          return {...v, test_value: newValue};
        }
        return v;
      });
      setBuiltinVariables(newVariables);
      debouncedSaveBuiltinVariables(newVariables);
    } else {
      const newVariables = customVariables.map((v) => {
        if (v.variable_name === row.variable_name) {
          const newAttributes = v.cv_attributes.map((attr, i) => {
            if (i === index) {
              return {...attr, test_value: newValue};
            }
            return attr;
          });
          return {...v, cv_attributes: newAttributes};
        }
        return v;
      });
      setCustomVariables(newVariables);
      debouncedSaveCustomVariables(newVariables);
    }
  }, [builtinVariables, debouncedSaveBuiltinVariables, customVariables, debouncedSaveCustomVariables]);


  const columns = [
    {
      field: 'data_provider',
      headerName: t('ui.project.variables.grid.column.data_provider'),
      // minWidth: 90,
      renderCell: (row) => <ConnectionBadge size={18} name={row.data_provider}/>,
      sxTableHeaderCell: {minWidth: 90},
      sxTableBodyCell: {minWidth: 90},
    },
    {
      field: 'category',
      headerName: t('ui.project.variables.grid.column.category'),
      minWidth: 100,
      renderCell: (row) => <FieldCategory row={row}/>,
      sxTableHeaderCell: {minWidth: 100},
      sxTableBodyCell: {minWidth: 100},
    },
    {field: 'type', headerName: t('ui.project.variables.grid.column.variable_nature'), minWidth: 100},
    {
      field: 'actions',
      headerName: t('ui.project.variables.grid.column.actions'),
      type: 'actions',
      sortable: false,
      // minWidth: 90,
      disableClickEventBubbling: true,
      renderCell: (row) =>
        <FieldActions
          row={row}
          onEditClick={
            (id) => {
              setSelectedCustomVariableId(id);
              setOpenEditCustomVariableDialog(true);
            }
          }
          onDeleteClick={
            (id) => {
              setSelectedCustomVariableId(id);
              setOpenDeleteCustomVariableDialog(true);
            }
          }
          showLabels={true}
        />,
      sxTableHeaderCell: {minWidth: 90},
      sxTableBodyCell: {minWidth: 90},
    },
    {
      field: 'name',
      headerName: t('ui.project.variables.grid.column.variable_name'),
      // minWidth: 150,
      renderCell: (row) =>
        <FieldVariableName
          row={row}
          onSelect={(index, checked) => {
            if (row.type === 'Custom') {
              const newVariables = customVariables.map((v) => {
                if (v.variable_name === row.variable_name) {
                  v.cv_attributes[index].enabled = checked;
                }
                return v;
              });
              setCustomVariables(newVariables);
              debouncedSaveCustomVariables(newVariables);
            }
          }}
        />,
      // sxTableHeaderCell: {minWidth: 150},
      // sxTableBodyCell: {minWidth: 150},
      sxTableHeaderCell: {flex: 2},
      sxTableBodyCell: {flex: 2},
    },
    {
      field: 'description',
      headerName: t('ui.project.variables.grid.column.description'),
      // minWidth: 150,
      renderCell: (row) => <FieldDescription row={row}/>,
      // sxTableHeaderCell: {minWidth: 150},
      // sxTableBodyCell: {minWidth: 150, overflowWrap: 'break-word'},
      sxTableHeaderCell: {minWidth: 150, flex: 3},
      sxTableBodyCell: {minWidth: 150, flex: 3, overflowWrap: 'break-word'},
    },
    {
      field: 'data_type',
      headerName: t('ui.project.variables.grid.column.type'),
      // minWidth: 100,
      renderCell: (row) => <FieldDataType row={row}/>,
      sxTableHeaderCell: {minWidth: 70, maxWidth: 75},
      sxTableBodyCell: {minWidth: 70, maxWidth: 75},
    },
    {
      field: 'test_value',
      headerName: t('ui.project.variables.grid.column.test_value'),
      // minWidth: 150,
      editable: true,
      renderCell: (row) => {
        return <FieldTestValue
          row={row}
          onChange={handleTestValueChange}
        />
      },
      sxTableHeaderCell: {minWidth: 150},
      sxTableBodyCell: {minWidth: 150},
    },
    {
      field: 'info',
      headerName: t('ui.project.variables.grid.column.info'),
      // minWidth: 40,
      // maxWidth: 60,
      sortable: false,
      renderCell: (row) => <FieldInfo row={row}/>,
      sxTableHeaderCell: {minWidth: 35, maxWidth: 50},
      sxTableBodyCell: {minWidth: 35, maxWidth: 50},
    },

  ];

  const gridVariables = useMemo(() => [...builtinVariables, ...customVariables].map((v, index) => ({
    id: index,
    ...v
  })), [builtinVariables, customVariables]);

  return (
    <Stack spacing={2}>
      <Stack direction="row" alignItems="center" spacing={2} justifyContent={"space-between"} width={"100%"}>
        <Typography variant="h6">{t('ui.project.variables.title')}</Typography>
        <Button
          disableElevation={true}
          variant={"contained"}
          size={"small"}
          color="primary"
          startIcon={<AddIcon/>}
          onClick={() => setOpenAddCustomVariableDialog(true)}
          disabled={!gridVariables.length}
        >
          {t('ui.project.variables.button.add_custom_variable')}
        </Button>
      </Stack>
      {
        !gridVariables.length ?
          <Typography variant="body1">
            {t('ui.project.variables.missing_data_providers_info')}
          </Typography>
          :
          <DataTable
            rows={gridVariables}
            columns={columns}
            selectable={true}
            selectableLabel={t('ui.project.variables.grid.column.enabled')}
            selectableField='enabled'
            onRowSelectChange={handleRowSelectChange}
          />
      }
      <AddCustomVariableDialog
        project={project}
        open={openAddCustomVariableDialog}
        onClose={() => setOpenAddCustomVariableDialog(false)}
        onAdd={(newVariables) => {
          setCustomVariables(newVariables);
          setOpenAddCustomVariableDialog(false);
        }}
      />
      <EditCustomVariableDialog
        project={project}
        customVariableId={selectedCustomVariableId}
        open={openEditCustomVariableDialog}
        onClose={() => setOpenEditCustomVariableDialog(false)}
        onEdit={(newVariables) => {
          setCustomVariables(newVariables);
          setOpenEditCustomVariableDialog(false);
        }}
      />
      <DialogFeedback
        open={openDeleteCustomVariableDialog}
        title={t('ui.project.custom_variable.delete.title')}
        content={
          <Stack spacing={2}>
            <Typography variant="body1">
              {t('ui.project.custom_variable.delete.content')}
            </Typography>
          </Stack>
        }
        onClose={() => setOpenDeleteCustomVariableDialog(false)}
        onConfirm={handleDeleteCustomVariable}
        confirmProps={{color: 'error'}}
        confirmText={t('ui.dialog.delete')}
      />

    </Stack>
  )
}


export default VariableManagement;
