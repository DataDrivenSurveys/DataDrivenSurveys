export type DataProviderType = 'frontend' | 'oauth' | 'generic';

export type SurveyStatus = 'active' | 'inactive' | 'unknown';

export type VariableType = 'Builtin' | 'Custom';

export interface DataOrigin {
  documentation: string;
  endpoint?: string;
  method?: string;
}
