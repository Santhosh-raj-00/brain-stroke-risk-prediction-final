import { createGlobalStyle } from 'styled-components';

const GlobalStyles = createGlobalStyle`
  :root {
    /* Primary Colors */
    --primary: #6C63FF;
    --primary-dark: #5A52D5;
    --primary-light: #8F88FF;
    --secondary: #4D96FF;
    
    /* Neumorphic Base */
    --bg-color: #E6E9EF;
    --surface-color: #E6E9EF;
    
    /* Shadows */
    --shadow-light: #FFFFFF;
    --shadow-dark: #C4C9D4;
    
    /* Text */
    --text-main: #2D3436;
    --text-secondary: #636E72;
    --text-light: #B2BEC3;
    
    /* Status */
    --success: #00B894;
    --warning: #FDCB6E;
    --error: #FF7675;
  }

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Inter', sans-serif;
  }

  body {
    background-color: var(--bg-color);
    color: var(--text-main);
    line-height: 1.5;
    letter-spacing: 0.2px;
  }

  /* Neumorphism Soft Card */
  .soft-card {
  .soft-card {
    background: var(--surface-color);
    border-radius: 20px;
    box-shadow:
      10px 10px 20px var(--shadow-dark),
      -10px -10px 20px var(--shadow-light);
    padding: 24px;
    transition: all 0.3s ease;
  }

  .soft-card:hover {
    box-shadow:
      6px 6px 12px var(--shadow-dark),
      -6px -6px 12px var(--shadow-light);
  }

  /* Neumorphism Button */
  .soft-button {
  .soft-button {
    background: var(--surface-color);
    border: none;
    border-radius: 16px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-main);
    cursor: pointer;
    box-shadow:
      6px 6px 12px var(--shadow-dark),
      -6px -6px 12px var(--shadow-light);
    transition: all 0.3s ease;
  }

  .soft-button:hover {
    box-shadow:
      4px 4px 8px var(--shadow-dark),
      -4px -4px 8px var(--shadow-light);
  }

  .soft-button:active {
    box-shadow:
      inset 4px 4px 8px var(--shadow-dark),
      inset -4px -4px 8px var(--shadow-light);
  }

  /* Primary Button */
  .soft-button.primary {
  .soft-button.primary {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    color: white;
    box-shadow:
      6px 6px 12px rgba(108, 99, 255, 0.4),
      -6px -6px 12px rgba(255, 255, 255, 0.9);
  }

  .soft-button.primary:hover {
  .soft-button.primary:hover {
    background: linear-gradient(135deg, var(--primary-light), var(--primary));
    box-shadow:
      4px 4px 8px rgba(108, 99, 255, 0.4),
      -4px -4px 8px rgba(255, 255, 255, 0.9);
  }

  /* Input Fields */
  .soft-input {
  .soft-input {
    background: var(--surface-color);
    border: none;
    border-radius: 16px;
    padding: 14px 16px;
    font-size: 14px;
    color: var(--text-main);
    box-shadow:
      inset 4px 4px 8px var(--shadow-dark),
      inset -4px -4px 8px var(--shadow-light);
    outline: none;
    width: 100%;
  }

  .soft-input:focus {
    box-shadow:
      inset 6px 6px 12px var(--shadow-dark),
      inset -6px -6px 12px var(--shadow-light);
  }

  /* Select Dropdown */
  .soft-select {
  .soft-select {
    background: var(--surface-color);
    border: none;
    border-radius: 16px;
    padding: 14px 16px;
    font-size: 14px;
    color: var(--text-main);
    box-shadow:
      inset 4px 4px 8px var(--shadow-dark),
      inset -4px -4px 8px var(--shadow-light);
    outline: none;
    width: 100%;
    appearance: none;
    background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231F2937' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right 1rem center;
    background-size: 1em;
  }

  /* Typography */
  h1, .heading-1 {
    font-size: 28px;
    font-weight: 700;
    color: #1F2937;
  }

  h2, .heading-2 {
    font-size: 20px;
    font-weight: 600;
    color: #1F2937;
  }

  h3, .heading-3 {
    font-size: 16px;
    font-weight: 600;
    color: #1F2937;
  }

  p, .body-text {
    font-size: 14px;
    font-weight: 400;
    color: #1F2937;
  }

  .label-text {
    font-size: 12px;
    font-weight: 500;
    color: #6B7280;
  }

  /* Risk Indicators */
  .risk-low {
    color: #22C55E;
    background-color: rgba(34, 197, 94, 0.1);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 500;
  }

  .risk-medium {
    color: #F59E0B;
    background-color: rgba(245, 158, 11, 0.1);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 500;
  }

  .risk-high {
    color: #EF4444;
    background-color: rgba(239, 68, 68, 0.1);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 500;
  }

  /* Container */
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }

  /* Flex utilities */
  .flex-center {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .flex-between {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .flex-column {
    display: flex;
    flex-direction: column;
  }

  /* Grid utilities */
  .grid-2 {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }

  .grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }

  /* Margin and Padding Utilities */
  .m-1 { margin: 8px; }
  .m-2 { margin: 16px; }
  .m-3 { margin: 24px; }
  .m-4 { margin: 32px; }
  
  .mt-1 { margin-top: 8px; }
  .mt-2 { margin-top: 16px; }
  .mt-3 { margin-top: 24px; }
  .mt-4 { margin-top: 32px; }
  
  .mb-1 { margin-bottom: 8px; }
  .mb-2 { margin-bottom: 16px; }
  .mb-3 { margin-bottom: 24px; }
  .mb-4 { margin-bottom: 32px; }
  
  .p-1 { padding: 8px; }
  .p-2 { padding: 16px; }
  .p-3 { padding: 24px; }
  .p-4 { padding: 32px; }
`;

export default GlobalStyles;