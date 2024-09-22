import { Box } from '@mui/material';
import React, { JSX } from 'react';

import useEventTracker from './useEventTracker';

interface ClickTrackerProps {
  children: React.ReactNode;
  details: Record<string, string>;
  storageKey?: string;
}

const ClickTracker = ({ children, details, storageKey = 'FrontendActivity' }: ClickTrackerProps): JSX.Element => {
  const { logEvent } = useEventTracker(storageKey);

  const handleClick = (e: { stopPropagation: () => void }): void => {
    e.stopPropagation(); // Prevent event from bubbling up
    logEvent(details);
  };

  return <Box onClick={handleClick}>{children}</Box>;
};

export default ClickTracker;
