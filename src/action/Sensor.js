
import * as React from "react";
import { List, Datagrid, TextField, NumberField, DateField } from 'react-admin';

const SensorList = () => (
	<List>
        <Datagrid rowClick="show">
            <TextField source="id" />
            <TextField source="method" />
            <DateField source="forecast_start" />
            <NumberField source="days" />
        </Datagrid>
    </List>
);

export {
	SensorList as list
};
