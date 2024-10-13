import { Delete as DeleteIcon } from '@mui/icons-material';
import { Button, IconButton, Stack, Typography } from '@mui/material';
import type { JSX } from 'react';
import React, { useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import type { API } from '../../../types';
import DropDown from '../../input/DropDown';
import ValueInput from '../../input/ValueInput';

// @ts-expect-error Intentionally extending in an incompatible way
interface Filter extends API.Projects.CVFilter {
  operator: API.Projects.CVOperator | '';
}

type FilterValues = API.Projects.CVOperator | number;

interface CVFiltersProps {
  filters: Filter[];
  index: number;
  operators: API.Projects.CVOperator[];
  dataCategory: API.Projects.DataCategory;
  onChange: (filters: Filter[]) => void;
}

const CVFilters = ({ filters, dataCategory, operators, onChange }: CVFiltersProps): JSX.Element => {
  const { t } = useTranslation();

  const addFilter = (): void => {
    onChange([
      ...filters,
      {
        attribute: '',
        operator: '',
        value: '',
      },
    ]);
  };

  const removeFilter = (index: number): void => {
    const newFilters = [...filters];
    newFilters.splice(index, 1);
    onChange(newFilters);
  };

  const updateFilter = (index: number, key: keyof Filter, value: FilterValues): void => {
    const newFilters = [...filters];
    if (key === 'operator') {
      newFilters[index][key] = value as API.Projects.CVOperator;
    } else {
      newFilters[index][key] = value as string;
    }
    onChange(newFilters);
    // console.log("newFilters", newFilters)
  };

  return (
    <Stack spacing={2}>
      <Typography variant="body1">{t('ui.project.custom_variable.filters.title')}</Typography>
      {filters.map((filter, index) => (
        <Stack direction="row" spacing={2} alignItems="center" key={index}>
          <CVFilter
            filter={filter}
            index={index}
            operators={operators}
            dataCategory={dataCategory}
            onChange={updateFilter}
            onRemove={removeFilter}
          />
        </Stack>
      ))}

      <Button onClick={addFilter}>Add Filter</Button>
    </Stack>
  );
};

interface CVFilterProps {
  filter: Filter;
  index: number;
  operators: API.Projects.CVOperator[];
  dataCategory: API.Projects.DataCategory;
  onChange: (index: number, key: keyof Filter, value: FilterValues) => void;
  onRemove: (index: number) => void;
}

const CVFilter = ({ filter, index, operators, dataCategory, onChange, onRemove }: CVFilterProps): JSX.Element => {
  const { t } = useTranslation();

  const getDataTypeForAttribute = useCallback(
    (attribute: string) => {
      return dataCategory.cv_attributes.find(prop => prop.attribute === attribute)?.data_type;
    },
    [dataCategory]
  );

  const getUnitForAttribute = useCallback(
    (attribute: string) => {
      return dataCategory.cv_attributes.find(prop => prop.attribute === attribute)?.unit;
    },
    [dataCategory]
  );

  const getOperatorsForAttribute = useCallback(
    (attribute: string) => {
      const ops = operators[getDataTypeForAttribute(attribute)] || [];
      return ops.map(op => ({
        ...op,
        label: t(op.label), // translate label
      }));
    },
    [operators, getDataTypeForAttribute, t]
  );

  return (
    <Stack direction="row" spacing={1} alignItems="center">
      <DropDown
        label="Attribute"
        items={dataCategory.cv_attributes.map(prop => ({
          value: prop.attribute,
          label: prop.label,
        }))}
        value={filter.attribute}
        onChange={event => onChange(index, 'attribute', event.target.value)}
        sx={{ minWidth: 200 }}
      />

      {filter.attribute && (
        <DropDown
          label="Operator"
          items={getOperatorsForAttribute(filter.attribute)}
          value={filter.operator}
          onChange={event => onChange(index, 'operator', event.target.value)}
          sx={{ minWidth: 200 }}
        />
      )}

      {filter.operator && (
        <ValueInput
          label="Value"
          data_type={getDataTypeForAttribute(filter.attribute)}
          value={filter.value}
          unit={getUnitForAttribute(filter.attribute)}
          onChange={value => onChange(index, 'value', value)}
        />
      )}

      <IconButton onClick={() => onRemove(index)}>
        <DeleteIcon />
      </IconButton>
    </Stack>
  );
};

export default CVFilters;
