import { Chip } from '@mui/material';
import React, { useCallback } from 'react';
import { useTranslation } from 'react-i18next';

const SurveyStatus = ({ status }) => {
  const { t } = useTranslation();

  const getColor = useCallback((status) => {
    switch (status) {
    case 'active':
      return 'success';
    case 'inactive':
      return 'default';
    default:
      return 'warning';
    }
  }, []);

  return (
    <Chip
      size={'small'}
      label={t(`ui.project.survey_platform.survey.status.${status}`)}
      color={getColor(status)}
    />
  );
};

export default SurveyStatus;
