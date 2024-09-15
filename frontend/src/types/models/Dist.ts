import {DataProviderType} from "../Shared";

export interface RespondentTempTokens {
  data_provider_name: string;
  access_token: string;
  refresh_token: string;
  success: boolean;
  user_id: string;
  user_name: string;
}

export interface DataProvider {
  authorize_url: string;
  client_id: string;
  data_provider_name: string;
  token?: RespondentTempTokens | null;
  type: DataProviderType;
  was_used: boolean;
}
