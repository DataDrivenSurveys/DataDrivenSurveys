import { Stack } from '@mui/material';
import React, { Dispatch, JSX, SetStateAction, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';

import SurveyPlatformFields from './SurveyPlatformFields';
import { GET } from '../../../code/http_requests';
import { useSnackbar } from '../../../context/SnackbarContext';
import { API } from '../../../types';
import ConfirmationDialog from '../../feedback/ConfirmationDialog';
import { Loading } from '../../feedback/Loading';
import { Field } from '../../input/FormFields';
import { getNonParamURL } from '../../utils/getURL';

interface EditSurveyPlatformDialogProps {
  open: boolean;
  surveyPlatformName: string;
  initialFields: API.Projects.SurveyPlatformFields;
  onClose: () => void;
  onConfirm: (fields: API.Projects.SurveyPlatformFields) => Promise<void>;
}

const EditSurveyPlatformDialog = ({
  open,
  surveyPlatformName,
  initialFields,
  onClose,
  onConfirm,
}: EditSurveyPlatformDialogProps): JSX.Element => {
  const { t } = useTranslation();

  const location = useLocation();
  const navigate = useNavigate();

  const { showBottomCenter: showSnackbar } = useSnackbar();

  const [surveyPlatforms, setSurveyPlatforms] = useState<API.SurveyPlatforms.SurveyPlatform[]>([]);
  const [selectedSurveyPlatform, setSelectedSurveyPlatform] = useState<API.SurveyPlatforms.SurveyPlatform>(
    {} as API.SurveyPlatforms.SurveyPlatform
  );
  const [surveyPlatformFields, setSurveyPlatformFields] = useState<API.SurveyPlatforms.SurveyPlatformField[]>([]);

  useEffect(() => {
    (async (): Promise<void> => {
      const response = await GET('/survey-platforms');

      response.on('2xx', (_: number, data: API.SurveyPlatforms.SurveyPlatform[]) => {
        setSurveyPlatforms(data);

        const theOne: API.SurveyPlatforms.SurveyPlatform =
          data.find(sp => sp.value === surveyPlatformName) || ({} as API.SurveyPlatforms.SurveyPlatform);
        setSelectedSurveyPlatform(theOne);
        setSurveyPlatformFields(
          theOne.fields.map(field => ({
            ...field,
            value: initialFields[field.name as keyof API.Projects.SurveyPlatformFields] || '',
          }))
        );
      });
    })();
  }, [surveyPlatformName, initialFields]);

  const checkInputs = useCallback(() => surveyPlatformFields.every(f => f.value), [surveyPlatformFields]);

  const handleConfirm = useCallback(() => {
    if (!selectedSurveyPlatform) return;
    if (surveyPlatformFields.some(f => f.required && !f.value)) {
      showSnackbar(t('ui.project.survey_platform.add.error.missing_fields'), 'error');
      return;
    }

    const fields: API.Projects.SurveyPlatformFields = surveyPlatformFields.reduce((acc, field) => {
      return { ...acc, [field.name]: field.value };
    }, {} as API.Projects.SurveyPlatformFields);
    localStorage.removeItem('surveyPlatformFields');
    onConfirm(fields);
    // redirect to the same url without the survey_platform and access_token query params
    const url = getNonParamURL(location.pathname);
    navigate(url);
  }, [selectedSurveyPlatform, surveyPlatformFields, showSnackbar, t, onConfirm, location, navigate]);

  return (
    <Loading loading={surveyPlatforms.length === 0}>
      <ConfirmationDialog
        open={open}
        title={t('ui.project.survey_platform.edit.title')}
        disableConfirm={!checkInputs()}
        content={
          <Stack spacing={2} pt={1} width={'450px'}>
            <SurveyPlatformFields
              selectedSurveyPlatform={selectedSurveyPlatform}
              surveyPlatformFields={surveyPlatformFields as unknown as Field[]}
              // initialData={surveyPlatformFields}
              onChange={setSurveyPlatformFields as unknown as Dispatch<SetStateAction<Field[]>>}
            />
          </Stack>
        }
        onClose={onClose}
        onConfirm={handleConfirm}
        confirmProps={{ variant: 'contained', disableElevation: true }}
      />
    </Loading>
  );
};

export default EditSurveyPlatformDialog;
