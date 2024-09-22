import { InputAdornment, Typography } from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers';
import dayjs from 'dayjs';
import React, { JSX } from 'react';

import TextInput from './TextInput';

interface ValueInputProps {
  data_type: 'Date' | 'Number' | 'Text';
  label: string;
  value: Date | number | string;
  unit?: string | null;
  minWidth?: number;
  onChange: (value: string | number) => void;
}

const ValueInput = ({ data_type, label, value, unit, minWidth = 200, onChange }: ValueInputProps): JSX.Element => {
  switch (data_type) {
    case 'Date':
      return (
        <DateTimePicker
          label={label}
          value={dayjs(value)}
          onChange={value => onChange((value as dayjs.Dayjs).toISOString())}
          sx={{ minWidth: minWidth }}
          // textField={params => <TextInput {...params} variant="filled" />}
        />
      );
    case 'Number':
      return (
        <TextInput
          label={label}
          type="number"
          value={value}
          onChange={value => onChange(value)}
          sxStack={{ minWidth: minWidth }}
          inputProps={{
            endAdornment: unit && (
              <InputAdornment position="start">
                <Typography variant={'caption'}>
                  <b>{unit}</b>
                </Typography>
              </InputAdornment>
            ),
          }}
        />
      );
    default:
      return (
        <TextInput label={label} value={value} onChange={value => onChange(value)} sxStack={{ minWidth: minWidth }} />
      );
  }
};

export default ValueInput;
