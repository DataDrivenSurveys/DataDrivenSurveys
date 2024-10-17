import type { DataProviderType } from '../Shared';

export interface RespondentTempTokens {
  access_token: string;
  data_provider_name: string;
  refresh_token: string;
  success: boolean;
  user_id: string;
  user_name: string;
}

export interface DataProvider {
  type: DataProviderType;
  authorize_url: string;
  client_id: string;
  data_provider_name: string;
  token?: RespondentTempTokens | null;
  was_used: boolean;
}
