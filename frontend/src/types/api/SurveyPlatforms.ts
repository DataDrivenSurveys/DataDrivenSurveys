import { ResponseData } from './ResponseReturnValue';

export interface SurveyPlatformFieldData {
  helper_url: string;
}

export type SurveyPlatformFieldVisibilityConditionOperator = 'is_empty' | 'is_not_empty';

export interface SurveyPlatformFieldVisibilityConditionValue {
  field: 'access_token',
  'operator': SurveyPlatformFieldVisibilityConditionOperator
}

export interface SurveyPlatformFieldVisibilityCondition {
  hide?: SurveyPlatformFieldVisibilityConditionValue[];
  show?: SurveyPlatformFieldVisibilityConditionValue[];
}

export interface SurveyPlatformField {
  data: SurveyPlatformFieldData | null;
  disabled?: boolean;
  helper_text: string;
  interaction_effects?: null;
  label: string;
  name: string;
  onClick?: {
    action: string;
    args: Record<string, string>
  };
  required?: boolean;
  type: string;
  value?: string;
  visibility_conditions: SurveyPlatformFieldVisibilityCondition | null;
}

export interface SurveyPlatform {
  fields: SurveyPlatformField[];
  instructions: string;
  instructions_helper_url: string;
  label: string | undefined;
  oauth2?: {
    authorize_url: string;
  };
  value: string;
}

// Response values
export interface ResponseExchangeCodeSuccess extends ResponseData {
  entity: {
    data: {
      access_token: string;
    };
  };
}
