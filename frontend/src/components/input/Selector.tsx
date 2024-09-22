import { FormControl, FormControlLabel, Radio, RadioGroup } from '@mui/material';
import React, { JSX, useCallback, useState } from 'react';

interface SelectorProps {
  selected: string;
  options: string[];
  onSelect: (value: React.SetStateAction<string>) => void;
}

const Selector = ({ selected, options, onSelect }: SelectorProps): JSX.Element => {
  const [selectedOption, setSelectedOption] = useState(selected);

  const handleChange = useCallback(
    (event: { target: { value: React.SetStateAction<string> } }) => {
      setSelectedOption(event.target.value);
      onSelect(event.target.value);
    },
    [onSelect]
  );

  return (
    <FormControl component="fieldset">
      <RadioGroup value={selectedOption} onChange={handleChange}>
        {options.map((option, index) => (
          <FormControlLabel key={index} value={option} control={<Radio />} label={option} />
        ))}
      </RadioGroup>
    </FormControl>
  );
};

export default Selector;
