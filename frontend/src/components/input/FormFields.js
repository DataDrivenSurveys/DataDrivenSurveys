import {useCallback} from "react";
import {useTranslation} from "react-i18next";
import TextInput from "./TextInput";
import HelperText from "../HelperText";
import { Button } from "@mui/material";
import formatString, { formatURL } from "../utils/formatString";

const FormFields = ({ fields, onChange, buttonActionReducer }) => {

  const {t} = useTranslation();

  const replacePlaceholders = useCallback((value) => {
    const urlValues = {};
    const stringValues = {};

    const regexPattern = /\{(url|string):([^}]+)\}/g;  
    // Extract all placeholders
    const matches = value.match(regexPattern);  

    if (matches) {
      matches.forEach(match => {
        if (match) {
          const [type, fieldName] = match.replace('{', '').replace('}', '').split(':');
          
          const fieldValue = fields.find(f => f.name === fieldName)?.value || '';
    
          if (type === 'url') {
            urlValues[`${type}:${fieldName}`] = fieldValue; // Use the full placeholder as key
          } 
          
          if (type === 'string'){
            stringValues[`${type}:${fieldName}`] = fieldValue; // Use the full placeholder as key
          }
        }
      });
    }
    
    // First replace URL placeholders
    let result = formatURL(value, urlValues);
    // Then replace string placeholders
    result = formatString(result, stringValues);

    return result;
  }, [fields]);
  
  const applyInteractionEffects = useCallback((name, value, fields) => {
    const changedField = fields.find(f => f.name === name);
    if (!changedField || !changedField.interaction_effects) {
      return fields;
    }

    let updatedFields = [...fields];
    changedField.interaction_effects.on_change.forEach(effect => {
      if (effect.action === "set_value") {
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
  }, []);

  const checkVisibility = useCallback((field) => {
    const evaluateCondition = (condition) => {
      const relatedField = fields.find(f => f.name === condition.field);
      if (!relatedField) return false;

      const value = relatedField.value;
      switch (condition.operator) {
        case "is_not_empty":
          return value && value !== '';
        case "is_empty":
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
  }, [fields]);

  const handleChange = useCallback((name, value) => {
    let updatedFields = fields.map(field => field.name === name ? {...field, value: value} : field);
    updatedFields = applyInteractionEffects(name, value, updatedFields);
    onChange(updatedFields);
  }, [fields, onChange, applyInteractionEffects]);

  return fields.map((field, index) => {
    // Conditional rendering based on the field type
    if (!checkVisibility(field)) {
      console.log(`Skipping field because of visibility conditions`, field);
      return null; // Skip rendering if visibility conditions are not met
    }


    if (field.type === 'text') {
      return (
        <TextInput
          key={index}
          label={t(field.label)}
          value={field.value || ''}
          onChange={(value) => handleChange(field.name, value)}
          required={field.required}
          disabled={field.disabled}
          helperText={
            <HelperText
              text={t(field.helper_text)}
              url={field.data?.helper_url || ''}
            />
          }
        />
      );
    } else if (field.type === 'text_area') {
      return (
        <TextInput
          key={index}
          label={t(field.label)}
          value={field.value || ''}
          onChange={(value) => handleChange(field.name, value)}
          required={field.required}
          disabled={field.disabled}
          multiline
          rows={4}
          helperText={
          <HelperText
            text={t(field.helper_text)}
            url={field.data?.helper_url || ''}
          />
          }
        />
      );
    } else if(field.type === 'button') {
        const onClick = () => {
          // execute the reducer action
          // replace eventual placeholders in every key of the args object
          const args = {};
          if(field.onClick.args){
            for (const [key, value] of Object.entries(field.onClick.args)) {
              args[key] = replacePlaceholders(value);
            }  
          }

          buttonActionReducer(field.onClick.action, args);
        };

        return (
          <Button key={index} variant="contained" onClick={onClick}>
            {t(field.label)}
          </Button>
        );
    }
    return null;
    // Additional field types can be handled with more conditions or a switch-case structure
  });
}

export default FormFields;
