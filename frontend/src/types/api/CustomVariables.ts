export interface FilterOperators {
  Date: [
    {
      label: 'api.custom_variables.filters.operators.date.is';
      value: '__eq__';
    },
    {
      label: 'api.custom_variables.filters.operators.date.is_not';
      value: '__ne__';
    },
    {
      label: 'api.custom_variables.filters.operators.date.is_after';
      value: '__gt__';
    },
    {
      label: 'api.custom_variables.filters.operators.date.is_on_or_after';
      value: '__ge__';
    },
    {
      label: 'api.custom_variables.filters.operators.date.is_before';
      value: '__lt__';
    },
    {
      label: 'api.custom_variables.filters.operators.date.is_on_or_before';
      value: '__le__';
    },
  ];
  Number: [
    {
      label: 'api.custom_variables.filters.operators.number.is';
      value: '__eq__';
    },
    {
      label: 'api.custom_variables.filters.operators.number.is_not';
      value: '__ne__';
    },
    {
      label: 'api.custom_variables.filters.operators.number.is_greater_than';
      value: '__gt__';
    },
    {
      label: 'api.custom_variables.filters.operators.number.is_greater_than_or_equal_to';
      value: '__ge__';
    },
    {
      label: 'api.custom_variables.filters.operators.number.is_less_than';
      value: '__lt__';
    },
    {
      label: 'api.custom_variables.filters.operators.number.is_less_than_or_equal_to';
      value: '__le__';
    },
  ];
  Text: [
    {
      label: 'api.custom_variables.filters.operators.text.is';
      value: '__eq__';
    },
    {
      label: 'api.custom_variables.filters.operators.text.is_not';
      value: '__ne__';
    },
    {
      label: 'api.custom_variables.filters.operators.text.contains';
      value: '__contains__';
    },
    {
      label: 'api.custom_variables.filters.operators.text.does_not_contain';
      value: '__not_contains__';
    },
    {
      label: 'api.custom_variables.filters.operators.text.begins_with';
      value: 'startswith';
    },
    {
      label: 'api.custom_variables.filters.operators.text.ends_with';
      value: 'endswith';
    },
    {
      label: 'api.custom_variables.filters.operators.text.regexp';
      value: 'regexp';
    },
  ];
}
