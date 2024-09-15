import {Bases} from ".";
import {DataProviderType, SurveyStatus} from "../Shared";

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

interface CVAttribute extends Bases.CVAttribute {
  category: string;
}

interface CVSelection {
  attr?: string;
  operator: "max" | "min" | "random";
}

export interface CustomVariable {
  cv_attributes: CVAttribute[];
  data_category: string;
  data_provider: string;
  filters: Bases.CVFilter[];
  id: number;
  selection: CVSelection;
  type: 'Custom';
  variable_name: string;
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
  data_provider: string;
  enabled: boolean;
  id: number;
  provider_type: DataProviderType;
  qualified_name: string;
  type: 'Builtin';
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
  survey_status: string;
  variables: BuiltinVariable[];
}
