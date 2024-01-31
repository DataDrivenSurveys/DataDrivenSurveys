import { Menu, Button, Stack } from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import { useAuth } from '../../context/AuthContext';

import { useTranslation } from 'react-i18next';

const UserContextMenu = ({ anchorElUser, handleCloseUserMenu }) => {
  const { t } = useTranslation();

  const {  signout } = useAuth();
  
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
  )
}

export default UserContextMenu
