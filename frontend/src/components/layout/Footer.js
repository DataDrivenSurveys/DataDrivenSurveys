import React from 'react';
import {Box, Container, Typography, Grid, Link, Stack, AppBar} from '@mui/material';
import {Facebook, Twitter, Instagram} from '@mui/icons-material';

function Footer() {
  return (
    <AppBar position="static" color="transparent">
      <Stack
        direction="row"
        justifyContent="center"
        alignItems="center"
        spacing={4}
        pl={1}
        pr={1}
        height="100%"
        padding={2}
      >
        <Link href="/privacy-policy" color="primary">Privacy Policy</Link>

        <Link href="/terms-of-service" color="primary">Terms of Service</Link>

        <Typography variant="body1" align="center">
          © 2024 DataDriven Surveys (DDS)
        </Typography>
      </Stack>
    </AppBar>
  );
}

export default Footer;
