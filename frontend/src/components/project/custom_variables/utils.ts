import { API } from '../../../types';

interface CVCheckResult {
  success: boolean;
  messageId: string;
  message: string;
}

const isValidVariableName = (variableName: string): CVCheckResult => {
  if (!variableName) {
    return { success: false, messageId: 'ui.variables.name_required', message: 'Variable name is required.' };
  }

  if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(variableName)) {
    return { success: false, messageId: 'ui.variables.invalid_name', message: 'Invalid variable name.' };
  }

  return { success: true, messageId: '', message: '' };
};

export const checkCustomVariableCompleteness = (customVariable: API.Projects.CustomVariable): CVCheckResult => {
  const variableNameCheck = isValidVariableName(customVariable?.variable_name);
  if (!variableNameCheck.success) {
    return variableNameCheck;
  }

  if (!customVariable.data_provider) {
    return {
      success: false,
      messageId: 'ui.custom_variables.error.data_provider_required',
      message: 'Data provider is required.',
    };
  }

  if (!customVariable.data_category) {
    return {
      success: false,
      messageId: 'ui.custom_variables.error.data_category_required',
      message: 'Data category is required.',
    };
  }

  if (!customVariable.cv_attributes) {
    return {
      success: false,
      messageId: 'ui.custom_variables.error.attributes_required',
      message: 'Attributes are required.',
    };
  }

  if (!customVariable.selection) {
    return {
      success: false,
      messageId: 'ui.custom_variables.error.selection_required',
      message: 'Selection is required.',
    };
  }

  if (customVariable.selection) {
    const { attr, operator } = customVariable.selection;
    if (!operator) {
      return {
        success: false,
        messageId: 'ui.custom_variables.error.selection_operator_required',
        message: 'Selection operator is required.',
      };
    }

    if (operator !== 'random' && !attr) {
      return {
        success: false,
        messageId: 'ui.custom_variables.error.selection_attr_required',
        message: 'Selection attribute is required.',
      };
    }
  }

  if (customVariable.filters) {
    for (const filter of customVariable.filters) {
      const { attr, operator, value } = filter;
      if (!attr) {
        return {
          success: false,
          messageId: 'ui.custom_variables.error.filter_attr_required',
          message: 'Filter attribute is required.',
        };
      }
      if (!operator) {
        return {
          success: false,
          messageId: 'ui.custom_variables.error.filter_operator_required',
          message: 'Filter operator is required.',
        };
      }
      if (!value) {
        return {
          success: false,
          messageId: 'ui.custom_variables.error.filter_value_required',
          message: 'Filter value is required.',
        };
      }
    }
  }

  return { success: true, messageId: '', message: '' };
};
