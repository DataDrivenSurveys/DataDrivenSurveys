export type DataProviderType = "frontend" | "oauth" | "generic";

export type SurveyStatus = "active" | "inactive" | "unknown";

export interface Researcher {
  id: number;
  email: string;
  firstname: string;
  lastname: string;
}

export interface Collaborations {
  project_id: string;
  researcher: Researcher;
}

export interface CustomVariable {
}

export interface DataProvider {
  data_provider_name: string;
  data_provider_type: DataProviderType;
  name: string;
}

export interface DataConnection {
  data_provider: DataProvider;
  data_provider_name: string;
  fields: {
    client_id?: string;
    client_secret?: string;
    project_id?: string;
    information?: string;
  };
  project_id: string;
}

export interface Respondent {
}

export interface SurveyPlatformFields {
  base_url: string;
  survey_id: string;
  survey_name: string;
  survey_platform_api_key: string;
  survey_status: SurveyStatus;
}

export interface BuiltinVariable {
  category: string;
  data_origin: {
    documentation: string;
    endpoint: string;
    method: string;
  }[];
  data_provider: string;
  data_type: string;
  description: string;
  enabled: boolean;
  id: number;
  index: number | null;
  info: string;
  is_indexed_variable: boolean;
  label: string;
  name: string;
  provider_type: DataProviderType;
  qualified_name: string;
  test_value: string;
  test_value_placeholder: string;
  type: string;
  unit: string;
}

interface Project {
  collaborations: Collaborations[];
  creation_date: string;
  custom_variables: CustomVariable[];
  data_connections: DataConnection[];
  id: string;
  last_modified: string;
  last_synced: string | null;
  name: string;
  respondents: Respondent[];
  short_id: string;
  survey_platform_fields: SurveyPlatformFields;
  survey_platform_name: string;
  survey_status: string;
  variables: BuiltinVariable[];
}

export default Project;
