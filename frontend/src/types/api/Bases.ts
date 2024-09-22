import { DataOrigin } from '../Shared';

export interface Variable {
  category: string;
  data_origin: DataOrigin[];
  data_type: 'Date' | 'Number' | 'Text';
  description: string;
  name: string;
  info: string;
  label: string;
  test_value: string | number;
  test_value_placeholder: string;
  unit: string | null;
}

export interface BuiltinVariable extends Variable {
  index: number | null;
  is_indexed_variable: boolean;
}

export interface CVAttribute extends Variable {
  attribute: string;
}

export interface CVFilter {
  operator: string;
  value: string | number;
}

export interface DataCategoryCVAttribute extends CVAttribute {
  category: string;
}

export interface DataCategory {
  label: string;
  value: string;
  custom_variables_enabled: boolean;
  builtin_variables: BuiltinVariable[];
  cv_attributes: DataCategoryCVAttribute[];
  data_origin: DataOrigin[];
}

export interface InteractionEffect {
  action: string;
  field: string;
  args: { value: string };
}

export type FieldVisibilityConditionOperator = 'is_empty' | 'is_not_empty';

export interface FieldVisibilityConditionValue {
  field: 'access_token';
  operator: FieldVisibilityConditionOperator;
}

export interface FieldVisibilityCondition {
  hide?: FieldVisibilityConditionValue[];
  show?: FieldVisibilityConditionValue[];
}

export interface Field {
  name: string;
  label: string;
  value: string;
  helper_text?: string;
  type: 'text_block' | 'text_area' | 'text' | 'button' | 'dropdown' | 'multiselect' | 'boolean' | 'number';
  disabled?: boolean;
  required?: boolean;
  visibility_conditions: FieldVisibilityCondition | null;
  interaction_effects: { on_change: InteractionEffect[] };
}

export interface Provider {
  label: string;
  value: string;
  instructions: string;
  instructions_helper_url: string;
}
