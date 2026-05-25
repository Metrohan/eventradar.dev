import React from 'react'

export const TAG_STYLES = {
  hackathon: { label: 'Hackathon',        emoji: '🏆', bg: 'rgba(56,189,248,0.15)',  bgSelected: 'rgba(56,189,248,0.3)',  color: '#38bdf8', border: 'rgba(56,189,248,0.5)'  },
  seminer:   { label: 'Seminer / Webinar', emoji: '🎓', bg: 'rgba(168,85,247,0.15)', bgSelected: 'rgba(168,85,247,0.3)', color: '#a855f7', border: 'rgba(168,85,247,0.5)'  },
  atolye:    { label: 'Atölye',            emoji: '🛠', bg: 'rgba(34,197,94,0.15)',  bgSelected: 'rgba(34,197,94,0.3)',  color: '#22c55e', border: 'rgba(34,197,94,0.5)'   },
  konferans: { label: 'Konferans',         emoji: '🎤', bg: 'rgba(251,146,60,0.15)', bgSelected: 'rgba(251,146,60,0.3)', color: '#fb923c', border: 'rgba(251,146,60,0.5)'  },
  bootcamp:  { label: 'Bootcamp',          emoji: '💻', bg: 'rgba(244,63,94,0.15)',  bgSelected: 'rgba(244,63,94,0.3)',  color: '#f43f5e', border: 'rgba(244,63,94,0.5)'   },
  diger:     { label: 'Diğer',             emoji: '📌', bg: 'rgba(148,163,184,0.15)',bgSelected: 'rgba(148,163,184,0.3)',color: '#94a3b8', border: 'rgba(148,163,184,0.4)' },
}

const TagBadge = ({ name, selected = false, clickable = false, onClick }) => {
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
      <span>{s.label}</span>
    </span>
  )
}

export default TagBadge
