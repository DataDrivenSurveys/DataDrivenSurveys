interface DateFormatParams {
  dateStyle?: 'short' | 'long' | 'full' | 'medium' | undefined;
  timeStyle?: 'short' | 'long' | 'full' | 'medium' | undefined;
  year?: 'numeric' | '2-digit' | undefined;
  month?: 'numeric' | '2-digit' | 'short' | 'long' | 'narrow' | undefined;
  day?: 'numeric' | '2-digit' | undefined;
  hour?: 'numeric' | '2-digit' | undefined;
  minute?: 'numeric' | '2-digit' | undefined;
  second?: 'numeric' | '2-digit' | undefined;
}

function formatDateToLocale(date: Date, formatParams: DateFormatParams = {}): string {
  const defaultParams: DateFormatParams = { dateStyle: 'short', timeStyle: 'long' };

  if (Object.keys(formatParams).length === 0) {
    formatParams = defaultParams;
  }

  // See the following link for formatting information:
  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat
  // https://devhints.io/wip/intl-datetime
  // {
  //   dateStyle: 'short', timeStyle: 'long',
  //   // year: 'numeric', month:'numeric', day: 'numeric',
  //   // hour: '2-digit', minute: '2-digit', second: '2-digit',
  // }
  return new Intl.DateTimeFormat(navigator.language, formatParams).format(date);
}


function formatDateStringToLocale(dateString: string, formatParams: DateFormatParams = {}): string {
  // See the following link for formatting information:
  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat
  // https://devhints.io/wip/intl-datetime
  const date = new Date(dateString);
  return formatDateToLocale(date, formatParams);
}


export { formatDateToLocale, formatDateStringToLocale };
