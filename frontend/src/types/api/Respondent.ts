import type { Bases, ResponseData } from '.';
import type { DataOrigin, DataProviderType } from '../Shared';
import type * as Projects from './Projects';
import type { MessageData } from './ResponseReturnValue';

export interface DataConnection {
  data_provider: {
    data_provider_name: string;
    data_provider_type: DataProviderType;
    name: string;
  };
}

export interface BuiltinVariable {
  type: 'Builtin';
  data_origin: DataOrigin[];
  data_provider: string;
  description: string;
  variable_name: string;
}

export interface CVFilter extends Bases.CVFilter {
  attribute: Bases.CVAttribute;
}

export interface CVSelectionOperator {
  operator: 'max' | 'min' | 'random';
  strategy: '_max_strategy' | '_min_strategy' | '_random_strategy';
}

export interface CVSelection {
  attribute: Bases.CVAttribute | null;
  operator: CVSelectionOperator;
}

export interface CustomVariableData {
  attributes: Bases.CVAttribute[];
  data_category: Bases.DataCategory;
  filters: CVFilter[];
  qualified_name: string;
  selection: CVSelection;
  variable_name: string;
}

export interface CustomVariable {
  type: 'Custom';
  data: CustomVariableData;
  data_origin: DataOrigin[];
  data_provider: string;
  variable_name: string;
}

export interface DataProvider {
  type: DataProviderType;
  authorize_url: string;
  client_id: string;
  data_provider_name: string;
}

// @ts-expect-error Ignore extending incompatible types
export interface UsedVariable extends BuiltinVariable, CustomVariable, Projects.UsedVariables {
  type: 'Builtin' | 'Custom';
}

export interface Project {
  data_connections: DataConnection[];
  id: string;
  name: string;
  project_ready: boolean;
  short_id: string;
  survey_name: string;
  used_variables: UsedVariable[];
}

// Responses

export interface ResponseExchangeCodeSuccess extends ResponseData {
  data_provider_name: string;
  tokens: {
    access_token: string;
    refresh_token: string;
    success: true;
    user_id: string;
    user_name: string;
  };
}

export interface MessageExchangeCodeFailure extends MessageData {
  accepted_scopes: string[];
  data_provider_name: string;
  required_scopes: string[];
  text: string;
}

export interface ResponseExchangeCodeFailure extends ResponseData {
  message: MessageExchangeCodeFailure;
}

export interface ResponseDataSurveyDistribution {
  entity: {
    id: string;
    url: string;
  };
  message: MessageData;
}
