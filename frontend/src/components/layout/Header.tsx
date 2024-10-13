import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { AppBar, Button, PropTypes, Stack } from '@mui/material';
import React, { JSX } from 'react';
import { useTranslation } from 'react-i18next';
import { To, useNavigate } from 'react-router-dom';

interface HeaderProps {
  children: React.ReactNode;
  color: PropTypes.Color | 'transparent' | 'error' | 'info' | 'success' | 'warning';
  backUrl?: To | number;
  rightCorner?: React.ReactNode;
}

const Header = ({ children, color, backUrl, rightCorner }: HeaderProps): JSX.Element => {
  const { t } = useTranslation();

  const navigate = useNavigate();

  return (
    <AppBar
      position="static"
      color={color}
      sx={{
        height: '60px',
        maxWidth: '100vw',
        p: 0,
        position: 'relative',
        zIndex: 1000,
      }}
    >
      <Stack direction="row" alignItems="center" pl={1} pr={1} spacing={1} height="100%">
        {backUrl && (
          <Button
            variant="text"
            color="primary"
            size={'small'}
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate(backUrl as To)}
          >
            {t('ui.layout.button.back')}
          </Button>
        )}
        <Stack flex={1} sx={{ overflow: 'hidden' }}>
          {children}
        </Stack>
        {rightCorner}
      </Stack>
    </AppBar>
  );
};

export default Header;
