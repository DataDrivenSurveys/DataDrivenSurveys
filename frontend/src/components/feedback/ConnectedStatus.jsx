import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import { LoadingButton } from "@mui/lab";
import { Tooltip } from "@mui/material";
import React from 'react';


const ConnectedStatus = ({ connected }) => {

    return (
        <LoadingButton loading={connected===undefined}>
            {
                connected ?
                    <Tooltip title={"Connected"}>
                        <CheckCircleIcon color={"success"} />
                    </Tooltip>
                :
                    <Tooltip title={"Not Connected"}>
                        { connected === undefined ? <></> : <ErrorIcon color={"error"} />}
                    </Tooltip>
            }

        </LoadingButton>
    )
}

export default ConnectedStatus;
