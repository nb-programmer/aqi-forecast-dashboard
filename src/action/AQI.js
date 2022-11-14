
import * as React from "react";
import { useState, useEffect } from "react";
import { List, Show, Datagrid, TextField, NumberField, DateField, useShowController } from 'react-admin';
import { Typography, FormControl, Select, InputLabel, MenuItem, Checkbox, FormControlLabel, Skeleton } from '@mui/material';

import Plot from 'react-plotly.js';

const AQIList = () => (
	<List>
        <Datagrid rowClick="show">
            <TextField source="name" label="Location name" />
            <DateField source="from_date" />
            <DateField source="to_date" />
            <NumberField source="average_aqi" />
        </Datagrid>
    </List>
);

const AQIChartLayout = (props) => {
    const {
        defaultTitle,
        error,
        isFetching,
        isLoading,
        record,
        refetch,
        resource
    } = useShowController();
    
    const lineType = props.plotSmooth ? "spline" : "linear";
    
    if (isLoading || isFetching) {
        return <Skeleton animation="wave" variant="rectangular" />;
    }
    if (error) {
        return <div>Error!</div>;
    }

    const dX = record.data.map(d => d.sampling_ts);
    const dY = record.data.map(d => d.metric_aqi);
    
    //const dX_MA = record.data_ma.map(d => d.sampling_ts);
    //const dY_MA = record.data_ma.map(d => d.metric_aqi);

    const dataset = [
        {
            x: dX,
            y: dY,
            name: 'AQI',
            type: 'scatter',
            mode: 'lines',
            line: {shape: lineType}
        },
        /*{
            x: dX_MA,
            y: dY_MA,
            name: 'AQI (Moving Average)',
            type: 'scatter',
            mode: 'lines'
        }*/
    ];
    
    return (
        <Plot
            style={{width: "100%"}}
            data={dataset}
            layout={{ title: defaultTitle, uirevision: "true" }}
            useResizeHandler={true}
            />
    );
};

const AQIShow = () => {
    const [ selectYear, setSelectYear ] = useState("All");
    const [ plotSmooth, setPlotSmooth ] = useState(false);

	return (
        <Show>
            {/*<FormControl sx={{ mr: 2 }}>
                <InputLabel id="select-data-year-label">Year</InputLabel>
                <Select
                    labelId="select-data-year-label"
                    id="select-data-year"
                    defaultValue={selectYear}
                    label="Year"
                    onChange={e => setSelectYear(e.target.value)}
                    >
                    <MenuItem value="All">All</MenuItem>
                    <MenuItem value={"2017"}>2017</MenuItem>
                    <MenuItem value={"2018"}>2018</MenuItem>
                    <MenuItem value={"2019"}>2019</MenuItem>
                    <MenuItem value={"2020"}>2020</MenuItem>
                    <MenuItem value={"2021"}>2021</MenuItem>
                    <MenuItem value={"2022"}>2022</MenuItem>
                </Select>
            </FormControl>
            */}
            <FormControl sx={{ mr: 2 }}>
                <FormControlLabel
                    value="end"
                    control={
                        <Checkbox
                            checked={plotSmooth}
                            onChange={e => setPlotSmooth(e.target.checked)}
                        />
                    }
                    label="Smooth"
                    labelPlacement="end"
                />
            </FormControl>

            <AQIChartLayout plotSmooth={plotSmooth} />
        </Show>
    );
};

export {
	AQIList as list,
    AQIShow as show
};
