import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ClearIcon from '@mui/icons-material/Clear';
import {TextField, InputAdornment, Box, FormHelperText, Stack} from "@mui/material";
import React from 'react';

interface TextInputProps {
  label: string;
  value: string;
  type?: "text" | "password" | "number";
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
}

// Work together with useInput hook in /hook folder
const TextInput = ({
  label,
  value,
  type = "text",
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
  return (
    <Stack sx={sxStack}>
      <TextField
        label={label}
        variant={"outlined"}
        value={value}
        type={type}
        autoFocus={autoFocus}
        inputProps={{
          maxLength: maxLength,
          startAdornment: (
            <InputAdornment position="start">
              {minLength && value?.length >= minLength ? <CheckCircleIcon color={"success"}/> : null}
            </InputAdornment>
          ),
          endAdornment: (
            showClear && value?.length > 0 ? (
              <Box sx={{cursor: 'pointer'}}>
                <InputAdornment position="end">
                  <ClearIcon onClick={() => onChange('')}/>
                </InputAdornment>
              </Box>
            ) : null
          )
        }}
        required={required}
        onChange={(e) => {
          onChange(e.target.value);
          if (onAfterChange) {
            onAfterChange(e.target.value)
          }
        }}
        {...props}
      />
      {helperText && (
        <FormHelperText error={error}>{helperText}</FormHelperText>
      )}
    </Stack>
  );
}

export default TextInput;
