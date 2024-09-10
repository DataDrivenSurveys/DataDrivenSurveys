import { Snackbar, Paper, Box, Stack, Typography } from '@mui/material'
import { useTheme } from '@mui/material'
import React from 'react';

import { useSnackbar } from '../../context/SnackbarContext'

const SnackbarFeedback = () => {
  const theme = useTheme()
  const {
    snackbar: {
      position: { vertical, horizontal },
      open,
      message,
      severity = 'success',
    },
    hide,
  } = useSnackbar()
  return (
    <Snackbar
      sx={{ mt: 5 }}
      anchorOrigin={{ vertical, horizontal }}
      open={open}
      autoHideDuration={3000}
      onClose={hide}
    >
      <Paper elevation={4}>
        <Stack direction="row" sx={{ p: 0 }}>
          <Box
            sx={{
              minWidth: 8,
              maxWidth: 8,
              backgroundColor: theme.palette[severity]?.main,
            }}
          ></Box>
          <Box sx={{ pl: 2, pr: 2, pt: 1, pb: 1 }}>
            <Typography variant="caption">{message}</Typography>
          </Box>
        </Stack>
      </Paper>
    </Snackbar>
  )
}

export default SnackbarFeedback
