import { Bases } from '.';
import { ResponseData } from './ResponseReturnValue';

export interface SurveyPlatformFieldData {
  helper_url: string;
}

export interface SurveyPlatformField extends Bases.Field {
  data: SurveyPlatformFieldData | null;
  helper_text: string;
  interaction_effect?: null;
  onClick?: {
    action: string;
    args: {
      auth_url: string;
    };
  };
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
