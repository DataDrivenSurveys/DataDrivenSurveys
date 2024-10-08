import { Button, Typography } from '@mui/material';
import React, { JSX, useCallback } from 'react';
import { useTranslation } from 'react-i18next';

import { API } from '../../types';
import HelperText from '../HelperText';
import TextInput from './TextInput';
import formatString, { formatURL } from '../utils/formatString';

interface Condition {
  operator: string;
  field: string;
  value: string;
}

// @ts-expect-error Intentionally extending in an incompatible way
export interface Field extends API.Projects.DataProviderField, API.SurveyPlatforms.SurveyPlatformField {
  condition: Condition;
  label: string;
  helper_text: string;
  helper_url: string;
  interaction_effects: { on_change: API.Bases.InteractionEffect[] };
  visibility_conditions: { expression: string; show: { every: CallableFunction }; hide: { some: CallableFunction } };
}

/**
 * Replaces placeholders in the given string with actual values from fields.
 *
 * @param {string} value - The string containing placeholders to replace.
 * @param {Array} fields - The fields containing the data to use for replacement.
 * @returns {string} - The string with placeholders replaced by actual values.
 */
const replacePlaceholders = (value: string, fields: Field[]): string => {
  const urlValues: Record<string, string> = {};
  const stringValues: Record<string, string> = {};
  const regexPattern = /\{(url|string):([^}]+)\}/g;
  const matches = value.match(regexPattern);

  if (matches) {
    matches.forEach(match => {
      const [type, fieldName] = match.replace('{', '').replace('}', '').split(':');
      const fieldValue = fields.find(f => f.name === fieldName)?.value || '';
      const name = `${type}:${fieldName}` as string;
      if (type === 'url') {
        urlValues[name] = fieldValue;
      } else if (type === 'string') {
        stringValues[name] = fieldValue;
      }
    });
  }

  let result = formatURL(value, urlValues);
  result = formatString(result, stringValues);
  return result;
};

/**
 * Applies interaction effects based on field changes.
 *
 * @param {string} name - The name of the field that changed.
 * @param {any} value - The new value of the field.
 * @param {Array} fields - The current list of fields.
 * @returns {Array} - The updated list of fields after applying interaction effects.
 */
const applyInteractionEffects = (name: string, value: string, fields: Field[]): Field[] => {
  const changedField = fields.find(f => f.name === name);
  if (!changedField || !changedField.interaction_effects) {
    return fields;
  }

  let updatedFields = [...fields];
  changedField.interaction_effects.on_change.forEach(effect => {
    if (effect.action === 'set_value') {
      updatedFields = updatedFields.map(field => {
        if (field.name === effect.field) {
          return { ...field, value: effect.args.value };
        }
        return field;
      });
    }
    // Additional actions can be handled here
  });

  return updatedFields;
};

interface FormFieldsProps {
  fields: Field[];
  onChange: (fields: Field[]) => void;
  buttonActionReducer?: (action: string, args: Record<string, string>) => void;
}

const FormFields = ({ fields, onChange, buttonActionReducer }: FormFieldsProps): (null | JSX.Element)[] => {
  const { t } = useTranslation();

  const checkVisibility = useCallback(
    (field: Field) => {
      const evaluateCondition = (condition: { field: string; operator: string }): boolean => {
        const relatedField = fields.find(f => f.name === condition.field);
        if (!relatedField) return false;

        const value = relatedField.value;
        switch (condition.operator) {
          case 'is_not_empty':
            return (value && value !== '') as boolean;
          case 'is_empty':
            return !value || value === '';
          default:
            return true;
        }
      };

      if (field.visibility_conditions) {
        if (field.visibility_conditions.show && !field.visibility_conditions.show.every(evaluateCondition)) {
          return false;
        }
        if (field.visibility_conditions.hide && field.visibility_conditions.hide.some(evaluateCondition)) {
          return false;
        }
      }
      return true;
    },
    [fields]
  );

  const handleChange = useCallback(
    (name: string, value: string) => {
      // console.log('Handling change:', name, value)
      let updatedFields = fields.map(field => (field.name === name ? { ...field, value: value } : field));
      // console.log('Updated fields:', updatedFields);
      updatedFields = applyInteractionEffects(name, value, updatedFields);
      onChange(updatedFields);
    },
    [fields, onChange]
  );

  const handleButtonClick = useCallback(
    (field: Field) => {
      const args: Record<string, string> = {};
      if (field.onClick && field.onClick.args) {
        for (const [key, value] of Object.entries(field.onClick.args)) {
          args[key] = replacePlaceholders(value, fields);
        }
      }
      if (buttonActionReducer) {
        buttonActionReducer(field?.onClick?.action as never, args);
      }
    },
    [buttonActionReducer, fields]
  );

  return fields.map((field, index) => {
    if (!checkVisibility(field)) {
      // console.log('Skipping field because of visibility conditions', field);
      return null; // Skip rendering if visibility conditions are not met
    }

    switch (field.type) {
      case 'text':
        return (
          <TextInput
            key={index}
            label={t(field.label)}
            value={field.value || ''}
            onChange={value => handleChange(field.name, value)}
            required={field.required}
            disabled={field.disabled}
            helperText={<HelperText text={t(field.helper_text)} url={field.data?.helper_url || ''} />}
          />
        );
      case 'text_area':
        return (
          <TextInput
            key={index}
            label={t(field.label)}
            value={field.value || ''}
            onChange={value => handleChange(field.name, value)}
            required={field.required}
            disabled={field.disabled}
            multiline
            rows={4}
            helperText={<HelperText text={t(field.helper_text)} url={field?.data?.helper_url || ''} />}
          />
        );
      case 'button':
        return (
          <Button key={index} variant="contained" onClick={() => handleButtonClick(field)}>
            {t(field.label)}
          </Button>
        );
      case 'text_block':
        return (
          <Typography key={index} component="div" variant="body1" style={{ margin: '20px 0' }}>
            {t(field.content as string)}
          </Typography>
        );
      default:
        return null;
    }
  });
};

export default FormFields;
