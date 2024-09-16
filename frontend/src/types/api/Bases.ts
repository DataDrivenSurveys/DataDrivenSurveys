import { DataOrigin } from '../Shared';

export interface BuiltinVariable {
  category: string;
  data_origin: DataOrigin[];
  data_type: string;
  description: string;
  index: number | null;
  info: string;
  is_indexed_variable: boolean;
  label: string;
  name: string;
  test_value: string;
  test_value_placeholder: string;
  unit: string | null;
}

export interface CVAttribute {
  attribute: string;
  data_origin: DataOrigin[];
  data_type: string;
  description: string;
  enabled: boolean;
  info: string;
  label: string;
  name: string;
  test_value: string;
  test_value_placeholder: string;
  unit: string;
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

