import React from 'react'
import { useTranslation } from 'react-i18next'

// name (object key) is the value stored/matched against event.tags data and
// must stay fixed; labelKey is the i18n key for the badge's displayed text.
export const TAG_STYLES = {
  hackathon: { labelKey: 'tags.hackathon', emoji: '🏆', bg: 'rgba(56,189,248,0.15)',  bgSelected: 'rgba(56,189,248,0.3)',  color: '#38bdf8', border: 'rgba(56,189,248,0.5)'  },
  seminer:   { labelKey: 'tags.seminer',   emoji: '🎓', bg: 'rgba(168,85,247,0.15)', bgSelected: 'rgba(168,85,247,0.3)', color: '#a855f7', border: 'rgba(168,85,247,0.5)'  },
  atolye:    { labelKey: 'tags.atolye',    emoji: '🛠', bg: 'rgba(34,197,94,0.15)',  bgSelected: 'rgba(34,197,94,0.3)',  color: '#22c55e', border: 'rgba(34,197,94,0.5)'   },
  konferans: { labelKey: 'tags.konferans', emoji: '🎤', bg: 'rgba(251,146,60,0.15)', bgSelected: 'rgba(251,146,60,0.3)', color: '#fb923c', border: 'rgba(251,146,60,0.5)'  },
  bootcamp:  { labelKey: 'tags.bootcamp',  emoji: '💻', bg: 'rgba(244,63,94,0.15)',  bgSelected: 'rgba(244,63,94,0.3)',  color: '#f43f5e', border: 'rgba(244,63,94,0.5)'   },
  diger:     { labelKey: 'tags.diger',     emoji: '📌', bg: 'rgba(148,163,184,0.15)',bgSelected: 'rgba(148,163,184,0.3)',color: '#94a3b8', border: 'rgba(148,163,184,0.4)' },
}

const TagBadge = ({ name, selected = false, clickable = false, onClick }) => {
  const { t } = useTranslation()
  const s = TAG_STYLES[name] || TAG_STYLES.diger

  return (
    <span
      onClick={clickable ? onClick : undefined}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '3px',
        padding: '3px 8px',
        borderRadius: '6px',
        background: selected ? s.bgSelected : s.bg,
        border: `1px solid ${selected ? s.color : s.border}`,
        color: s.color,
        fontSize: '0.7rem',
        fontWeight: 700,
        cursor: clickable ? 'pointer' : 'default',
        userSelect: 'none',
        transition: 'all 0.15s ease',
        whiteSpace: 'nowrap',
      }}
    >
      <span>{s.emoji}</span>
      <span>{t(s.labelKey)}</span>
    </span>
  )
}

export default TagBadge
