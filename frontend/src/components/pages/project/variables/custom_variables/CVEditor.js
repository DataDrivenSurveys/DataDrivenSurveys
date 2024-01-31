import {useTranslation} from "react-i18next";
import {useSnackbar} from "../../../../../context/SnackbarContext";
import {useCallback, useEffect, useState} from "react";
import {GET} from "../../../../../code/http_requests";
import Logo from "../../../../Logo";
import Loading from "../../../../feedback/Loading";
import {Stack, TextField} from "@mui/material";
import DropDown from "../../../../input/DropDown";
import CVFilters from "./CVFilters";
import CVSelection from "./CVSelection";

const CVEditor = ({project, data: initial, onChange}) => {

  const {t} = useTranslation();

  const {showBottomCenter: showSnackbar} = useSnackbar();

  /* Fetched Data states */
  const [dataProviders, setDataProviders] = useState(null);
  const [dataCategories, setDataCategories] = useState(null);
  const [filterOperators, setFilterOperators] = useState(null);

  const fetchDataCategories = useCallback(async () => {
    const response = await GET(`/data-providers/data-categories`);

    response.on('2xx', (status, data) => {
      if (status === 200) {
        // Filter data categories to keep only data categories that should be used for custom variables
        let dataCategories = [];
        for (let data_category of data) {
          if (data_category.custom_variables_enabled) {
            dataCategories.push(data_category);
          }
        }
        setDataCategories(dataCategories);
      }
    });

    response.on('4xx', (_, data) => {
      showSnackbar(t(data.message.id), 'error');
    });

  }, [showSnackbar, t]);

  const fetchFilterOperators = useCallback(async () => {
    const response = await GET(`/custom-variables/filter-operators`);

    response.on('2xx', (status, data) => {
      if (status === 200) {
        setFilterOperators(data);
      }
    });

    response.on('4xx', (_, data) => {
      showSnackbar(t(data.message.id), 'error');
    });
  }, [showSnackbar, t]);


  useEffect(() => {
    fetchFilterOperators();
    fetchDataCategories();
    setDataProviders(project?.data_connections.map(dc => ({
      label: dc.data_provider.name,
      value: dc.data_provider_type,
      icon: <Logo name={dc.data_provider_type} size={18}/>
    })));
  }, [fetchFilterOperators, fetchDataCategories, project]);

  /* Input States */
  const [variableName, setVariableName] = useState(null);

  const [selectedDataProvider, setSelectedDataProvider] = useState(null);
  const [selectedDataCategory, setSelectedDataCategory] = useState(null);

  const [filters, setFilters] = useState([]);

  const [selection, setSelection] = useState(null);

  const getData = useCallback(() => {
    return {
      variable_name: variableName,
      type: 'Custom',
      data_provider: selectedDataProvider?.value,
      data_category: selectedDataCategory?.value,
      cv_attributes: selectedDataCategory?.cv_attributes,
      filters: filters,
      selection: selection
    }
  }, [variableName, selectedDataProvider, selectedDataCategory, filters, selection]);

  useEffect(() => {
    if (initial) {
      // Set up initial states from the passed data for updating
      setVariableName(initial.variable_name);
      setSelectedDataProvider(dataProviders?.find(dp => dp.value === initial.data_provider));
      setSelectedDataCategory(dataCategories?.find(dc => dc.value === initial.data_category));
      setFilters(initial.filters);
      setSelection(initial.selection);
    }
  }, [initial, dataProviders, dataCategories]);

  return (
    <Loading loading={!dataProviders || !filterOperators} content={t('ui.project.custom_variable.loading')}>
      <Stack spacing={2} width={"100%"} alignItems={"flex-start"}>
        <TextField
          autoFocus
          showClear
          label={t(`ui.project.custom_variable.name.label`) + "*"}
          helperText={t(`ui.project.custom_variable.name.helper_text`)}
          value={variableName}
          onChange={(e) => {
            setVariableName(e.target.value);
            onChange({
              ...getData(),
              variable_name: e.target.value
            });
          }}
        />

        <DropDown
          label={t('ui.project.custom_variable.data_provider.label')}
          items={dataProviders}
          value={selectedDataProvider?.value}
          onChange={(e) => {
            setSelectedDataProvider(dataProviders.find(dp => dp.value === e.target.value));
            onChange({
              ...getData(),
              data_provider: e.target.value,
              data_category: null,
              filters: [],
              selection: null
            });
          }}
        />

        {
          selectedDataProvider && dataCategories &&
          (
            <DropDown
              label={t('ui.project.custom_variable.data_category.label')}
              items={dataCategories.filter(dc => dc.data_provider_type === selectedDataProvider.label)}
              value={selectedDataCategory?.value}
              onChange={(e) => {
                const dc = dataCategories.find(dc => dc.value === e.target.value);
                setSelectedDataCategory(dc);
                onChange({
                  ...getData(),
                  data_category: e.target.value,
                  attributes: dc.attributes,
                  filters: [],
                  selection: null
                });
              }}
            />
          )
        }

        {
          selectedDataCategory &&
          <>
            <CVFilters
              filters={filters}
              dataCategory={selectedDataCategory}
              operators={filterOperators}
              onChange={(filters) => {
                setFilters(filters)
                onChange({
                  ...getData(),
                  filters: filters

                });
              }}
            />
            <CVSelection
              selection={selection}
              dataCategory={selectedDataCategory}
              onChange={(selection) => {
                setSelection(selection)
                onChange({
                  ...getData(),
                  selection: selection
                });
              }}
            />
          </>
        }

      </Stack>

    </Loading>

  )
}

export default CVEditor;
