
import * as React from "react";
import { useState, useEffect } from "react";
import querystring from 'query-string';

import {
    List,
    Datagrid,
    TextField,
    NumberField,
    DateField,
    useShowController,
    useGetOne,
    useGetList
} from 'react-admin';

import {
    Create,
    Edit,
    Show,
    SimpleForm,
    TextInput,
    NumberInput,
    SelectInput,
    DateInput,
    required
} from 'react-admin';

import {
    Box,
    Typography,
    FormControl,
    Select,
    InputLabel,
    MenuItem,
    Checkbox,
    Skeleton,
    FormControlLabel
} from '@mui/material';

import Plot from 'react-plotly.js';

//List of all predictions done
const ForecastList = () => (
	<List title="List of forecasts" sort={{ field: 'id', order: 'DESC' }}>
        <Datagrid rowClick="show">
            <TextField source="id" />
            <TextField source="method" />
            <TextField source="ds" label="Used dataset" />
            <DateField source="forecast_start" />
            <NumberField source="avg" label="Forecast Average" />
            <TextField source="LOC" label="Level of Concern" />
            <NumberField source="days" />
        </Datagrid>
    </List>
);

//Generate preview of AQI data
const PreviewChart = ({dsid, ipol, dsstart}) => {
    if (!ipol) ipol = 'none';

    const fetchQuery = {
        i: ipol
    };

    //Fetch data
    const { data, isLoading, error, refetch } = useGetOne(
        'aqi',
        { id: `${dsid}?${querystring.stringify(fetchQuery)}` }
    );
    
    if (isLoading) {
        return <div>Loading preview...<Skeleton variant="rectangular" animation="wave" /></div>;
    }
    if (error) {
        return <div>Error!</div>;
    }

    const dX = data.data.map(d => d.sampling_ts);
    const dY = data.data.map(d => d.metric_aqi);

    const dataset = [
        {
            x: dX,
            y: dY,
            name: 'AQI',
            type: 'scatter',
            mode: 'lines' + (ipol === 'none' ? '+markers' : '')
        },
    ];

    return (
        <Plot
            style={{width: "100%"}}
            data={dataset}
            layout={{
                title: `Preview data ${dsid}`,
                uirevision: "true",
                shapes: [
                    {
                        type: 'line',
                        x0: dsstart,
                        y0: Math.min(...dY),
                        x1: dsstart,
                        y1: Math.max(...dY),
                        line: {
                            color: 'rgb(191, 55, 128)',
                            width: 2,
                            dash: 'dot'
                        }
                    }
                ],
                annotations: [
                    {
                        showarrow: false,
                        text: "Forecast from here",
                        align: "right",
                        x: dsstart,
                        xanchor: "right",
                        y: (1.5*dY.reduce((a, b) => a + b, 0) / dY.length),
                        yanchor: "bottom",
                        bgcolor: '#fff'
                    }
                ]
            }}
            useResizeHandler={true}
            />
    );
};

const DatasetSelectBox = ({source, ...others}) => {
    let { data, total, isLoading, error, refetch } = useGetList('aqi');

    return (
        isLoading ? (
            <Skeleton variant="rectangular" />
         ) : (
            <SelectInput source={source} validate={required()} choices={data} {...others} />
         )
    );
};

//List of all predictions done
const ForecastCreate = () => {
    const methodChoices = [
        { id: 'lstm', name: 'LSTM'},
        { id: 'arima', name: 'ARIMA'},
        { id: 'svr', name: 'SVR'},
        { id: 'polydeg10', name: 'Polynomial (degree 10)'},
    ];

    const interpolationChoices = [
        { id: 'none', name: "None" },
        { id: 'nearest', name: "Nearest" },
        { id: 'linear', name: "Linear (default)" },
        //{ id: 'spline', name: "Spline (order 3)" },
        { id: 'quadratic', name: "Quadratic" },
        //{ id: 'cubic', name: "Cubic" }
    ];

    const defaultInterpol = 'linear';
    const defaultStartDate = '2021-12-01';

    const [previewDSId, setPreviewDSId] = useState(null);
    const [previewStartLine, setPreviewStartLine] = useState(defaultStartDate);
    const [previewIpol, setPreviewIpol] = useState(defaultInterpol);
    
	return (
        <Create title="Create forecast">
            <SimpleForm>
                <Typography variant="h6" gutterBottom>
                    Forecast
                </Typography>
                <Box display={{ xs: 'block', sm: 'flex', width: '100%' }}>
                    <Box flex={1} mr={{ xs: 0, sm: '0.5em' }}>
                        <DatasetSelectBox fullWidth source="dataset" onChange={e=>setPreviewDSId(e.target.value)} />
                    </Box>
                    <Box flex={1} mr={{ xs: 0, sm: '0.5em' }}>
                        <DateInput fullWidth validate={required()} source="forecast_at" defaultValue={defaultStartDate} onChange={e=>setPreviewStartLine(e.target.value)} />
                    </Box>
                </Box>
                <Box display={{ xs: 'block', sm: 'flex', width: '100%' }}>
                    <Box flex={1} mr={{ xs: 0, sm: '0.5em' }}>
                        <SelectInput fullWidth source="method" validate={required()} choices={methodChoices} />
                    </Box>
                    <Box flex={1} mr={{ xs: 0, sm: '0.5em' }}>
                        <NumberInput fullWidth source="days" defaultValue={15} label="Forecast days" />
                    </Box>
                    <Box flex={1} mr={{ xs: 0, sm: '0.5em' }}>
                        <SelectInput fullWidth source="interpolation" validate={required()} choices={interpolationChoices} defaultValue={defaultInterpol} onChange={e=>setPreviewIpol(e.target.value)} />
                    </Box>
                </Box>
            </SimpleForm>

            {previewDSId && <PreviewChart dsid={previewDSId} ipol={previewIpol} dsstart={previewStartLine} />}
        </Create>
    );
};

const aqi_loc_color_map = {
    'Good': 'lime',
    'Moderate': 'yellow',
    'Unhealthy for Sensitive Groups': 'orange',
    'Unhealthy': 'red',
    'Very Unhealthy': 'purple',
    'Hazardous': 'maroon'
};

function fetchFuture(record) {
    
}

const ForecastChartLayout = (props) => {
    const {
        defaultTitle,
        error,
        isFetching,
        isLoading,
        record,
        refetch,
        resource
    } = useShowController();
    
    let futureData = {id: null, data: []};
    const fID = (record ? record.id : null);
    
    const subQ = useGetOne(
        'forecast/compare',
        { id: fID }
    );
    
    console.log(subQ.data);

    if (!subQ.isLoading && !subQ.error && subQ.data)
        futureData = subQ.data;

    console.log(futureData)

    const lineType = props.plotSmooth ? "spline" : "linear";
    
    if (isLoading || isFetching) {
        return <div>Loading...</div>;
    }
    if (error) {
        return <div>Error!</div>;
    }
    
    const dX_forecast = record.data_forecast.map(d => d.sampling_ts);
    const dY_forecast = record.data_forecast.map(d => d.metric_aqi);
    
    const dX_orig = record.data_original.map(d => d.sampling_ts);
    const dY_orig = record.data_original.map(d => d.metric_aqi);

    const dX_input = record.data_used.map(d => d.sampling_ts);
    const dY_input = record.data_used.map(d => d.metric_aqi);

    const dX_fut = futureData.data.map(d => d.sampling_ts);
    const dY_fut = futureData.data.map(d => d.metric_aqi);

    const forecast_method = record.method;
    const data_interpol_method = record.interpolation;

    const plotTitle = `${defaultTitle} (${forecast_method})`;
    const Remark = ({loc, aqi}) => (
        <Typography>
            <Typography display="inline">Level of concern:</Typography>
            <Typography display="inline" mx={1} sx={{ fontWeight: 'bold' }} color={aqi_loc_color_map[loc]}>{loc}</Typography>(AQI {aqi})
        </Typography>
    );

    const dataset = [
        {
            x: dX_forecast,
            y: dY_forecast,
            name: 'Forecasted AQI',
            type: 'scatter',
            mode: 'lines',
            line: {shape: lineType}
        },
        {
            x: dX_orig,
            y: dY_orig,
            name: 'Previous AQI(Original)',
            type: 'scatter',
            mode: 'lines+markers',
            line: {shape: lineType}
        },
        {
            x: dX_input,
            y: dY_input,
            name: `Previous AQI(Filled ${data_interpol_method})`,
            type: 'scatter',
            mode: 'lines',
            line: {shape: lineType},
            visible: 'legendonly'
        },
        {
            x: dX_fut,
            y: dY_fut,
            name: `Future AQI(Dataset)`,
            type: 'scatter',
            mode: 'lines',
            line: {shape: lineType},
            visible: 'legendonly'
        }
    ];
    
    return (
        <>
            <Remark loc={record.forecast_meta.LOC} aqi={Math.round(record.forecast_meta.avg)} />
            <Plot
                style={{width: "100%"}}
                data={dataset}
                layout={{title: plotTitle, uirevision: "true"}}
                useResizeHandler={true}
                />
        </>
    );
};

const ForecastShow = () => {
    const [ plotSmooth, setPlotSmooth ] = useState(false);

	return (
        <Show>
            <FormControl sx={{ mr: 2 }}>
                <FormControlLabel
                    value="end"
                    control={
                        <Checkbox
                            checked={plotSmooth}
                            onChange={(e) => setPlotSmooth(e.target.checked)}
                        />
                    }
                    label="Smooth"
                    labelPlacement="end"
                />
            </FormControl>
            <ForecastChartLayout plotSmooth={plotSmooth} />
        </Show>
    );
};

export {
	ForecastList as list,
	ForecastCreate as create,
    ForecastShow as show
};
