import { Box, Stack } from '@mui/material';
import Image from 'next/image';
import React, { JSX } from 'react';

interface UnauthorizedProps {
  children: React.ReactNode;
}

const Unauthorized = ({ children }: UnauthorizedProps): JSX.Element => {
  return (
    <Stack
      alignItems="center"
      justifyContent="center"
      height={'100vh'}
      width={'100vw'}
    >
      <Box sx={{ width: '20%', height: '20%', position: 'relative' }}>
        <Image src="/svg/unauthorized.svg" alt="Unauthorized" layout="fill" />
      </Box>
      <Stack spacing={1} padding={2} alignItems="center">
        {children}
      </Stack>
    </Stack>
  );
};

export default Unauthorized;
