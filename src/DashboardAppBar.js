
import { ToggleThemeButton, AppBar, defaultTheme } from 'react-admin';
import { Typography } from '@mui/material';

const lightTheme = {
    ...defaultTheme
};

const darkTheme = {
    palette: { mode: 'dark' }
};

export default (props) => (
    <AppBar {...props}>
        <Typography flex="1" variant="h6" id="react-admin-title"></Typography>
        <ToggleThemeButton
            lightTheme={lightTheme}
            darkTheme={darkTheme}
        />
    </AppBar>
);
