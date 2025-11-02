import { APP_THEME, THEMES } from '../config/theme';

// Inject CSS variables based on selected theme
export const injectTheme = () => {
    const theme = THEMES[APP_THEME];
    
    const style = document.createElement('style');
    style.textContent = `
        :root {
            --primary-color: ${theme.primary};
            --secondary-color: ${theme.secondary};
            --success-color: ${theme.success};
            --warning-color: ${theme.warning};
            --danger-color: ${theme.danger};
            --info-color: ${theme.info};
            --background-color: ${theme.background};
            --text-color: ${theme.text};
        }
    `;
    
    document.head.appendChild(style);
};

// Apply theme on import
injectTheme();