import {Box, Link, Typography, TypographyProps} from "@mui/material";
import React from 'react';

import updateObject from "./utils/updateObject";


interface HelperTextProps {
  text: string;
  url?: string;
  urlText?: string;
  typographyProps?: TypographyProps;
  urlInline?: boolean;
  maxURLLength?: number;
  textPostfix?: boolean;
}


const HelperText: React.FC<HelperTextProps> = ({
  text,
  url = '',
  urlText = '',
  typographyProps = {},
  urlInline = true,
  maxURLLength = -1,
  textPostfix = true,
}) => {
  const defaultTypographyProps: TypographyProps = {
    variant: "caption",
    color: "textSecondary",
  };
  let spacer = " ";

  typographyProps = updateObject(defaultTypographyProps, typographyProps);

  if (urlText === "") {
    urlText = url;
  }

  if (textPostfix) {
    if (urlText !== "") {
      if (!text.endsWith(":")) {
        spacer = ": ";
      }
    } else {
      if (!text.endsWith(".")) {
        spacer = ".";
      }
    }
  }

  if (urlText === url && maxURLLength !== -1) {
    if (urlText.length > maxURLLength + 3) {
      urlText = url.slice(0, maxURLLength + 3) + "...";
    } else {
      urlText = url.slice(0, maxURLLength);
    }
  }


  if (urlInline) {
    return (
      <Box maxWidth={400}>
        <Typography {...typographyProps}>
          {text}
          {url && (
            <>
              {spacer}
              <Link href={url} target="_blank" rel="noopener noreferrer" color="primary">
                {urlText}
              </Link>
            </>
          )}
        </Typography>
      </Box>
    );
  } else {
    return (
      <Box maxWidth={400}>
        <Typography {...typographyProps}>
          {text}
          {url && (
            <>
              {spacer}
              <br/>
              <Link href={url} target="_blank" rel="noopener noreferrer" color="primary">
                {urlText}
              </Link>
            </>
          )}
        </Typography>
      </Box>
    );
  }
};

export default HelperText;
