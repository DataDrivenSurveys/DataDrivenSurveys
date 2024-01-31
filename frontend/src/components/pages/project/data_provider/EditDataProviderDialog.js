import {useSnackbar} from "../../../../context/SnackbarContext";
import {useCallback, useEffect, useState} from "react";
import {GET, PUT} from "../../../../code/http_requests";
import DialogModal from "../../../layout/DialogModal";
import {Stack, Typography} from "@mui/material";

import {useTranslation} from 'react-i18next';
import FormFields from "../../../input/FormFields";
import HelperText from "../../../HelperText";
import CopyClipboard from "../../../input/CopyClipboard";
import {getFrontendBaseURL} from "../../../utils/getURL";


const EditDataProviderDialog = ({projectId, data, open, onClose, onEdit}) => {

  const {t} = useTranslation();

  const {showBottomCenter: showSnackbar} = useSnackbar();
  const [dataProviders, setDataProviders] = useState(undefined);
  const [selected, setSelected] = useState(undefined);
  const [fields, setFields] = useState([]);

  useEffect(() => {
    if (!data) return;
    (async () => {
      const response = await GET('/data-providers');

      response.on('2xx', (status, dataProviders) => {
        setDataProviders(dataProviders);
        const dataProvider = dataProviders.find(dp => dp.value === data.data_provider_type);
        setSelected(dataProvider);
        const mergedFields = dataProvider.fields.map(field => ({
          ...field,
          value: data.fields[field.name] || '',
        }));

        setFields(mergedFields);
      });
    })();
  }, [data]);

  const handleConfirm = useCallback(() => {
    if (fields.some(f => f.required && !f.value)) {
      showSnackbar(t('ui.project.data_providers.add.error.missing_fields'), 'error');
      return;
    }

    (async () => {
      const response = await PUT(`/projects/${projectId}/data-providers/${data.data_provider_type}`, {
        selected_data_provider: selected,
        fields
      });

      response.on('2xx', (status, data) => {
        if (status === 200) {
          showSnackbar(t(data.message.id), 'success');
          onEdit();
        }
      });

      response.on('4xx', (_, data) => {
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
      <DialogModal
        open={open}
        title={t('ui.project.data_providers.edit.title')}
        titleLogo={{logoName: selected.value, logoSize: 18, label: selected.label}}
        disableConfirm={!checkInputs()}
        content={
          <Stack spacing={2}>
            <Typography></Typography>
            <Typography variant="body1">
              {t('ui.project.data_providers.create_app.common_fields.callback_url.instructions')}
              <br/>
              <CopyClipboard
                what={`${getFrontendBaseURL()}/${selected.callback_url}`}
              />
            </Typography>
            <HelperText
              text={t('ui.project.data_providers.add.documentation_instructions')}
              url={t(selected.instructions_helper_url)}
              typographyProps={{variant: "body1", color: "textPrimary"}}
              urlInline={false}
            />
            <FormFields fields={fields} onChange={setFields}/>
          </Stack>
        }
        onClose={onClose}
        onConfirm={handleConfirm}
      />
    )
  );
}

export default EditDataProviderDialog;
