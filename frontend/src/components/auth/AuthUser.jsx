import React from 'react';
import { useState } from "react";

import { useAuth } from "../../context/AuthContext";
import UserAvatar from "../layout/UserAvatar";
import UserContextMenu from "../layout/UserContextMenu";

const AuthUser = () => {
    const { user } = useAuth();

    const [anchorElUser, setAnchorElUser] = useState(null);
    const handleOpenUserMenu = (event) => setAnchorElUser(event.currentTarget)
    const handleCloseUserMenu = () => setAnchorElUser(null)

    return (
        user && (
            <>
            <UserAvatar
              firstname={user.firstname}
              lastname={user.lastname}
              email={user.email}
              onCLick={handleOpenUserMenu}
            />
            <UserContextMenu
              anchorElUser={anchorElUser}
              handleCloseUserMenu={handleCloseUserMenu}
            />
            </>
          )
    )
}

export default AuthUser;
