import { Chip } from '@mui/material';
import React, { JSX, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import { Shared } from '../../../types';

interface SurveyStatusProps {
  status?: Shared.SurveyStatus; // active, inactive, scheduled, completed, abandoned, failed, or draft
}

const SurveyStatus = ({ status = 'unknown' }: SurveyStatusProps): JSX.Element => {
  const { t } = useTranslation();

  const getColor = useCallback((status: Shared.SurveyStatus) => {
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
    <Chip size={'small'} label={t(`ui.project.survey_platform.survey.status.${status}`)} color={getColor(status)} />
  );
};

export default SurveyStatus;
