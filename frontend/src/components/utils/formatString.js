function formatString(string, values) {
  let result = string;

  for (const key in values) {
    // Replace all occurrences of the placeholder
    result = result.replace(new RegExp(`{${key}}`, 'g'), values[key]);
  }

  return result;
}

function formatURL(string, values) {
  let result = string;

  for (const key in values) {
    // Replace all occurrences of the placeholder
    result = result.replace(new RegExp(`{${key}}`, 'g'), encodeURIComponent(values[key]));
  }

  return result;
}


export {formatString, formatURL};

export default formatString;
