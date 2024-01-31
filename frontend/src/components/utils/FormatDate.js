function formatDateToLocale(date, formatParams = {}) {
  let defaultParams = {dateStyle: 'short', timeStyle: 'long'};

  if (formatParams.length === 0) {
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


function formatDateStringToLocale(dateString) {
  // See the following link for formatting information:
  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat
  // https://devhints.io/wip/intl-datetime
  const date = new Date(dateString);
  return formatDateToLocale(date);
}


export {formatDateToLocale, formatDateStringToLocale};
