import React, { JSX, useState } from 'react';

import { useAuth } from '../../context/AuthContext';
import UserAvatar from '../layout/UserAvatar';
import UserContextMenu from '../layout/UserContextMenu';

const AuthUser = (): JSX.Element | null => {
  const { user } = useAuth();

  const [anchorElUser, setAnchorElUser] = useState<HTMLElement | null>(null);
  const handleOpenUserMenu = (event: React.MouseEvent<HTMLElement>): void => setAnchorElUser(event.currentTarget as HTMLElement);
  const handleCloseUserMenu = (): void => setAnchorElUser(null);

  return (
    user && (
      <>
        <UserAvatar
          firstname={user.firstname}
          lastname={user.lastname}
          email={user.email}
          collapsed={false}
          onCLick={handleOpenUserMenu}
        />
        <UserContextMenu
          anchorElUser={anchorElUser}
          handleCloseUserMenu={handleCloseUserMenu}
        />
      </>
    )
  );
};

export default AuthUser;
