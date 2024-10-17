import type { API } from '../../index';

export * as Create from './Create';

export interface DataProvider extends API.Projects.DataProvider {
  api_key?: string;
  id: number;
}

export interface DataConnection extends API.Projects.DataConnection {
  api_key: string;
  data_provider: DataProvider;
}

export interface Project extends API.Projects.Project {
  data_connections: DataConnection[];
}
