import { FormControl, FormControlLabel, Radio, RadioGroup } from "@mui/material";
import { useCallback, useState } from "react";

const Selector = ({selected, options, onSelect}) => {
    const [selectedOption, setSelectedOption] = useState(selected);

    const handleChange = useCallback((event) => {
        setSelectedOption(event.target.value);
        onSelect(event.target.value);
    }, [onSelect]);

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