import {Link, Typography} from "@mui/material";
import React from 'react';
import {useTranslation} from 'react-i18next';

import ConnectionBadge from "../../feedback/ConnectionBadge";
import DataTable from "../../layout/DataTable";
import addWBR from "../../utils/addWBR";
import {formatDateStringToLocale} from "../../utils/FormatDate";

interface CustomVariable {
  data_category: { label: string };
  selection: { attribute: { label: string, data_type: string }, operator: { operator: string } };
  filters: { attribute: { label: string, data_type: string, unit: string }, operator: string, value: any }[];
}

function formatCustomVariableDescription(custom_variable: CustomVariable, t: any): string {
  const data_category = custom_variable.data_category;
  const selection = custom_variable.selection;

  let type = 'random';
  let attributeName = '';

  if (selection.attribute !== null) {
    type = selection.attribute.data_type === 'Date' ? 'time' : 'quantity';
    attributeName = t(selection.attribute.label);
  }

  let description = `${
    t(`api.custom_variables.used_variables.selection.${selection.operator.operator}.${type}`,
      {data_category: t(data_category.label), attribute_name: attributeName})
  }`;

  if (custom_variable.filters.length > 0) {
    const filtersPhrase = custom_variable.filters.map((filter) => {
      let value = '';
      switch (filter.attribute.data_type) {
        case 'Date':
          value = formatDateStringToLocale(filter.value);
          break;
        case 'Number':
          value = Intl.NumberFormat().format(filter.value);
          break;
        default:
          value = `'${filter.value}'`;
          break;
      }

      return `${filter.attribute.label} ${t(filter.operator)} ${value} ${filter.attribute.unit || ''}`.trim();
    }).join('; ');

    description = `${description} ${t('api.custom_variables.used_variables.filters')} ${filtersPhrase}`;
  }

  // Remove whitespace and add full stop at the end of the description.
  description = `${description.trim()}.`;

  return description;
}


interface UsedVariable {
  // data: { custom_variable: CustomVariable };
  data: CustomVariable;
  description: string;
  type: string;
  data_origin: { method: string, endpoint: string, documentation: string }[];
  data_provider: string;
  variable_name: string;
}

interface UsedVariablesTableProps {
  used_variables: UsedVariable[];
}

const UsedVariablesTable = ({used_variables: initial_variables}: UsedVariablesTableProps): JSX.Element => {
  const {t} = useTranslation();

  const used_variables = initial_variables?.map((variable) => ({
    ...variable,
    description: variable.type === 'Custom' ? formatCustomVariableDescription(variable.data, t) : variable.description,
  }));

  return (
    <DataTable
      columns={[
        {
          field: 'data_provider',
          headerName: t('ui.respondent.connection.table.data_provider_name'),
          minWidth: 90,
          renderCell: (params: UsedVariable) => {
            return (
              <ConnectionBadge name={params.data_provider}/>
            )
          }
        },
        {
          field: 'type',
          headerName: t('ui.respondent.connection.table.type'),
          minWidth: 100,
          renderCell: (params: UsedVariable) => {
            return (
              <Typography variant="body2">{t(params.type)}</Typography>
            )
          }
        },
        {
          field: 'variable_name',
          headerName: t('ui.respondent.connection.table.variable_name'),
          minWidth: 150,
          renderCell: (params: UsedVariable) => {
            return (
              <Typography variant="body2">{addWBR(t(params.variable_name))}</Typography>
            )
          }
        },
        {
          field: 'description',
          headerName: t('ui.respondent.connection.table.variable_description'),
          minWidth: 150
        },
        {
          field: 'data_origin',
          headerName: t('ui.respondent.connection.table.data_origin'),
          minWidth: 100,
          renderCell: (data: UsedVariable) => {
            return data.data_origin?.map(({documentation}, index) => {
              return (
                <Link key={`origin_${index}`} href={documentation} target={"_blank"}
                      rel="noreferrer">{documentation}</Link>
              )
            })
          }
        }
      ]}
      rows={used_variables}
    />
  )
}

export default UsedVariablesTable;
