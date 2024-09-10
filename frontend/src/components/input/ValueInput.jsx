import { InputAdornment, Typography } from "@mui/material";
import { DateTimePicker } from "@mui/x-date-pickers";
import dayjs from 'dayjs';
import React from 'react';

import TextInput from "./TextInput";

const ValueInput = ({ data_type, label, value, unit, minWidth=200, onChange }) => {

    switch(data_type) {
        case 'Date':
            return (
                <DateTimePicker

                    label={label}
                    value={dayjs(value)}
                    onChange={value => onChange(value.toISOString())}
                    sx={{ minWidth: minWidth }}
                    textField={(params) => <TextInput {...params} variant="filled" />}
                />
            );
        case 'Number':
            return (
                <TextInput
                    label={label}
                    type="number"
                    value={value}
                    onChange={value => onChange(value)}
                    sx={{ minWidth: minWidth }}
                    variant="filled"
                    InputProps={{
                        endAdornment: unit && <InputAdornment position="start"><Typography variant={"caption"}><b>{unit}</b></Typography></InputAdornment>,
                    }}
                />
            );
        default:
            return (
                <TextInput
                    label={label}
                    value={value}
                    onChange={value => onChange(value)}
                    sx={{ minWidth: minWidth }}
                    variant="filled"
                />
            );
    }
};

export default ValueInput;
