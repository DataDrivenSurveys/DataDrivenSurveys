import { Stack, Typography } from '@mui/material';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

const defaultOptions = {
  value: '',
  minLength: 0,
  maxLength: Infinity,
  required: false,
  label: '',
  helperText: '',
};

const useInput = (options) => {
  options = { ...defaultOptions, ...options };

  const { t } = useTranslation();

  const [value, setValue] = useState(options.value || '');
  const [touched, setTouched] = useState(false);
  const [error, setError] = useState(null);

  const onChange = (value) => {
    setValue(value);
    setTouched(true);
    validate(value);
  };

  const validate = (value) => {
    if (options.required && value.trim() === '') {
      if (touched) {
        setError(t('ui.input.required_field'));
      }
      return false;
    } else if (options.required && options.minLength && value.length < options.minLength) {
      setError(t('ui.input.min_length', { minLength: options.minLength }));
      return false;
    } else if (options.required && options.maxLength && value.length > options.maxLength) {
      setError(t('ui.input.max_length', { maxLength: options.maxLength }));
      return false;
    } else {
      setError(null);
      return true;
    }
  };

  useEffect(() => {
    validate(value);
  }, // eslint-disable-next-line react-hooks/exhaustive-deps
  []);

  return {
    bind: {
      value,
      minLength: options.minLength,
      maxLength: options.maxLength,
      required: options.required,
      onChange,
      label: options.label,
      error: touched && error !== null,
      helperText: (
        <Stack sx={{ pl: 1 }}>
          {touched && error !== null && <Typography variant={'caption'}>{error}</Typography>}
          {options.helperText}
        </Stack>
      ),
    },
    error: error !== null,
    value,
  };
};

export default useInput;
