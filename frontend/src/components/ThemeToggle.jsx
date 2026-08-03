import React from 'react';
import { useTranslation } from 'react-i18next';
import { useTheme } from '../contexts/ThemeContext';

const ThemeToggle = () => {
    const { theme, toggleTheme } = useTheme();
    const { t } = useTranslation();
    const label = theme === 'dark' ? t('themeToggle.toLightMode') : t('themeToggle.toDarkMode');

    return (
        <button
            onClick={toggleTheme}
            className="btn btn-link text-decoration-none p-2"
            title={label}
            aria-label={label}
            style={{ color: 'var(--text-primary)' }}
            // The prerender PoC snapshots the browser-serialized DOM (see
            // docs/adr/0006-prerender-poc.md), which normalizes this inline
            // style string ("color:var(--text-primary)") slightly
            // differently than React's own serialization on hydrate
            // ("color: var(--text-primary);"). Same value, cosmetic-only
            // diff — suppress rather than let it force a client remount.
            suppressHydrationWarning
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
