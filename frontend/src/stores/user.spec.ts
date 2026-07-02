import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { authApi, type UserProfile } from '@/api/auth'
import { clearTokens, runWithoutAuthRedirect, saveTokens } from '@/api/index'
import { useUserStore } from './user'

vi.mock('@/api/auth', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    refresh: vi.fn(),
    logout: vi.fn(),
    me: vi.fn(),
  },
}))

vi.mock('@/api/index', () => ({
  saveTokens: vi.fn(),
  clearTokens: vi.fn(),
  runWithoutAuthRedirect: vi.fn((fn: () => unknown) => fn()),
}))

const profile: UserProfile = { id: 1, username: 'alice', email: 'alice@example.com' }

describe('useUserStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('login saves tokens, fetches the profile, and marks the user as logged in', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      data: { access: 'access-token', refresh: 'refresh-token' },
    } as never)
    vi.mocked(authApi.me).mockResolvedValue({ data: profile } as never)

    const store = useUserStore()
    await store.login('alice', 'secret')

    expect(saveTokens).toHaveBeenCalledWith('access-token', 'refresh-token')
    expect(store.isLoggedIn).toBe(true)
    expect(store.profile).toEqual(profile)
  })

  it('initAuth resolves false immediately when there is no stored token', async () => {
    const store = useUserStore()
    store.token = ''

    const result = await store.initAuth()
    expect(result).toBe(false)
    expect(store.authReady).toBe(true)
    expect(authApi.me).not.toHaveBeenCalled()
  })

  it('initAuth clears auth when fetching the profile fails', async () => {
    vi.mocked(authApi.me).mockRejectedValue(new Error('unauthorized'))

    const store = useUserStore()
    store.token = 'stale-token'

    const result = await store.initAuth()
    expect(result).toBe(false)
    expect(store.authReady).toBe(true)
    expect(runWithoutAuthRedirect).toHaveBeenCalled()
    expect(clearTokens).toHaveBeenCalled()
    expect(store.isLoggedIn).toBe(false)
  })

  it('logout clears auth even if the API call fails', async () => {
    localStorage.setItem('refresh_token', 'refresh-token')
    vi.mocked(authApi.logout).mockRejectedValue(new Error('already invalid'))

    const store = useUserStore()
    store.isLoggedIn = true
    store.profile = profile

    await store.logout()

    expect(authApi.logout).toHaveBeenCalledWith('refresh-token')
    expect(clearTokens).toHaveBeenCalled()
    expect(store.isLoggedIn).toBe(false)
    expect(store.profile).toBeNull()
  })
})
