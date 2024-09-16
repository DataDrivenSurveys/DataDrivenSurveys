import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { Box, FormControl, IconButton, Input, InputAdornment, InputLabel, Typography } from '@mui/material';
import React, { JSX } from 'react';

import { useSnackbar } from '../../context/SnackbarContext';


interface CopyClipboardProps {
  label?: string;
  leadingLabel?: boolean;
  what: string;
  labelProps?: object;
}


const CopyClipboard = ({
  label,
  what,
  labelProps = {},
  leadingLabel = false,
}: CopyClipboardProps): JSX.Element => {
  const { showBottomCenter: showSnackbar } = useSnackbar();

  return (
    <Box>
      <FormControl variant="standard">
        {(!leadingLabel && label) && <InputLabel {...labelProps} >{label}</InputLabel>}
        <Input
          type={'text'}
          value={what}
          style={{ width: 300 }}
          inputProps={{
            readOnly: true,
          }}
          startAdornment={(leadingLabel && label) &&
            <InputAdornment position="start"><Typography {...labelProps}>{label}</Typography></InputAdornment>
          }
          endAdornment={
            <InputAdornment position="end">
              <IconButton
                component="label"
                size="small"
                onClick={async () => {
                  await navigator.clipboard.writeText(what);
                  showSnackbar('Copied to clipboard');
                }}>
                <ContentCopyIcon />
              </IconButton>
            </InputAdornment>
          }
        />
      </FormControl>
    </Box>
  );
};


export default CopyClipboard;
