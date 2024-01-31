import { Button, IconButton, Stack, Typography } from "@mui/material";
import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import DropDown from "../../../../input/DropDown";
import { Delete as DeleteIcon } from '@mui/icons-material';
import ValueInput from "../../../../input/ValueInput";

const CVFilters = ({ filters, dataCategory, operators, onChange }) => {

    const { t } = useTranslation();

    const addFilter = () => {
        onChange([...filters, {
            attr: '',
            operator: '',
            value: '',
        }]);
    };

    const removeFilter = (index) => {
        const newFilters = [...filters];
        newFilters.splice(index, 1);
        onChange(newFilters);
    };

    const updateFilter = (index, key, value) => {
        const newFilters = [...filters];
        newFilters[index][key] = value;
        onChange(newFilters);
        console.log("newFilters", newFilters)
    };

    return (
        <Stack spacing={2}>
        <Typography variant="body1">
            {t('ui.project.custom_variable.filters.title')}
        </Typography>
        {filters.map((filter, index) => (
            <Stack direction="row" spacing={2} alignItems="center" key={index}>
            <CVFilter
                filter={filter}
                index={index}
                operators={operators}
                dataCategory={dataCategory}
                onChange={updateFilter}
                onRemove={removeFilter}
            />
            </Stack>
        ))}

        <Button onClick={addFilter}>
            Add Filter
        </Button>
        </Stack>
    );
};


const CVFilter = ({ filter, index, operators, dataCategory, onChange, onRemove }) => {

    const { t } = useTranslation();

    const getDataTypeForAttribute = useCallback((attribute) => {
        return dataCategory.cv_attributes.find(prop => prop.attribute === attribute)?.data_type;
    }, [dataCategory]);

    const getUnitForAttribute = useCallback((attribute) => {
        return dataCategory.cv_attributes.find(prop => prop.attribute === attribute)?.unit;
    }, [dataCategory]);

    const getOperatorsForAttribute = useCallback((attribute) => {
        const ops = operators[getDataTypeForAttribute(attribute)] || [];
        return ops.map(op => ({
            ...op,
            label: t(op.label) // translate label
        }));
    }, [operators, getDataTypeForAttribute, t]);



    return (
        <Stack direction="row" spacing={1} alignItems="center">
            <DropDown
                label="Attribute"
                items={dataCategory.cv_attributes.map(prop => ({
                    value: prop.attribute,
                    label: prop.label
                }))}
                value={filter.attr}
                onChange={e => onChange(index, 'attr', e.target.value)}
                sx={{ minWidth: 200 }}
            />

            {filter.attr && (
                <DropDown
                    label="Operator"
                    items={getOperatorsForAttribute(filter.attr)}
                    value={filter.operator}
                    onChange={e => onChange(index, 'operator', e.target.value)}
                    sx={{ minWidth: 200 }}
                />
            )}

            {filter.operator && (
                <ValueInput
                    label="Value"
                    data_type={getDataTypeForAttribute(filter.attr)}
                    value={filter.value}
                    unit={getUnitForAttribute(filter.attr)}
                    onChange={(value) => onChange(index, "value", value)}
                />
            )}


            <IconButton onClick={() => onRemove(index)}>
                <DeleteIcon />
            </IconButton>

        </Stack>
    );
};

export default CVFilters;
