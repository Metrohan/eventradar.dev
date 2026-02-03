import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

const ThemeToggle = () => {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            onClick={toggleTheme}
            className="btn btn-link text-decoration-none p-2"
            title={theme === 'dark' ? "Açık Mod'a Geç" : "Koyu Mod'a Geç"}
            style={{ color: 'var(--text-primary)' }}
        >
            {theme === 'dark' ? (
                <i className="fas fa-sun fa-lg text-warning"></i>
            ) : (
                <i className="fas fa-moon fa-lg text-primary"></i>
            )}
        </button>
    );
};

export default ThemeToggle;
