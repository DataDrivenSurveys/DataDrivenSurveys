import type { ContainerProps } from '@mui/material';
import type { JSX, ReactNode } from 'react';
import type { To } from 'react-router-dom';

import { Box, Container, Stack } from '@mui/material';
import React from 'react';

import { LoadingPageContent } from '../feedback/Loading';
import Footer from './Footer';
import Header from './Header';
import ScrollContainer from './ScrollContainer';

interface LayoutMainProps {
  backUrl?: To | number;
  children: ReactNode;
  header?: ReactNode;
  headerRightCorner?: ReactNode;
  horizontalContainerProps?: ContainerProps;
  loading?: boolean;
  padding?: number;
  spacing?: number;
  subheader?: ReactNode;
}

const LayoutMain = ({
  backUrl,
  children,
  header,
  headerRightCorner,
  horizontalContainerProps = {},
  loading = false,
  padding = 0,
  spacing = 0,
  subheader,
}: LayoutMainProps): JSX.Element => {
  if (loading) {
    return <LoadingPageContent />;
  }

  return (
    <Stack height="100vh" width="100vw">
      <Header backUrl={backUrl} color="transparent" rightCorner={headerRightCorner}>
        {header}
      </Header>
      {subheader && <Box sx={{ overflow: 'hidden' }}>{subheader}</Box>}
      <ScrollContainer padding={padding} spacing={spacing}>
        <Stack alignItems="center" height="100%" paddingBottom={4} paddingTop={4} width="100%">
          <Container {...horizontalContainerProps}>{children}</Container>
        </Stack>
      </ScrollContainer>
      <Footer />
    </Stack>
  );
};

export default LayoutMain;
