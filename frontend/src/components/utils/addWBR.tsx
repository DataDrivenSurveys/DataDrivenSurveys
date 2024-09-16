import React, { JSX } from 'react';

function addWBR(str: string): (string | JSX.Element)[] {
  const parts = str.split('.');
  return parts.reduce<(string | JSX.Element)[]>((acc, part, index) => {
    if (index === 0) {
      return [part]; // Start with the first part
    } else {
      return [...acc, <wbr key={index} />, '.', part]; // Add <wbr> before the period
    }
  }, []);
}

export default addWBR;
