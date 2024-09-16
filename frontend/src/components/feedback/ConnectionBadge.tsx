import { Stack, Typography } from '@mui/material';
import React, { JSX } from 'react';
import { useTranslation } from 'react-i18next';

import Logo from '../Logo';

export interface ConnectionBadgeProps {
  name: string;
  size?: number; // in pixels
}

const ConnectionBadge = ({ name, size = 24 }: ConnectionBadgeProps): JSX.Element => {
  const { t } = useTranslation();

  return (
    <Stack direction="row" spacing={1} alignItems={'center'} justifyContent={'flex-start'}>
      <Logo name={name} size={size} />
      <Typography variant={'body1'}><b>{t(`ui.badges.${name.toLowerCase()}.label`)}</b></Typography>
    </Stack>
  );
};


export default ConnectionBadge;
