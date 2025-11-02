// Theme configuration - change this value to apply different themes
export const APP_THEME = 'dark'; // CHANGED: Set to 'dark'

// Theme color definitions
export const THEMES = {
    default: {
        primary: '#2185d0',
        secondary: '#1b1c1d',
        success: '#21ba45',
        warning: '#f2711c',
        danger: '#db2828',
        info: '#00b5ad',
        background: '#ffffff',
        text: '#333333'
    },
    twitter: {
        primary: '#1da1f2',
        secondary: '#14171a',
        success: '#17bf63',
        warning: '#ffad1f',
        danger: '#e0245e',
        info: '#794bc4',
        background: '#f5f8fa',
        text: '#14171a'
    },
    material: {
        primary: '#4285f4',
        secondary: '#34a853',
        success: '#34a853',
        warning: '#fbbc05',
        danger: '#ea4335',
        info: '#4285f4',
        background: '#fafafa',
        text: '#3c4043'
    },
    bootstrap: {
        primary: '#007bff',
        secondary: '#6c757d',
        success: '#28a745',
        warning: '#ffc107',
        danger: '#dc3545',
        info: '#17a2b8',
        background: '#f8f9fa',
        text: '#212529'
    },
    amazon: {
        primary: '#ff9900',
        secondary: '#146eb4',
        success: '#00a650',
        warning: '#ff8c00',
        danger: '#e47911',
        info: '#146eb4',
        background: '#ffffff',
        text: '#111111'
    },
    // NEW DARK MODE THEME 
    dark: {
        // Core Palette from the component
        primary: '#00bcd4',   // Cyan (Used for highlights/primary buttons)
        secondary: '#2d2d2d',  // Card/Element background
        
        // Semantic UI equivalents adapted for dark mode contrast
        success: '#4caf50',   // Green
        warning: '#ff9800',   // Orange
        danger: '#f44336',    // Red
        info: '#03a9f4',      // Light Blue/Info

        // Base background and text colors
        background: '#1e1e1e', // Dark Mode Base Background
        text: '#f0f0f0'        // Light Text
    }
};

// Get current theme colors
export const currentTheme = THEMES[APP_THEME];