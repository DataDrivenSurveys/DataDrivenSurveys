import { formatURL } from './formatString';

function getNonParamURL(url: string): string {
  return url.split('?')[0];
}

function getFrontendBaseURL(): string {
  return process.env.REACT_APP_FRONTEND_URL || window.location.origin;
}

function getAppCreationURL(appCreationURL: string, dataProvider: string, props = {}): string {
  const defaultProps = {
    project_name: '',
    application_description: '',
    organization_name: '',
    organization_url: '',
    dds_about_url: `${getFrontendBaseURL()}/about`,
    dds_tos_url: `${getFrontendBaseURL()}/terms-of-service`,
    dds_privacy_policy_url: `${getFrontendBaseURL()}/privacy-policy`,
    callback_url: `${getFrontendBaseURL()}/dist/redirect/${dataProvider}`,
  };

  props = Object.assign({}, defaultProps, props);

  return formatURL(appCreationURL, props);
}

export { getNonParamURL, getAppCreationURL, getFrontendBaseURL };
