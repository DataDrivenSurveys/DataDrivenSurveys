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
  Typography
} from "@mui/material";
import {useCallback, useMemo, useState} from "react";
import React from 'react';

interface SpanDictionaries {
  [key: string]: number[];
}

interface Column {
  field: string;
  headerName: string;
  type?: 'number' | 'string' | 'actions';
  sortable?: boolean;
  spannable?: boolean;
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
  rows: object[];
  columns: Column[];
  selectable?: boolean;
  selectableLabel?: string;
  selectableField?: string;
  onRowSelectChange?: (row: object, rows: object[]) => void;
}

const DataTable = ({
  rows, columns, selectable, selectableLabel, selectableField, onRowSelectChange
}: DataTableProps) => {
  const [sortField, setSortField] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState(1); // 1 for 'asc' and -1 for 'desc'

  const sortRows = useCallback((rows: object[]): { [key: string]: any }[] => {
    const sortedRows = [...rows];
    if (sortField) {
      sortedRows.sort((a: any, b: any) => {
        if (a[sortField] < b[sortField]) {
          return sortDirection === 1 ? -1 : 1;
        }
        if (a[sortField] > b[sortField]) {
          return sortDirection === 1 ? 1 : -1;
        }
        return 0;
      });
    }
    return sortedRows;
  }, [sortField, sortDirection]);

  const sortedRows = useMemo(() => sortRows(rows), [sortRows, rows]);

  // Function to calculate rowSpan values
  const computeRowSpan = (field: string): number[] => {
    let currentFieldValue = null;
    let currentSpan = 0;
    const spans: number[] = [];

    for (let i = 0; i < sortedRows.length; i++) {
      if (sortedRows[i][field] !== currentFieldValue) {
        currentFieldValue = sortedRows[i][field];
        currentSpan = 1;

        for (let j = i + 1; j < sortedRows.length; j++) {
          if (sortedRows[j][field] === currentFieldValue) {
            currentSpan++;
          } else {
            break;
          }
        }

        spans.push(currentSpan);
      } else {
        spans.push(0); // subsequent rows with the same value get a span of 0
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
                      checked={sortedRows.every(row => row[selectableField as keyof typeof row] || false)}
                      onChange={(event) => {
                        const checked = event.target.checked;
                        onRowSelectChange && onRowSelectChange({}, rows.map(row => ({
                          ...row,
                          [selectableField as string]: checked
                        })));
                      }}
                    />
                    {selectableLabel && (
                      <Typography variant="body1">
                        {selectableLabel}
                      </Typography>
                    )}
                  </Stack>
                </TableCell>
              )}
              {columns.map((column, index) => (
                <TableCell
                  key={index}
                  style={{...column.sxTableHeaderCell}}
                >
                  {
                    ((column.hasOwnProperty("sortable") && column.sortable) || !column.hasOwnProperty("sortable")) ? (
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
                          sortDirection === -1 ? <ExpandMoreIcon/> : <ExpandLessIcon/>
                        ) : null}
                      </TableSortLabel>
                    ) : (
                      column.headerName
                    )
                  }
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedRows.map((row, rowIndex) => (
              <TableRow key={rowIndex}>
                {selectable && (
                  <TableCell>
                    <Checkbox
                      checked={(row as any)[selectableField as string] || false}
                      onChange={(event) => {
                        const checked = event.target.checked;
                        rows = rows.map(r => {
                          if ((r as any).id === (row as any).id) {
                            (r as any)[selectableField as string] = checked;
                          }
                          return r;
                        });
                        onRowSelectChange && onRowSelectChange((row as any).id, rows);
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
                      style={{...column.sxTableBodyCell}}
                      key={columnIndex}
                      rowSpan={column.spannable && spanDictionaries[column.field][rowIndex] > 0 ? spanDictionaries[column.field][rowIndex] : undefined}>
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
