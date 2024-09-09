import { FormControl, FormControlLabel, FormGroup, FormLabel, Switch } from "@mui/material";

const SwitchLabel = ({ label, checked, onChange }) => {
    return (
        <FormControl component="fieldset" variant="standard">
            <FormLabel component="legend">{label}</FormLabel>
            <FormGroup>
                <FormControlLabel
                    control={<Switch checked={checked} onChange={onChange} />}
                    label={checked ? "On" : "Off"}
                />
            </FormGroup>
        </FormControl>
    )
}

export default SwitchLabel;