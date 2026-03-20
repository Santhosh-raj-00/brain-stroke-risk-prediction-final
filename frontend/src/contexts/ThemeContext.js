import React, { createContext, useContext, useState } from 'react';

const ThemeContext = createContext();

const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState({
    colors: {
      // Backgrounds
      mainBackground: '#E6E9EF',
      cardSurface: '#E6E9EF', // Same as bg for true neumorphism
      sidebar: '#E6E9EF',
      adminBackground: '#E0E5EC',

      // Primary Accents
      primary: '#6C63FF',
      primaryDark: '#5A52D5',
      primaryLight: '#8F88FF',
      secondary: '#4D96FF',
      highlight: '#00CEC9',

      // Risk Colors
      riskLow: '#00B894',
      riskMedium: '#FDCB6E',
      riskHigh: '#FF7675',

      // Text
      primaryText: '#2D3436',
      secondaryText: '#636E72',
      mutedLabels: '#B2BEC3',
    },
    typography: {
      fontFamily: "'Inter', sans-serif",
      sizes: {
        appTitle: '28px',
        sectionHeading: '20px',
        cardTitle: '16px',
        bodyText: '14px',
        labels: '12px',
      },
      weights: {
        appTitle: '700',
        sectionHeading: '600',
        cardTitle: '600',
        bodyText: '400',
        labels: '500',
      },
      lineHeight: '1.5',
      letterSpacing: '0.2px',
    },
    shadows: {
      softCard: '10px 10px 20px #C4C9D4, -10px -10px 20px #FFFFFF',
      softButton: '6px 6px 12px #C4C9D4, -6px -6px 12px #FFFFFF',
      softInput: 'inset 4px 4px 8px #C4C9D4, inset -4px -4px 8px #FFFFFF',
    },
    borderRadius: {
      card: '20px',
      button: '16px',
      input: '16px',
    },
  });

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export { ThemeProvider, useTheme };