import {Bases} from ".";
import {MessageData} from "./ResponseReturnValue";
import {DataOrigin, DataProviderType} from "../Shared";

export interface DataConnection {
  data_provider: {
    data_provider_name: string;
    data_provider_type: DataProviderType;
    name: string;
  };
}

export interface BuiltinVariable {
  data_provider: string;
  variable_name: string;
  description: string;
  data_origin: DataOrigin[];
  type: 'Builtin';
}

export interface CVFilter extends Bases.CVFilter {
  attribute: Bases.CVAttribute;
}

export interface CVSelectionOperator {
  strategy: "_max_strategy" | "_min_strategy" | "_random_strategy";
  operator: "max" | "min" | "random";
}

export interface CVSelection {
  operator: CVSelectionOperator;
  attribute: Bases.CVAttribute | null;
}

export interface CustomVariableData {
  variable_name: string;
  qualified_name: string;
  data_category: Bases.DataCategory;
  attributes: Bases.CVAttribute[];
  filters: CVFilter[];
  selection: CVSelection;
}

export interface CustomVariable {
  data_provider: string;
  variable_name: string;
  data: CustomVariableData;
  data_origin: DataOrigin[];
  type: 'Custom';
}

export interface DataProvider {
  data_provider_name: string;
  type: DataProviderType;
  client_id: string;
  authorize_url: string;
}

export type UsedVariable = BuiltinVariable | CustomVariable

export interface Project {
  id: string;
  short_id: string;
  name: string;
  survey_name: string;
  data_connections: DataConnection[];
  project_ready: boolean;
  used_variables: UsedVariable[];
}


export interface ResponseDataSurveyDistribution {
  message: MessageData;
  entity: {
    id: string;
    url: string;
  }
}
