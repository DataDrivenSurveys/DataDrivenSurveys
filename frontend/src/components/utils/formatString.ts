type Values = Record<string, string>

function formatString(string: string, values: Values): string {
  let result = string;

  for (const key in values) {
    // Replace all occurrences of the placeholder
    result = result.replace(new RegExp(`{${key}}`, 'g'), values[key]);
  }

  return result;
}

function formatURL(string: string, values: Values): string {
  let result = string;

  for (const key in values) {
    // Replace all occurrences of the placeholder
    result = result.replace(new RegExp(`{${key}}`, 'g'), encodeURIComponent(values[key]));
  }

  return result;
}


export { formatString, formatURL };

export default formatString;
