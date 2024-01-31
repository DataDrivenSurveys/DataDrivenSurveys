import { Stack } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '../../../../context/SnackbarContext';
import {  POST } from '../../../../code/http_requests';
import { useCallback, useEffect, useState } from 'react';


import CVEditor from './custom_variables/CVEditor';
import DialogModal from '../../../layout/DialogModal';
import { checkCustomVariableCompleteness } from './custom_variables/utils';

const AddCustomVariableDialog = ({ project, open, onClose, onAdd }) => {

    const { t } = useTranslation();

    const { showBottomCenter: showSnackbar } = useSnackbar();


    const [ customVariable, setCustomVariable ] = useState({
        variable_name: "",
    });

    // reinitialize customVariable when the dialog is closed
    useEffect(() => {
        if(!open) setCustomVariable({
            variable_name: "",
        });
    }, [open]);


    const createCustomVariable = useCallback(async () => {

        const { success, messageId } = checkCustomVariableCompleteness(customVariable);
        if(!success){
            showSnackbar(t(messageId), 'error');
            return;
        }

        const response = await POST(`/projects/${project.id}/custom-variables/`, customVariable);

        response.on('2xx', (status, data) => {
            if(status === 200) {
                showSnackbar(t('ui.project.custom_variable.create.success'), 'success');
                onAdd && onAdd(data);
            }
        });

        response.on('4xx', (status, data) => {
            showSnackbar(t(data.message.id), 'error');
        });

    }, [showSnackbar, t, project.id, customVariable, onAdd]);

    const checkInputs = useCallback(() => {
        if(!customVariable) return false;
        const { success } = checkCustomVariableCompleteness(customVariable);
        return success;
    }, [customVariable]);

    return (
        <DialogModal
            open={open}
            title={t('ui.project.custom_variable.create.title')}
            onClose={onClose}
            onConfirm={() => createCustomVariable()}
            disableConfirm={!checkInputs()}
            content={
                <Stack width={"100%"} alignItems={"flex-start"} pt={1}>
                    <CVEditor
                        project={project}
                        data={customVariable}
                        onChange={(data) => setCustomVariable(data)}
                    />
                </Stack>
            }
            confirmProps={{variant: 'contained', disableElevation: true}}
        />
    )
}



export default AddCustomVariableDialog;
