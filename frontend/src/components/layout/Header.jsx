
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { AppBar, Button, Stack } from '@mui/material'
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

const Header = ({ children, color, backUrl, rightCorner }) => {

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
      <Stack
        direction="row"
        alignItems="center"
        pl={1}
        pr={1}
        spacing={1}
        height="100%"
      >
        {backUrl && (
          <Button
            variant="text"
            color="primary"
            size={"small"}
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate(backUrl)}>
            {t('ui.layout.button.back')}
          </Button>
        )}
        <Stack flex={1} sx={{ overflow: 'hidden' }}>
          {children}
        </Stack>

        {rightCorner}
      </Stack>
    </AppBar>
  )
}

export default Header
