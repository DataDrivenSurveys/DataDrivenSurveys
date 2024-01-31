import { useSnackbar } from "../../../../context/SnackbarContext";
import { useCallback, useEffect, useState } from "react";
import DialogModal from "../../../layout/DialogModal";
import { Stack } from "@mui/material";

import { useTranslation } from 'react-i18next';

import { GET } from "../../../../code/http_requests";
import Loading from "../../../feedback/Loading";
import SurveyPlatformFields from "./SurveyPlatformFields";
import { useLocation, useNavigate } from "react-router-dom";
import { getNonParamURL } from "../../../utils/getURL";

const EditSurveyPlatformDialog = ({ open, surveyPlatformName, surveyPlatformFields:initialFields, onClose, onConfirm }) => {

    const { t } = useTranslation();

    const location = useLocation();
    const navigate = useNavigate();

    const { showBottomCenter: showSnackbar } = useSnackbar();

    const [ surveyPlatforms, setSurveyPlatforms ] = useState([]);
    const [ selectedSurveyPlatform, setSelectedSurveyPlatform] = useState(undefined);
    const [ surveyPlatformFields, setSurveyPlatformFields ] = useState([]);
    
    useEffect(() => {
        (async () => {
            const response = await GET('/survey-platforms');

            response.on('2xx', (status, data) => {
                setSurveyPlatforms(data);

                const theOne = data.find(si => si.value === surveyPlatformName)
                setSelectedSurveyPlatform(theOne);
                setSurveyPlatformFields(theOne.fields.map(field => ({
                    ...field, 
                    value: initialFields[field.name] || ""
                })));
            });
        })();
    }, [surveyPlatformName, initialFields]);

    const checkInputs = useCallback(() => {
        const surveyIdField = surveyPlatformFields.find(f => f.name === 'survey_id');
        const accessTokenField = surveyPlatformFields.find(f => f.name === 'access_token');
        return surveyIdField?.value && accessTokenField?.value;
    }, [surveyPlatformFields]);

    const handleConfirm = useCallback(() => {
        if (!selectedSurveyPlatform) return;
        if (surveyPlatformFields.some(f => f.required && !f.value)) {
            showSnackbar(t('ui.project.survey_platform.add.error.missing_fields'), 'error');
            return;
        }

        const fields = surveyPlatformFields.reduce((acc, field) => {
            return {...acc, [field.name]: field.value}
        }, {});
        localStorage.removeItem('surveyPlatformFields');
        onConfirm(fields);
        // redirect the the same url without the survey_platform and access_token query params
        const url = getNonParamURL(location.pathname, ['survey_platform', 'access_token']);
        navigate(url);

    }, [selectedSurveyPlatform, surveyPlatformFields, showSnackbar, t, onConfirm, location, navigate]);

    return (
        <Loading loading={surveyPlatforms.length === 0}>
            <DialogModal
                open={open}
                title={t('ui.project.survey_platform.edit.title')}
                disableConfirm={!checkInputs()}
                content={
                    <Stack spacing={2} pt={1} width={"450px"}>
                        <SurveyPlatformFields
                            selectedSurveyPlatform={selectedSurveyPlatform}
                            surveyPlatformFields={surveyPlatformFields}
                            initialData={surveyPlatformFields}
                            onChange={setSurveyPlatformFields}
                        />
                    </Stack>
                }
                onClose={onClose}
                onConfirm={handleConfirm}
                confirmProps={{variant: 'contained', disableElevation: true}}
            />
        </Loading>
    );
}

export default EditSurveyPlatformDialog;
