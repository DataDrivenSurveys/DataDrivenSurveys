import { API } from '../../index';

export * as Create from './Create';

export interface DataProvider extends API.Projects.DataProvider {
  id: number;
  api_key?: string;
}

export interface DataConnection extends API.Projects.DataConnection {
  data_provider: DataProvider;
  api_key: string;
}

export interface Project extends API.Projects.Project {
  data_connections: DataConnection[];
}
