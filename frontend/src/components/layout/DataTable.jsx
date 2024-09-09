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

import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

const DataTable = ({rows, columns, selectable, selectableLabel, selectableField, onRowSelectChange}) => {
  const [sortField, setSortField] = useState(null);
  const [sortDirection, setSortDirection] = useState(1); // 1 for 'asc' and -1 for 'desc'

  const sortRows = useCallback((rows) => {
    let sortedRows = [...rows];
    if (sortField) {
      sortedRows.sort((a, b) => {
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
  const computeRowSpan = (field) => {
    let currentFieldValue = null;
    let currentSpan = 0;
    const spans = [];

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
  const spanDictionaries = {};

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
                      checked={sortedRows.every(row => row[selectableField] || false)}
                      onChange={(event) => {
                        const checked = event.target.checked;
                        onRowSelectChange && onRowSelectChange(null, rows.map(row => ({
                          ...row,
                          [selectableField]: checked
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
                  style={{
                    width: column.width ? column.width : undefined,
                    maxWidth: column.maxWidth ? column.maxWidth : undefined,
                    wordWrap: 'break-word',
                  }}
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
                      checked={row[selectableField] || false}
                      onChange={(event) => {
                        const checked = event.target.checked;
                        rows = rows.map(r => {
                          if (r.id === row.id) {
                            r[selectableField] = checked;
                          }
                          return r;
                        });
                        onRowSelectChange && onRowSelectChange(row.id, rows);
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
                      style={{
                        width: column.width ? column.width : undefined,
                        maxWidth: column.maxWidth ? column.maxWidth : undefined,
                        wordWrap: 'break-word',
                      }}
                      key={columnIndex}
                      rowSpan={column.spannable && spanDictionaries[column.field][rowIndex] > 0 ? spanDictionaries[column.field][rowIndex] : undefined}>
                      {column.renderCell ? column.renderCell(row) : row[column.field] || ''}
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
