import React from 'react';

import { TextField, InputAdornment, Box, FormHelperText, Stack } from "@mui/material";
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ClearIcon from '@mui/icons-material/Clear';

// Woprk togeder with useInput hook in /hook folder
const TextInput = ({ label, value, type= "text", onChange, onAfterChange, minLength, maxLength, required = false, showClear = false, helperText, error, sx, ...props }) => {
  return (
    <Stack sx={sx}>
      <TextField
        label={label}
        variant={"outlined"}
        value={value}
        type={type}
        InputProps={{
          maxLength: maxLength,
          startAdornment: (
            <InputAdornment position="start">
              { value?.length >= minLength ? <CheckCircleIcon color={"success"} /> : null }
            </InputAdornment>
          ),
          endAdornment: (
            showClear && value?.length > 0 ? (
              <Box sx={{ cursor: 'pointer' }}>
                  <InputAdornment position="end">
                      <ClearIcon onClick={() => onChange('')} />
                  </InputAdornment>
              </Box>
            ) : null
          )
        }}
        required={required}
        onChange={(e) => {
          onChange(e.target.value);
          onAfterChange && onAfterChange(e.target.value);
        }}
        {...props}
      />
      { helperText && (
        <FormHelperText error={error}>{helperText}</FormHelperText>
      )}
    </Stack>
  );
}

export default TextInput;
