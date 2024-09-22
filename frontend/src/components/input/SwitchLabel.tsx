import { FormControl, FormControlLabel, FormGroup, FormLabel, Switch } from '@mui/material';
import React, { JSX } from 'react';

interface SwitchLabelProps {
  label: string;
  checked: boolean;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const SwitchLabel = ({ label, checked, onChange }: SwitchLabelProps): JSX.Element => {
  return (
    <FormControl component="fieldset" variant="standard">
      <FormLabel component="legend">{label}</FormLabel>
      <FormGroup>
        <FormControlLabel control={<Switch checked={checked} onChange={onChange} />} label={checked ? 'On' : 'Off'} />
      </FormGroup>
    </FormControl>
  );
};

export default SwitchLabel;
