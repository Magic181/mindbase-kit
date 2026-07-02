import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useUIStore } from './ui'

describe('useUIStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    document.documentElement.classList.remove('dark')
  })

  it('toggles sidebarCollapsed', () => {
    const store = useUIStore()
    expect(store.sidebarCollapsed).toBe(false)
    store.toggleSidebar()
    expect(store.sidebarCollapsed).toBe(true)
    store.toggleSidebar()
    expect(store.sidebarCollapsed).toBe(false)
  })

  it('toggles mobileSidebarOpen and closes it', () => {
    const store = useUIStore()
    expect(store.mobileSidebarOpen).toBe(false)
    store.toggleMobileSidebar()
    expect(store.mobileSidebarOpen).toBe(true)
    store.closeMobileSidebar()
    expect(store.mobileSidebarOpen).toBe(false)
  })

  it('toggles darkMode and syncs the documentElement class', () => {
    const store = useUIStore()
    expect(store.darkMode).toBe(false)
    expect(document.documentElement.classList.contains('dark')).toBe(false)

    store.toggleDarkMode()
    expect(store.darkMode).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)

    store.toggleDarkMode()
    expect(store.darkMode).toBe(false)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })
})
