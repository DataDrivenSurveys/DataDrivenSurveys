import { Stack, Typography } from '@mui/material';
import { useState, useEffect } from 'react';

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
            if(touched){
                setError(`Field is required`);
            }
            return false;
        } else if (options.required && options.minLength && value.length < options.minLength) {
            setError(`Must be at least ${options.minLength} characters`);
            return false;
        } else if (options.required && options.maxLength && value.length > options.maxLength) {
            setError(`Must be less than ${options.maxLength} characters`);
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
                <Stack sx={{pl:1}}>
                  {touched && error !== null && <Typography variant={"caption"}>{error}</Typography>}
                  {options.helperText}
                </Stack>
              )
        },
        error: error !== null,
        value,
    };
};

export default useInput;