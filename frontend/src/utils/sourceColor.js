const hashSource = (value) => {
  let hash = 0
  for (const char of value || '') {
    hash = ((hash << 5) - hash + char.codePointAt(0)) | 0
  }
  return Math.abs(hash)
}

export const getSourceStyle = (sourceKey) => {
  const hue = hashSource(sourceKey) % 360
  return {
    bg: `hsl(${hue} 75% 55% / 0.18)`,
    color: `hsl(${hue} 78% 68%)`,
    border: `hsl(${hue} 75% 55% / 0.35)`,
  }
}
