import type { DataOrigin } from '../Shared';

export interface Variable {
  category: string;
  data_origin: DataOrigin[];
  data_type: 'Date' | 'Number' | 'Text';
  description: string;
  info: string;
  label: string;
  name: string;
  test_value: number | string;
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
  attr?: string;
  operator: string;
  value: number | string;
}

export interface DataCategoryCVAttribute extends CVAttribute {
  category: string;
}

export interface DataCategory {
  builtin_variables: BuiltinVariable[];
  custom_variables_enabled: boolean;
  cv_attributes: DataCategoryCVAttribute[];
  data_origin: DataOrigin[];
  label: string;
  value: string;
}

export interface InteractionEffect {
  action: string;
  args: { value: string };
  field: string;
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
  type: 'boolean' | 'button' | 'dropdown' | 'multiselect' | 'number' | 'text' | 'text_area' | 'text_block';
  disabled?: boolean;
  helper_text?: string;
  interaction_effects: { on_change: InteractionEffect[] };
  label: string;
  name: string;
  required?: boolean;
  value: string;
  visibility_conditions: FieldVisibilityCondition | null;
}

export interface Provider {
  instructions: string;
  instructions_helper_url: string;
  label: string;
  value: string;
}
