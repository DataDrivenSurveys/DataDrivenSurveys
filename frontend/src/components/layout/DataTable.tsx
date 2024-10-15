import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {
  Checkbox,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Typography,
} from '@mui/material';
import React, { JSX, useCallback, useMemo, useState } from 'react';

import { API } from '../../types';

type SpanDictionaries = Record<string, number[]>;

export interface Row extends API.Projects.UsedVariable {
  id: number;
}

export interface Column {
  field: string;
  headerName: string;
  type?: 'number' | 'string' | 'actions';
  sortable?: boolean;
  spannable?: boolean;
  editable?: boolean;
  align?: 'left' | 'center' | 'right';
  verticalAlign?: 'top' | 'middle' | 'bottom' | 'text-bottom';
  width?: number;
  minWidth?: number;
  maxWidth?: number;
  flex?: number;
  disableClickEventBubbling?: boolean;
  renderCell?: (params: never) => React.ReactNode | JSX.Element;
  sxTableHeaderCell?: React.CSSProperties;
  sxTableBodyCell?: React.CSSProperties;
}

interface DataTableProps {
  rows: Row[];
  columns: Column[];
  selectable?: boolean;
  selectableLabel?: string;
  selectableField?: string;
  onRowSelectChange?: (id: number, rows: Row[]) => Promise<void>;
}

const DataTable = ({
  rows,
  columns,
  selectable = false,
  selectableLabel,
  selectableField,
  onRowSelectChange,
}: DataTableProps): JSX.Element => {
  const [sortField, setSortField] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState(1); // 1 for 'asc' and -1 for 'desc'

  const sortRows = useCallback(
    (rows: Row[]): Row[] => {
      const sortedRows = [...rows];
      if (sortField) {
        sortedRows.sort((a: Row, b: Row): -1 | 0 | 1 => {
          const aValue = a[sortField as keyof Row];
          const bValue = b[sortField as keyof Row];
          if (aValue === null || bValue === null) return 0;
          if (aValue < bValue) {
            return sortDirection === 1 ? -1 : 1;
          }
          if (aValue > bValue) {
            return sortDirection === 1 ? 1 : -1;
          }
          return 0;
        });
      }
      return sortedRows;
    },
    [sortField, sortDirection]
  );

  const sortedRows = useMemo(() => sortRows(rows), [sortRows, rows]);

  // Function to calculate rowSpan values
  const computeRowSpan = (field: string): number[] => {
    let currentFieldValue = null;
    let currentSpan = 0;
    const spans: number[] = [];

    for (let i = 0; i < sortedRows.length; i++) {
      if (sortedRows[i][field as keyof Row] !== currentFieldValue) {
        currentFieldValue = sortedRows[i][field as keyof Row];
        currentSpan = 1;

        for (let j = i + 1; j < sortedRows.length; j++) {
          if (sortedRows[j][field as keyof Row] === currentFieldValue) {
            currentSpan++;
          } else {
            break;
          }
        }

        spans.push(currentSpan);
      } else {
        spans.push(0); // The following rows with the same value get a span of 0
      }
    }

    return spans;
  };

  // Create a dictionary to store row spans for each spannable column
  const spanDictionaries: SpanDictionaries = {};

  columns.forEach(column => {
    if (column.spannable) {
      spanDictionaries[column.field] = computeRowSpan(column.field);
    }
  });

  return (
    <Paper variant="outlined">
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              {selectable && (
                <TableCell>
                  <Stack direction="row" alignItems="center">
                    <Checkbox
                      checked={sortedRows.every(row => row[selectableField as keyof Row] || false)}
                      onChange={event => {
                        const checked = event.target.checked;
                        if (onRowSelectChange) {
                          onRowSelectChange(
                            -1,
                            rows.map(
                              (row: Row): Row => ({
                                ...row,
                                [selectableField as string]: checked,
                              })
                            )
                          );
                        }
                      }}
                    />
                    {selectableLabel && <Typography variant="body1">{selectableLabel}</Typography>}
                  </Stack>
                </TableCell>
              )}
              {columns.map((column, index) => (
                <TableCell key={index} style={{ ...column.sxTableHeaderCell }}>
                  {(Object.hasOwnProperty.call(column, 'sortable') && column.sortable) ||
                  !Object.hasOwnProperty.call(column, 'sortable') ? (
                    <TableSortLabel
                      active={sortField === column.field}
                      direction={sortDirection === 1 ? 'asc' : 'desc'}
                      onClick={() => {
                        const isAsc = sortField === column.field && sortDirection === 1;
                        setSortField(column.field);
                        setSortDirection(isAsc ? -1 : 1);
                      }}
                    >
                      {column.headerName}
                      {sortField === column.field ? (
                        sortDirection === -1 ? (
                          <ExpandMoreIcon />
                        ) : (
                          <ExpandLessIcon />
                        )
                      ) : null}
                    </TableSortLabel>
                  ) : (
                    column.headerName
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedRows.map((row: Row, rowIndex) => (
              <TableRow key={rowIndex}>
                {selectable && (
                  <TableCell>
                    <Checkbox
                      checked={row.enabled || false}
                      onChange={event => {
                        const checked = event.target.checked;
                        rows = rows.map((r: Row): Row => {
                          if (r.id === row.id) {
                            r['enabled'] = checked;
                          }
                          return r;
                        });
                        if (onRowSelectChange) {
                          onRowSelectChange(row.id, rows);
                        }
                      }}
                    />
                  </TableCell>
                )}
                {columns.map((column, columnIndex) => {
                  if (column.spannable && spanDictionaries[column.field][rowIndex] === 0) {
                    return null; // skip rendering for rows with a span of 0
                  }

                  return (
                    <TableCell
                      style={{ ...column.sxTableBodyCell }}
                      key={columnIndex}
                      rowSpan={
                        column.spannable && spanDictionaries[column.field][rowIndex] > 0
                          ? spanDictionaries[column.field][rowIndex]
                          : undefined
                      }
                    >
                      {column.renderCell ? column.renderCell(row as never) : (row as never)[column.field] || ''}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default DataTable;
