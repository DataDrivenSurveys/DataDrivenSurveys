import { Box, Container, ContainerProps, Stack } from '@mui/material';
import React, { JSX, ReactNode } from 'react';
import { To } from 'react-router-dom';

import Footer from './Footer';
import Header from './Header';
import ScrollContainer from './ScrollContainer';
import { LoadingPageContent } from '../feedback/Loading';

interface LayoutMainProps {
  children: ReactNode;
  backUrl?: To | number;
  header?: ReactNode;
  subheader?: ReactNode;
  padding?: number;
  spacing?: number;
  headerRightCorner?: ReactNode;
  horizontalContainerProps?: ContainerProps;
  loading?: boolean;
}

const LayoutMain = ({
  children,
  backUrl,
  header,
  subheader,
  padding = 0,
  spacing = 0,
  headerRightCorner,
  horizontalContainerProps = {},
  loading = false,
}: LayoutMainProps): JSX.Element => {
  if (loading) {
    return <LoadingPageContent />;
  }

  return (
    <Stack height="100vh" width="100vw">
      <Header color="transparent" backUrl={backUrl} rightCorner={headerRightCorner}>
        {header}
      </Header>
      {subheader && <Box sx={{ overflow: 'hidden' }}>{subheader}</Box>}
      <ScrollContainer padding={padding} spacing={spacing}>
        <Stack paddingTop={4} paddingBottom={4} alignItems="center" height="100%" width="100%">
          <Container {...horizontalContainerProps}>{children}</Container>
        </Stack>
      </ScrollContainer>
      <Footer />
    </Stack>
  );
};

export default LayoutMain;
