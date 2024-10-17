import type { JSX } from 'react';

import type { API } from '../../';

export interface SurveyPlatform extends API.SurveyPlatforms.SurveyPlatform {
  icon: JSX.Element | undefined;
  label: string | undefined;
}
