import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import { LoadingButton } from '@mui/lab';
import { Tooltip } from '@mui/material';
import React, { JSX } from 'react';

interface ConnectedStatusProps {
  connected?: boolean; // undefined if not connected, true if connected, false if disconnected.
}

const ConnectedStatus = ({ connected }: ConnectedStatusProps): JSX.Element => {
  return (
    <LoadingButton loading={connected === undefined}>
      {connected ? (
        <Tooltip title={'Connected'}>
          <CheckCircleIcon color={'success'} />
        </Tooltip>
      ) : (
        <Tooltip title={'Not Connected'}>{connected === undefined ? <></> : <ErrorIcon color={'error'} />}</Tooltip>
      )}
    </LoadingButton>
  );
};

export default ConnectedStatus;
