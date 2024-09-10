import { Box } from "@mui/material";
import React from 'react';

import useEventTracker from "./useEventTracker";

const ClickTracker = ({ children, details, storageKey = "FrontendActivity" }) => {
    const { logEvent } = useEventTracker(storageKey);

    const handleClick = (e) => {
        e.stopPropagation(); // Prevent event from bubbling up
        logEvent(details);
    };

    return <Box onClick={handleClick}>{children}</Box>;
};

export default ClickTracker;
