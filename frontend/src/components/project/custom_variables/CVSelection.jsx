import { Stack, Typography } from "@mui/material";
import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import DropDown from "../../input/DropDown";

const CVSelection = ({ selection, dataCategory, onChange }) => {

    const { t } = useTranslation();

    const [selectedAttribute, setSelectedAttribute] = useState(null);

    useEffect(() => {
        setSelectedAttribute(selection?.attr);
    }, [selection]);

    const getSelectionCriteriaOptions = useCallback(() => {
        const filter_attribute = dataCategory.cv_attributes.find(prop => prop.attribute === selectedAttribute);
        switch (filter_attribute?.data_type) {
            case 'Date':
                return [
                    { value: 'max', label: t('ui.custom_variables.selection_criterion.selection_criterion.date.min.label') },
                    { value: 'min', label: t('ui.custom_variables.selection_criterion.selection_criterion.date.max.label') },
                    { value: 'random', label: t('ui.custom_variables.selection_criterion.selection_criterion.date.random.label') }
                ];
            default:
                return [
                    { value: 'max', label: t('ui.custom_variables.selection_criterion.selection_criterion.min.label') },
                    { value: 'min', label: t('ui.custom_variables.selection_criterion.selection_criterion.max.label') },
                    { value: 'random', label: t('ui.custom_variables.selection_criterion.selection_criterion.random.label') }
                ];
        }
    }, [selectedAttribute, dataCategory, t]);

    return (
        <Stack direction={"row"} spacing={2} alignItems={"center"}>
            <Typography variant="body1">
                {t('ui.project.custom_variable.selection.part1', {data_category: dataCategory?.label})}
            </Typography>
            <DropDown
                label={t('ui.custom_variables.selection_criterion.selection_criterion.dropdown.label')}
                items={getSelectionCriteriaOptions()}
                value={selection?.operator}
                onChange={(e) => {
                    onChange({
                        ...selection,
                        operator: e.target.value
                    });
                }}
            />

            {
                selection?.operator && selection?.operator !== 'random' && (
                    <>
                    <Typography variant="body1">
                        {t('ui.project.custom_variable.selection.part2')}
                    </Typography>
                    <DropDown
                        label="Attribute"
                        items={dataCategory.cv_attributes.map(prop => ({
                            value: prop.attribute,
                            label: prop.label
                        }))}
                        value={selection?.attr}
                        onChange={(e) => {
                            setSelectedAttribute(e.target.value);
                            onChange({
                                ...selection,
                                attr: e.target.value
                            });
                        }}
                    />
                    </>
                )
            }
        </Stack>
    );
}

export default CVSelection;
