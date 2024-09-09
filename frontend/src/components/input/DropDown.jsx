import React from 'react';
import { FormControl, InputLabel, MenuItem, Select, Stack, Typography } from "@mui/material";

const DropDown = ({ items, label, value, onChange, ...props }) => {
  return (
    <FormControl variant="filled" sx={{ m: 1, minWidth: 120 }} {...props}>
      <InputLabel id="dropdown-filled-label">{label}</InputLabel>
      <Select
        labelId="dropdown-filled-label"
        id="dropdown-filled"
        value={value || ""}
        onChange={onChange}
      >
        {items.map((item, index) => (
          <MenuItem key={index} value={item.value}>
            <Stack direction="row" alignItems="center">
              {item.icon && 
                <Stack mr={1} alignItems="center" justifyContent={"center"}>
                  {item.icon}
                </Stack>
              }
              <Typography variant="caption">{item.label}</Typography>
            </Stack>
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}

export default DropDown;
