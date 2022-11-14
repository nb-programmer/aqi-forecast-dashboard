import { Admin, Layout, Title } from 'react-admin';
import { Resource } from 'react-admin';
import simpleRestProvider from 'ra-data-simple-rest';

//Custom App bar
import DashboardAppBar from './DashboardAppBar';

//Components
import * as AQI from './action/AQI';
import * as Forecast from './action/Forecast';
import * as Sensor from './action/Sensor';
import * as Validate from './action/Validate';

//Icons
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SensorsIcon from '@mui/icons-material/Sensors';
import ScienceIcon from '@mui/icons-material/Science';

//The data provider (backend server)
const dataProvider = simpleRestProvider('http://localhost:5000');

//Apply custom layout (theme button, etc.)
const DashboardLayout = (props) => (
	<Layout {...props} appBar={DashboardAppBar} />
);

const App = () => (
	<Admin layout={DashboardLayout} dataProvider={dataProvider}>
		<Resource name="aqi" options={{ label: 'AQI dataset' }} {...AQI} />
		<Resource name="forecast" {...Forecast} icon={TrendingUpIcon} />
		{/*<Resource name="sensor" {...Sensor} icon={SensorsIcon} />
		<Resource name="validate" options={{ label: 'Validation' }} {...Validate} icon={ScienceIcon} />
		*/}
	</Admin>
);

export default App;
