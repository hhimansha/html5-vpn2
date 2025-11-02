import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import 'semantic-ui-css/semantic.min.css'; // Semantic UI base styles
import './styles/theme-injector'; // Dynamic theme injection - MUST come after semantic UI
import './styles/theme.css'; // Theme overrides - MUST come last
import 'flexlayout-react/style/dark.css';
import 'react-contexify/ReactContexify.css';
import App from './Components/App/App';
import { AppProvider } from "./Context/AppContext";
import { LayoutProvider } from "./Layout/LayoutContext";

ReactDOM.render(
    <LayoutProvider>
        <AppProvider>
            <App/>
        </AppProvider>
    </LayoutProvider>,
    document.getElementById('root')
);