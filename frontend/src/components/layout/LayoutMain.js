import { Box, Stack } from '@mui/material'

import Header from './Header'
import ScrollContainer from './ScrollContainer'
import Footer from "./Footer";
const LayoutMain = ({
  children,
  backUrl,
  header,
  subheader,
  padding = 0,
  spacing = 0,
  headerRightCorner,
}) => {
  return (
    <>
      <Stack height={'100vh'} width={'100vw'}>
        <Header color="transparent" backUrl={backUrl} rightCorner={headerRightCorner}> {header} </Header>
        {subheader && <Box sx={{ overflow: 'hidden' }}>{subheader}</Box>}
        <ScrollContainer padding={padding} spacing={spacing}>
          <Stack p={4} alignItems="center" height="100%">
            {children}
          </Stack>
        </ScrollContainer>
        <Footer />
      </Stack>
    </>
  )
}

export default LayoutMain
