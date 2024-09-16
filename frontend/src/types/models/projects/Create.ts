import { JSX } from 'react';

import { API } from '../../';

export interface SurveyPlatform extends API.SurveyPlatforms.SurveyPlatform {
  label: string | undefined;
  icon: JSX.Element | undefined;
}
