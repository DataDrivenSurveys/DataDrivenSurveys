import { Stack, Typography } from '@mui/material';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableRow from '@mui/material/TableRow';
import React, { JSX, useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { GET, POST } from '../../../code/http_requests';
import { useSnackbar } from '../../../context/SnackbarContext';
import { API } from '../../../types';
import ConfirmationDialog from '../../feedback/ConfirmationDialog';
import HelperText from '../../HelperText';
import CopyClipboard from '../../input/CopyClipboard';
import DropDown from '../../input/DropDown';
import FormFields, { Field } from '../../input/FormFields';
import Logo from '../../Logo';
import { getAppCreationURL, getFrontendBaseURL, getNonParamURL } from '../../utils/getURL';

interface AddDataProviderDialogProps {
  projectId: string;
  existingProviders: API.Projects.DataProvider[];
  open: boolean;
  onClose: CallableFunction;
  onAdd: CallableFunction;
  projectName: string;
}

const AddDataProviderDialog = ({
  projectId,
  existingProviders,
  open,
  onClose,
  onAdd,
  projectName,
}: AddDataProviderDialogProps): JSX.Element => {
  const { t } = useTranslation();

  const [fields, setFields] = useState<API.Projects.DataProviderField[]>([]);

  const { showBottomCenter: showSnackbar } = useSnackbar();
  const [dataProviders, setDataProviders] = useState<API.Projects.DataProvider[]>([]);
  const [selected, setSelected] = useState<API.Projects.DataProvider | undefined>(undefined);

  useEffect(() => {
    (async (): Promise<void> => {
      const response = await GET('/data-providers');

      response.on('2xx', (status: number, data: API.Projects.DataProvider[]) => {
        console.log(response);
        const remainingProviders: API.Projects.DataProvider[] = data
          .filter(p => !existingProviders.some(ep => ep.data_provider_name === p.value))
          .map(ep => ({ ...ep, icon: <Logo name={ep.value} size={18} /> }));

        setDataProviders(remainingProviders);
        if (remainingProviders.length === 0) {
          setSelected(undefined);
          setFields([]);
          return;
        }
        setDataProviders(remainingProviders);
        setSelected(remainingProviders[0]);
        setFields(remainingProviders[0].fields.map(field => ({ ...field, value: '' })));
      });
    })();
  }, [projectId, existingProviders]);

  useEffect(() => {
    const selectedProvider = dataProviders?.find(dp => dp.value === selected?.value);
    setFields(selectedProvider?.fields.map(field => ({ ...field, value: '' })) || []);
  }, [selected, dataProviders]);

  const handleConfirm = useCallback(() => {
    if (!selected) return;
    if (fields.some(f => f.required && !f.value)) {
      showSnackbar(t('ui.project.data_providers.add.error.missing_fields'), 'error');
      return;
    }

    (async (): Promise<void> => {
      const response = await POST(`/projects/${projectId}/data-providers/`, {
        selected_data_provider: {
          label: selected.label,
          value: selected.value,
        },
        fields,
      });

      response.on('2xx', (status: number) => {
        if (status === 201) {
          showSnackbar(t('ui.project.data_providers.add.success'), 'success');
          onAdd();
        }
      });
    })();
  }, [projectId, selected, fields, showSnackbar, onAdd, t]);

  const checkInputs = useCallback((): boolean => {
    if (!selected) return false;
    return !fields.some(f => f.required && !f.value);
  }, [selected, fields]);

  return (
    dataProviders && (
      <ConfirmationDialog
        open={open}
        title={t('ui.project.data_providers.add.title')}
        disableConfirm={!checkInputs()}
        content={
          <Stack spacing={2} width={'fit-content'}>
            {dataProviders.length === 0 && (
              <Typography variant="body1">{t('ui.project.data_providers.add.no_providers')}</Typography>
            )}
            {dataProviders.length > 0 && (
              <>
                <Typography variant="body1">
                  {t('ui.project.data_providers.add.select_provider.instructions')}
                </Typography>
                <DropDown
                  label={t('ui.project.data_providers.add.select_provider.label')}
                  value={selected?.value}
                  items={dataProviders}
                  onChange={e => setSelected(dataProviders.find(dp => dp.value === e.target.value))}
                />

                {selected && selected.app_required && (
                  <AppRelatedInstructions selected={selected} projectName={projectName} />
                )}

                <FormFields
                  fields={fields as unknown as Field[]}
                  onChange={setFields as unknown as (fields: Field[]) => void}
                />
              </>
            )}
          </Stack>
        }
        onClose={onClose}
        onConfirm={handleConfirm}
        confirmProps={{ variant: 'contained', disableElevation: true }}
      />
    )
  );
};

interface AppRelatedInstructionsProps {
  selected: API.Projects.DataProvider;
  projectName: string;
}

const AppRelatedInstructions = ({ selected, projectName }: AppRelatedInstructionsProps): JSX.Element => {
  const { t } = useTranslation();

  return (
    <>
      <Stack spacing={0.5}>
        <Typography variant="body1">
          {t('ui.project.data_providers.add.general_instructions')} {selected.label}
          {'.'}
        </Typography>

        <HelperText
          text={t('ui.project.data_providers.create_app.instructions')}
          url={getAppCreationURL(selected.app_creation_url, selected.value, {
            project_name: `DDSurvey - ${projectName}`,
          })}
          urlText={getNonParamURL(selected.app_creation_url)}
          typographyProps={{ variant: 'body1', color: 'textPrimary' }}
          urlInline={false}
          maxURLLength={50}
        />
      </Stack>

      <Stack spacing={0.5}>
        <Typography variant="body1">{t('ui.project.data_providers.create_app.common_fields.instructions')}</Typography>

        <TableContainer>
          <Table
            sx={{
              '& .MuiTableCell-sizeMedium': {
                padding: '2px 6px',
              },
            }}
          >
            <TableBody>
              <TableRow>
                <TableCell>{t('ui.project.data_providers.create_app.common_fields.application_name.label')}</TableCell>
                <TableCell>
                  <CopyClipboard what={`DDSurvey - ${projectName}`} />
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>
                  {t('ui.project.data_providers.create_app.common_fields.application_website_url.label')}
                </TableCell>
                <TableCell>
                  <CopyClipboard what={`${getFrontendBaseURL()}/about`} />
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>
                  {t('ui.project.data_providers.create_app.common_fields.terms_of_service_url.label')}
                </TableCell>
                <TableCell>
                  <CopyClipboard what={`${getFrontendBaseURL()}/terms-of-service`} />
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>
                  {t('ui.project.data_providers.create_app.common_fields.privacy_policy_url.label')}
                </TableCell>
                <TableCell>
                  <CopyClipboard what={`${getFrontendBaseURL()}/privacy-policy`} />
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>{t('ui.project.data_providers.create_app.common_fields.callback_url.label')}</TableCell>
                <TableCell>
                  <CopyClipboard what={`${getFrontendBaseURL()}/${selected.callback_url}`} />
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Stack>

      <HelperText
        text={t('ui.project.data_providers.add.documentation_instructions')}
        url={t(selected.instructions_helper_url)}
        urlText={t('ui.project.data_providers.add.documentation_url_text')}
        typographyProps={{ variant: 'body1', color: 'textPrimary' }}
        urlInline={true}
        textPostfix={false}
      />
    </>
  );
};

export default AddDataProviderDialog;
