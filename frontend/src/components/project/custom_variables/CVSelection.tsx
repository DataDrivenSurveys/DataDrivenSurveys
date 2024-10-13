import { Stack, Typography } from '@mui/material';
import React, { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import type { API } from '../../../types';
import DropDown from '../../input/DropDown';

interface CVSelectionLabels {
  value: API.Projects.CVOperator;
  label: string;
}

interface CVSelectionProps {
  selection: API.Projects.CVSelection;
  dataCategory: API.Bases.DataCategory;
  onChange: (selection: API.Projects.CVSelection) => void;
}

const CVSelection = ({ selection, dataCategory, onChange }: CVSelectionProps): React.JSX.Element => {
  const { t } = useTranslation();

  const [selectedAttribute, setSelectedAttribute] = useState<string>('');

  useEffect((): void => {
    setSelectedAttribute(selection.attribute || '');
  }, [selection]);

  const getSelectionCriteriaOptions = useCallback((): CVSelectionLabels[] => {
    const filter_attribute = dataCategory.cv_attributes.find(prop => prop.attribute === selectedAttribute);
    switch (filter_attribute?.data_type) {
      case 'Date':
        return [
          {
            value: 'max',
            label: t('ui.custom_variables.selection_criterion.selection_criterion.date.min.label'),
          },
          {
            value: 'min',
            label: t('ui.custom_variables.selection_criterion.selection_criterion.date.max.label'),
          },
          {
            value: 'random',
            label: t('ui.custom_variables.selection_criterion.selection_criterion.date.random.label'),
          },
        ];
      default:
        return [
          {
            value: 'max',
            label: t('ui.custom_variables.selection_criterion.selection_criterion.min.label'),
          },
          {
            value: 'min',
            label: t('ui.custom_variables.selection_criterion.selection_criterion.max.label'),
          },
          {
            value: 'random',
            label: t('ui.custom_variables.selection_criterion.selection_criterion.random.label'),
          },
        ];
    }
  }, [selectedAttribute, dataCategory, t]);

  return (
    <Stack direction={'row'} spacing={2} alignItems={'center'}>
      <Typography variant="body1">
        {t('ui.project.custom_variable.selection.part1', { data_category: dataCategory.label })}
      </Typography>
      <DropDown
        label={t('ui.custom_variables.selection_criterion.selection_criterion.dropdown.label')}
        items={getSelectionCriteriaOptions()}
        value={selection.operator}
        onChange={(event): void => {
          onChange({
            ...selection,
            operator: event.target.value as API.Projects.CVOperator,
          });
        }}
      />

      {selection.operator !== 'random' && (
        <>
          <Typography variant="body1">{t('ui.project.custom_variable.selection.part2')}</Typography>
          <DropDown
            label="Attribute"
            items={dataCategory.cv_attributes.map(prop => ({
              value: prop.attribute,
              label: prop.label,
            }))}
            value={selection.attribute}
            onChange={e => {
              setSelectedAttribute(e.target.value);
              onChange({
                ...selection,
                attribute: e.target.value,
              });
            }}
          />
        </>
      )}
    </Stack>
  );
};

export default CVSelection;
