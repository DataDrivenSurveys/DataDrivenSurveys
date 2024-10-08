/* eslint-disable react/prop-types */

import { Stack } from '@mui/material';
import React, { forwardRef, ReactNode } from 'react';

interface ScrollContainerProps {
  children: ReactNode;
  spacing?: number;
  padding?: number;
  dashed?: boolean;
}

/**
 * Fill the parent container with a scrollable container.
 * Use absolute positioning to get the children out of the flow of the parent container,
 * insuring the children do not affect the size of the parent container.

 * The parent container must have a height and width set.
 */
const ScrollContainer = forwardRef<HTMLDivElement, ScrollContainerProps>(
  // Use forwardRef with proper typing for ref
  ({ children, spacing = 0, padding = 0, dashed = false }, ref) => {
    return (
      <Stack
        ref={ref}
        position="relative"
        flex={1}
        overflow="auto"
        height="100%"
        width="100%"
        border={dashed ? '1px dashed red' : 0}
      >
        <Stack
          position="absolute"
          alignItems="center"
          top={0}
          left={0}
          bottom={0}
          right={0}
          spacing={spacing}
          padding={padding}
        >
          {children}
        </Stack>
      </Stack>
    );
  }
);

ScrollContainer.displayName = 'ScrollContainer';
export default ScrollContainer;
