export type DataProviderType = 'frontend' | 'generic' | 'oauth';

export type SurveyStatus = 'active' | 'inactive' | 'loading' | 'unknown';

export type VariableType = 'Builtin' | 'Custom';

export interface DataOrigin {
  documentation: string;
  endpoint?: string;
  method?: string;
}
