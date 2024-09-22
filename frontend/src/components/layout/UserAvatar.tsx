import { Avatar, Collapse, IconButton, ListItemText, Stack, Typography } from '@mui/material';
import React, { JSX } from 'react';

interface UserAvatarProps {
  firstname: string;
  lastname: string;
  email: string;
  collapsed: boolean;
  onCLick: (event: React.MouseEvent<HTMLElement>) => void;
}

const UserAvatar = ({ firstname, lastname, email, collapsed, onCLick }: UserAvatarProps): JSX.Element => {
  return (
    <Stack direction="row" onClick={onCLick} sx={{ cursor: 'pointer' }}>
      <IconButton sx={{ p: 1 }}>
        <Avatar alt={`${firstname} ${lastname}`} sx={{ width: 32, height: 32 }} />
      </IconButton>
      <Collapse orientation="horizontal" in={!collapsed}>
        <ListItemText
          primary={<Typography variant="body2">{`${firstname} ${lastname}`}</Typography>}
          secondary={<Typography variant="caption">{email}</Typography>}
        />
      </Collapse>
    </Stack>
  );
};

export default UserAvatar;
