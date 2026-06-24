export function getTokenExpiry(token: string): number | null {
  try {
    const payload = token.split('.')[1]
    const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    return typeof decoded.exp === 'number' ? decoded.exp : null
  } catch {
    return null
  }
}

export function isTokenExpiringSoon(token: string, thresholdSeconds = 60): boolean {
  const exp = getTokenExpiry(token)
  if (!exp) return false
  return exp - Date.now() / 1000 < thresholdSeconds
}
