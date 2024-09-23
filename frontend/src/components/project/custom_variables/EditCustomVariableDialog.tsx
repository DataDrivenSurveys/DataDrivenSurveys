import { Stack } from '@mui/material';
import React, { JSX, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import CVEditor from './CVEditor';
import { checkCustomVariableCompleteness } from './utils';
import { GET, PUT } from '../../../code/http_requests';
import { useSnackbar } from '../../../context/SnackbarContext';
import { API } from '../../../types';
import ConfirmationDialog from '../../feedback/ConfirmationDialog';

interface EditCustomVariableDialogProps {
  project: API.Projects.Project;
  customVariableId: number | null;
  open: boolean;
  onClose?: () => void;
  onEdit?: (customVariable: API.Projects.CustomVariable) => void;
}

const EditCustomVariableDialog = ({
  project,
  customVariableId,
  open,
  onClose,
  onEdit,
}: EditCustomVariableDialogProps): JSX.Element => {
  const { t } = useTranslation();

  const { showBottomCenter: showSnackbar } = useSnackbar();

  const [customVariable, setCustomVariable] = useState<API.Projects.CustomVariable>({} as API.Projects.CustomVariable);

  const fetchCustomVariable = useCallback(
    async (projectId: string, customVariableId: number) => {
      const response = await GET(`/projects/${projectId}/custom-variables/${customVariableId}`);

      response.on('2xx', (status: number, data: API.Projects.CustomVariable) => {
        if (status === 200) {
          setCustomVariable(data);
        }
      });

      response.on('4xx', (_: number, data: API.ResponseData) => {
        showSnackbar(t(data.message.id), 'error');
      });
    },
    [showSnackbar, t]
  );

  useEffect(() => {
    if (!customVariableId) return;
    fetchCustomVariable(project.id, customVariableId);
  }, [fetchCustomVariable, project.id, customVariableId]);

  const editCustomVariable = useCallback(async () => {
    // console.log("editCustomVariable customVariable", customVariable)

    const response = await PUT(`/projects/${project.id}/custom-variables/${customVariableId}`, customVariable);

    response.on('2xx', (status: number, data: API.Projects.CustomVariable) => {
      if (status === 200) {
        showSnackbar(t('ui.project.custom_variable.edit.success'), 'success');
        onEdit?.(data);
      }
    });

    response.on('4xx', (_: number, data: API.ResponseData) => {
      showSnackbar(t(data.message.id), 'error');
    });

    response.on('5xx', (_: number, data: API.ResponseData) => {
      showSnackbar(t(data.message.id), 'error');
    });
  }, [showSnackbar, t, project.id, customVariable, customVariableId, onEdit]);

  const checkInputs = useCallback(() => {
    if (!customVariable) return false;
    const { success } = checkCustomVariableCompleteness(customVariable);
    return success;
  }, [customVariable]);

  return (
    <ConfirmationDialog
      open={open}
      title={t('ui.project.custom_variable.edit.title')}
      onClose={onClose}
      onConfirm={() => editCustomVariable()}
      disableConfirm={!checkInputs()}
      content={
        <Stack spacing={2} width={'100%'} alignItems={'flex-start'} pt={1}>
          <CVEditor
            project={project}
            data={customVariable}
            onChange={(data: API.Projects.CustomVariable) => setCustomVariable(data)}
          />
        </Stack>
      }
    />
  );
};

export default EditCustomVariableDialog;
