import { Stack, Typography } from '@mui/material';
import React, { JSX, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { GET, PUT } from '../../../code/http_requests';
import { useSnackbar } from '../../../context/SnackbarContext';
import { API, Models } from '../../../types';
import ConfirmationDialog from '../../feedback/ConfirmationDialog';
import HelperText from '../../HelperText';
import CopyClipboard from '../../input/CopyClipboard';
import FormFields, { Field } from '../../input/FormFields';
import { getFrontendBaseURL } from '../../utils/getURL';

interface EditDataProviderProps {
  projectId: string;
  data: Models.Projects.DataProvider;
  open: boolean;
  onClose: () => void;
  onEdit: (newData?: { data_provider_name: string; fields: Record<string, string> }) => void;
}

const EditDataProviderDialog = ({ projectId, data, open, onClose, onEdit }: EditDataProviderProps): JSX.Element => {
  const { t } = useTranslation();

  const { showBottomCenter: showSnackbar } = useSnackbar();
  const [dataProviders, setDataProviders] = useState<API.Projects.DataProvider[]>([]);
  const [selected, setSelected] = useState<API.Projects.DataProvider>({} as API.Projects.DataProvider);
  const [fields, setFields] = useState<Field[]>([]);

  useEffect(() => {
    if (!data) return;
    (async (): Promise<void> => {
      const response = await GET('/data-providers');

      response.on('2xx', (status: number, dataProviders: API.Projects.DataProvider[]) => {
        setDataProviders(dataProviders);
        const dataProvider = dataProviders.find(dp => dp.value === data.data_provider_name);
        setSelected(dataProvider as API.Projects.DataProvider);
        const mergedFields = (dataProvider as API.Projects.DataProvider).fields.map(field => ({
          ...field,
          // TODO: check whether the value is being set correctly.
          value: data.fields[field.name as unknown as number] || '',
        }));

        setFields(mergedFields as unknown as Field[]);
      });
    })();
  }, [data]);

  const handleConfirm = useCallback(() => {
    if (fields.some(f => f.required && !f.value)) {
      showSnackbar(t('ui.project.data_providers.add.error.missing_fields'), 'error');
      return;
    }

    (async (): Promise<void> => {
      const response = await PUT(`/projects/${projectId}/data-providers/${data.data_provider_name}`, {
        selected_data_provider: selected,
        fields,
      });

      response.on('2xx', (status: number, data: API.ResponseData) => {
        if (status === 200) {
          showSnackbar(t(data.message.id), 'success');
          onEdit();
        }
      });

      response.on('4xx', (_: number, data: API.ResponseData) => {
        showSnackbar(t(data.message.id), 'error');
      });
    })();
  }, [data, projectId, selected, fields, showSnackbar, onEdit, t]);

  const checkInputs = useCallback(() => {
    if (!selected) return false;
    return !fields.some(f => f.required && !f.value);
  }, [selected, fields]);

  return (
    dataProviders && (
      <ConfirmationDialog
        open={open}
        title={t('ui.project.data_providers.edit.title')}
        titleLogo={{ logoName: selected.value, logoSize: 18, label: selected.label }}
        disableConfirm={!checkInputs()}
        content={
          <Stack spacing={2}>
            {selected && selected.app_required && <AppRelatedInstructions selected={selected} />}

            <FormFields fields={fields as unknown as Field[]} onChange={setFields} />
          </Stack>
        }
        onClose={onClose}
        onConfirm={handleConfirm}
      />
    )
  );
};

interface AppRelatedInstructionsProps {
  selected: API.Projects.DataProvider;
}

const AppRelatedInstructions = ({ selected }: AppRelatedInstructionsProps): JSX.Element => {
  const { t } = useTranslation();
  return (
    <>
      <Typography variant="body1">
        {t('ui.project.data_providers.create_app.common_fields.callback_url.instructions')}
        <br />
        <CopyClipboard what={`${getFrontendBaseURL()}/${selected.callback_url}`} />
      </Typography>
      <HelperText
        text={t('ui.project.data_providers.add.documentation_instructions')}
        url={t(selected.instructions_helper_url)}
        typographyProps={{ variant: 'body1', color: 'textPrimary' }}
        urlInline={false}
      />
    </>
  );
};

export default EditDataProviderDialog;
