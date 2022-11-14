
import * as React from "react";
import { List, Datagrid, TextField, NumberField, DateField } from 'react-admin';

const ValidateList = () => (
	<List title="Validate Models">
        <Datagrid rowClick="show">
            <TextField source="id" />
            <TextField source="method" />
            <DateField source="forecast_start" />
            <NumberField source="days" />
        </Datagrid>
    </List>
);

export {
	ValidateList as list
};
