import LogoutIcon from '@mui/icons-material/Logout';
import { Button, Menu, PopoverVirtualElement, Stack } from '@mui/material';
import React, { JSX } from 'react';
import { useTranslation } from 'react-i18next';

import { useAuth } from '../../context/AuthContext';

interface UserContextMenuProps {
  anchorElUser: Element | (() => Element) | PopoverVirtualElement | (() => PopoverVirtualElement) | null | undefined;
  handleCloseUserMenu: () => void;
}

const UserContextMenu = ({ anchorElUser, handleCloseUserMenu }: UserContextMenuProps): JSX.Element => {
  const { t } = useTranslation();

  const { signout } = useAuth();

  return (
    <Menu
      sx={{ mt: '40px' }}
      id="menu-appbar"
      anchorEl={anchorElUser}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      keepMounted
      transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      open={Boolean(anchorElUser)}
      onClose={handleCloseUserMenu}
    >
      <Stack padding={1} spacing={2} alignItems={'flex-start'}>
        <Button onClick={() => signout()} startIcon={<LogoutIcon />}>
          {t('ui.auth.button.signout')}
        </Button>
      </Stack>
    </Menu>
  );
};

export default UserContextMenu;
