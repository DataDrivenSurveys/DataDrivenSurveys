import AddIcon from '@mui/icons-material/Add';
import AddLinkIcon from '@mui/icons-material/AddLink';
import {Stack, Typography, Button} from "@mui/material"
import {useCallback, useEffect, useState} from "react";
import React from "react";
import {useTranslation} from 'react-i18next';
import {useNavigate} from 'react-router-dom';

import {GET, POST} from "../../code/http_requests";
import {useSnackbar} from "../../context/SnackbarContext";
import useInput from "../../hook/useInput";
import Authorization from "../auth/Authorization"
import AuthUser from "../auth/AuthUser";
import ConnectionBadge from "../feedback/ConnectionBadge";
import Loading from "../feedback/Loading";
import DropDown from "../input/DropDown";
import TextInput from "../input/TextInput";
import LayoutMain from "../layout/LayoutMain"
import SurveyPlatformFields from "./project/survey_platform/SurveyPlatformFields";

const creationTypes = [
  {label: 'ui.project.create.select.type.from_scratch', value: "from_scratch", icon: <AddIcon/>},
  {label: 'ui.project.create.select.type.from_existing_survey', value: "from_existing", icon: <AddLinkIcon/>},
];

const hiddenFieldsFromScratch = ['survey_id'];


// Helper functions for local storage
const saveToLocalStorage = (key, value) => {
  // Check if value is an object (JSON field)
  if(value){
    if (typeof value === 'object') {
      localStorage.setItem(key, JSON.stringify(value));
    } else {
      // Handle simple value fields
      localStorage.setItem(key, value);
    }
  }
};

const getFromLocalStorage = (key, defaultValue) => {
  const storedValue = localStorage.getItem(key);
  if (storedValue !== null) {
    try {
      // Try to parse as JSON
      return JSON.parse(storedValue);
    } catch (e) {
      // Return as simple value if JSON.parse fails
      return storedValue;
    }
  }
  return defaultValue;
};

const PageCreateProject = () => {

  const {t} = useTranslation();

  const navigate = useNavigate();

  const {showBottomCenter: showSnackbar} = useSnackbar();

  const creationTypesUI = creationTypes.map((creationType) => ({...creationType, label: t(creationType.label)}));

  const [creating, setCreating] = useState(false);

  const [creationMode, setCreationMode] = useState(getFromLocalStorage('creationMode', creationTypesUI[0].value));

  const [ surveyPlatforms, setSurveyPlatforms ] = useState([]);

  const [ selectedSurveyPlatform, setSelectedSurveyPlatform] = useState();
  const [ surveyPlatformFields, setSurveyPlatformFields ] = useState();


  useEffect(() => {
    (async () => {
      const response = await GET('/survey-platforms');
      response.on('2xx', (status, data) => {
        const platforms = data.map((si) => ({...si, label: undefined, icon: <ConnectionBadge name={si.value} />}));

        setSurveyPlatforms(platforms);
        // Moved the state updates for selectedSurveyPlatform and surveyPlatformFields here
        // to avoid the dependency on surveyPlatforms in another useEffect
        const defaultPlatform = platforms[0] || {};

        setSelectedSurveyPlatform(getFromLocalStorage('selectedSurveyPlatform', defaultPlatform));
        setSurveyPlatformFields(getFromLocalStorage('surveyPlatformFields', defaultPlatform.fields || []));
      });
    })();
  }, []);

  const {bind: bindName, value: name, error: errorName} = useInput({
    label: t('ui.project.create.field.project_name.label'),
    value: getFromLocalStorage('projectName', ''),
    minLength: 3,
    maxLength: 50,
    required: creationMode === "from_scratch",
    helperText: creationMode === "from_existing" ? t('ui.project.create.field.project_name.helper_text') : ''
  });

  // Save to local storage when state changes
  useEffect(() => saveToLocalStorage('projectName', name), [name]);
  useEffect(() => saveToLocalStorage('creationMode', creationMode), [creationMode]);
  useEffect(() => saveToLocalStorage('selectedSurveyPlatform', selectedSurveyPlatform), [selectedSurveyPlatform]);

  // Hide fields that are not required when creating from scratch
  const shouldHideField = useCallback((fieldName) => creationMode === "from_scratch" && hiddenFieldsFromScratch.includes(fieldName), [creationMode]);

  const checkInputs = useCallback(() => {

      if (creationMode === "from_scratch" && !name) {
          return false;
      }
      for (let field of surveyPlatformFields.filter(f => f.type !== "button")) {
          // If the field is hidden, skip validation for it
          if (shouldHideField(field.name)) {
              continue;
          }

          if (field.required && !field.value) {
              return false;
          }
      }

      return true;
  }, [surveyPlatformFields, shouldHideField, creationMode, name]);

  const onCreateClick = useCallback(async () => {
    if ([errorName].some((error) => error === true) || !checkInputs()) {
      showSnackbar(t('ui.project.create.error.missing_fields'), 'error');
      return;
    }

    setCreating(true);
    const response = await POST('/projects/', {
      name: name,
      survey_platform_name: selectedSurveyPlatform.value,
      fields: surveyPlatformFields.map((field) => ({name: field.name, value: field.value})),
      use_existing_survey: creationMode === "from_existing"
    });
    setCreating(false);

    response.on('2xx', (status, data) => {
      if (status === 201) {
        showSnackbar(t(data.message.id), 'success');
        navigate(`/projects/${data.entity.id}`)
        // remove all fields from local storage
        localStorage.removeItem('projectName');
        localStorage.removeItem('creationMode');
        localStorage.removeItem('selectedSurveyPlatform');
        localStorage.removeItem('surveyPlatformFields');

      }
    });

    response.on('4xx', (_, data) => {
      showSnackbar(t(data.message.id), 'error');
    });
  }, [name, checkInputs, selectedSurveyPlatform, surveyPlatformFields, creationMode, errorName, showSnackbar, navigate, t]);

  return (

    <Authorization>
      <Loading loading={surveyPlatforms.length === 0}>
      <LayoutMain
        backUrl="/projects"
        headerRightCorner={<AuthUser/>}
        header={
          <Typography variant="h6">
            {t('ui.project.create.title')}
          </Typography>
        }
      >
        {

        selectedSurveyPlatform && (
          <Stack spacing={4} width={"400px"}>
          <DropDown
            items={creationTypesUI}
            label={t('ui.project.create.select.type.label')}
            value={creationMode}
            onChange={(e) => setCreationMode(e.target.value)}
          />

          <TextInput
            showClear
            {...bindName}
          />

          <DropDown
            items={surveyPlatforms}
            label={t('ui.project.create.select.survey_platform.label')}
            value={selectedSurveyPlatform.value}
            onChange={(e) => {
              const surveyPlatform = surveyPlatforms.find((platform) => platform.value === e.target.value);
              setSelectedSurveyPlatform(surveyPlatform)
              setSurveyPlatformFields(surveyPlatform.fields);
            }}
          />

          <SurveyPlatformFields
            selectedSurveyPlatform={selectedSurveyPlatform}
            surveyPlatformFields={surveyPlatformFields?.map(field => ({
              ...field,
              required: !shouldHideField(field.name),

            }))}
            hiddenFields={creationMode === "from_scratch" ? hiddenFieldsFromScratch : []}
            onChange={setSurveyPlatformFields}
          />

          <Button
            variant="contained"
            color="primary"
            size={"large"}
            disabled={!checkInputs() || creating}
            startIcon={
              creationMode ? <AddLinkIcon/> : <AddIcon/>
            }
            onClick={onCreateClick}
          >
            {t('ui.project.create.button.create')}
          </Button>

        </Stack>
        )}

      </LayoutMain>
      </Loading>
    </Authorization>

  )
}

export default PageCreateProject
