import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import authApi from './authApi'
import type { User } from './authTypes'
import { AuthContext } from './auth'
import type { AuthContextValue } from './auth'

const TOKEN_KEY = 'smart-credit-access-token'

function readToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = useCallback(async (): Promise<void> => {
    if (!readToken()) {
      setUser(null)
      return
    }

    try {
      const currentUser = await authApi.fetchCurrentUser()
      setUser(currentUser)
    } catch {
      authApi.clearAuthToken()
      setUser(null)
    }
  }, [])

  useEffect(() => {
    let active = true

    async function initialize() {
      try {
        await refreshUser()
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void initialize()

    return () => {
      active = false
    }
  }, [refreshUser])

  const login = useCallback(async (email: string, password: string) => {
    await authApi.loginRequest(email, password)
    const currentUser = await authApi.fetchCurrentUser()
    setUser(currentUser)
  }, [])

const register = useCallback(
  async (_name: string, email: string, password: string) => {
    await authApi.registerRequest(email, password)
    await login(email, password)
  },
  [login],
)

  const logout = useCallback(() => {
    authApi.clearAuthToken()
    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, loading, login, register, logout, refreshUser],
  )

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
