import type { DataProviderType, SurveyStatus } from '../Shared';
import type { Bases, ResponseData } from './index';

export interface Researcher {
  email: string;
  firstname: string;
  id: number;
  lastname: string;
}

export interface Collaborations {
  project_id: string;
  researcher: Researcher;
}

interface CVAttribute extends Bases.CVAttribute {
  category: string;
  enabled: boolean;
}

interface CVSelection {
  attr?: string;
  operator: 'max' | 'min' | 'random';
}

export interface CustomVariable {
  type: 'Custom';
  cv_attributes: CVAttribute[];
  data_category: string;
  data_provider: string;
  enabled: boolean;
  filters: Bases.CVFilter[];
  id: number;
  selection: CVSelection;
  variable_name: string;
}

export interface DataProviderField extends Bases.Field {
  content?: string;
}

export interface DataProvider extends Bases.Provider {
  app_creation_url: string;
  app_required: boolean;
  callback_url: string;
  data_provider_name: string;
  data_provider_type?: DataProviderType;
  dds_app_creation_instructions: string;
  fields: DataProviderField[];
  name?: string;
  oauth2?: { redirect_uri: string };
}

export interface DataConnection {
  data_provider: DataProvider;
  data_provider_name: string;
  fields: {
    client_id?: string;
    client_secret?: string;
    information?: string;
    project_id?: string;
  };
  project_id: string;
}

export interface Distribution {
  id: number;
  url: string;
}

export interface Respondent {
  distribution: Distribution;
  id: string;
  project_id: string;
}

export interface SurveyPlatformFields {
  base_url: string;
  directory_id?: string;
  mailing_list_id?: string;
  survey_id: string;
  survey_name: string;
  survey_platform_api_key: string;
  survey_status: SurveyStatus;
}

export interface BuiltinVariable extends Bases.BuiltinVariable {
  type: 'Builtin';
  data_provider: string;
  enabled: boolean;
  id: number;
  provider_type: DataProviderType;
  qualified_name: string;
}

// @ts-expect-error Intentionally extending interfaces in an incompatible way
export interface UsedVariable extends BuiltinVariable, CustomVariable {
  type: 'Builtin' | 'Custom';
}

export interface Project {
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
  survey_status: SurveyStatus;
  variables: BuiltinVariable[];
}

export interface ResponseCreateProjectSuccess extends ResponseData {
  entity: Project;
}

// /projects/{project_id}/survey_platform/check_connection
export interface SurveyPlatformCheckConnectionSuccess {
  active: boolean;
  connected: boolean;
  exists: boolean;
  id: number | null;
  survey_name: string;
  survey_status: SurveyStatus;
}
