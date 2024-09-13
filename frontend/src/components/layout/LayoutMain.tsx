import {Box, Stack} from '@mui/material';
import React, {ReactNode} from 'react';

import Footer from './Footer';
import Header from './Header';
import ScrollContainer from './ScrollContainer';
import {LoadingPageContent} from "../feedback/Loading";

// Define the props interface for LayoutMain
interface LayoutMainProps {
  children: ReactNode;
  backUrl?: string | number; // Can be a URL or a number for browser history navigation
  header?: ReactNode;
  subheader?: ReactNode;
  padding?: number;
  spacing?: number;
  headerRightCorner?: ReactNode;
  loading?: boolean; // Optional prop to display loading spinner while content is loading
}

const LayoutMain: React.FC<LayoutMainProps> = ({
  children,
  backUrl,
  header,
  subheader,
  padding = 0,
  spacing = 0,
  headerRightCorner,
  loading = false, // Default loading to false
}) => {
  if (loading) {
    return (
      <LoadingPageContent/>
    )
  }

  return (
    <Stack height="100vh" width="100vw">
      <Header color="transparent" backUrl={backUrl} rightCorner={headerRightCorner}>
        {header}
      </Header>
      {subheader && <Box sx={{overflow: 'hidden'}}>{subheader}</Box>}
      <ScrollContainer padding={padding} spacing={spacing}>
        <Stack p={4} alignItems="center" height="100%">
          {children}
        </Stack>
      </ScrollContainer>
      <Footer/>
    </Stack>
  );
};

export default LayoutMain;
