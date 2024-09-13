import { Stack } from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import React from 'react';
import { useTranslation } from 'react-i18next';

import CVEditor from './custom_variables/CVEditor';
import { checkCustomVariableCompleteness } from './custom_variables/utils';
import { GET, PUT } from '../../../../code/http_requests';
import { useSnackbar } from '../../../../context/SnackbarContext';
import DialogModal from '../../../layout/DialogModal';


const EditCustomVariableDialog = ({ project, customVariableId, open, onClose, onEdit}) => {

    const { t } = useTranslation();

    const { showBottomCenter: showSnackbar } = useSnackbar();

    const [ customVariable, setCustomVariable ] = useState(null);

    const fetchCustomVariable = useCallback(async (projectId, customVariableId) => {
        const response = await GET(`/projects/${projectId}/custom-variables/${customVariableId}`);

        response.on('2xx', (status, data) => {
            if(status === 200) {
                setCustomVariable(data);
            }
        });

        response.on('4xx', (status, data) => {
            showSnackbar(t(data.message.id), 'error');
        });

    }, [showSnackbar, t]);


    useEffect(() => {
        if(!customVariableId) return;
        fetchCustomVariable(project.id, customVariableId);
    }, [fetchCustomVariable, project.id, customVariableId]);

    const editCustomVariable = useCallback(async () => {
        console.log("editCustomVariable customVariable", customVariable)

        const response = await PUT(`/projects/${project.id}/custom-variables/${customVariableId}`, customVariable);

        response.on('2xx', (status, data) => {
            if(status === 200) {
                showSnackbar(t('ui.project.custom_variable.edit.success'), 'success');
                onEdit && onEdit(data);
            }
        });

        response.on('4xx', (_, data) => {
            showSnackbar(t(data.message.id), 'error');
        });

        response.on('5xx', (_, data) => {
            showSnackbar(t(data.message.id), 'error');
        });

    }, [showSnackbar, t, project.id, customVariable, customVariableId, onEdit]);


    const checkInputs = useCallback(() => {
        if(!customVariable) return false;
        const { success } = checkCustomVariableCompleteness(customVariable);
        return success;
    }, [customVariable]);


    return (
        <DialogModal
            open={open}
            title={t('ui.project.custom_variable.edit.title')}
            onClose={onClose}
            onConfirm={() => editCustomVariable()}
            disableConfirm={!checkInputs()}
            content={
                <Stack spacing={2} width={"100%"} alignItems={"flex-start"} pt={1}>
                    <CVEditor
                        project={project}
                        data={customVariable}
                        onChange={(data) => setCustomVariable(data)}
                    />
                </Stack>
            }
        />
    )
}



export default EditCustomVariableDialog;
