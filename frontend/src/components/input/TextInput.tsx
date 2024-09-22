import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ClearIcon from '@mui/icons-material/Clear';
import { Box, FormHelperText, InputAdornment, Stack, TextField } from '@mui/material';
import React, { JSX } from 'react';

interface TextInputProps {
  label: string;
  value: Date | string | number;
  type?: 'text' | 'password' | 'number';
  onChange: (value: string) => void;
  onAfterChange?: (value: string) => void;
  minLength?: number;
  maxLength?: number;
  autoFocus?: boolean;
  required?: boolean;
  showClear?: boolean;
  helperText?: string | JSX.Element;
  error?: boolean;
  sxStack?: object;
  [key: string]: any;
}

// Work together with useInput hook in /hook folder
const TextInput = ({
  label,
  value,
  type = 'text',
  onChange,
  onAfterChange,
  minLength,
  maxLength,
  autoFocus = false,
  required = false,
  showClear = false,
  helperText,
  error,
  sxStack,
  ...props
}: TextInputProps): JSX.Element => {
  value = String(value);
  return (
    <Stack sx={sxStack}>
      <TextField
        label={label}
        variant={'outlined'}
        value={value}
        type={type}
        autoFocus={autoFocus}
        inputProps={{
          maxLength: maxLength,
          startAdornment: (
            <InputAdornment position="start">
              {minLength && value?.length >= minLength ? <CheckCircleIcon color={'success'} /> : null}
            </InputAdornment>
          ),
          endAdornment:
            showClear && value?.length > 0 ? (
              <Box sx={{ cursor: 'pointer' }}>
                <InputAdornment position="end">
                  <ClearIcon onClick={() => onChange('')} />
                </InputAdornment>
              </Box>
            ) : null,
        }}
        required={required}
        onChange={e => {
          onChange(e.target.value);
          if (onAfterChange) {
            onAfterChange(e.target.value);
          }
        }}
        {...props}
      />
      {helperText && <FormHelperText error={error}>{helperText}</FormHelperText>}
    </Stack>
  );
};

export default TextInput;
