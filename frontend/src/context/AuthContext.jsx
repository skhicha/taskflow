import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { api, TOKEN_KEY } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(null)
  const [initializing, setInitializing] = useState(true)

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
  }, [])

  useEffect(() => {
    window.addEventListener('tf:unauthorized', logout)
    return () => window.removeEventListener('tf:unauthorized', logout)
  }, [logout])

  useEffect(() => {
    let active = true
    if (!token) {
      setUser(null)
      setInitializing(false)
      return
    }
    setInitializing(true)
    api
      .get('/api/auth/me')
      .then((res) => {
        if (active) setUser(res.data)
      })
      .catch(() => {
        if (active) logout()
      })
      .finally(() => {
        if (active) setInitializing(false)
      })
    return () => {
      active = false
    }
  }, [token, logout])

  const login = useCallback((accessToken) => {
    localStorage.setItem(TOKEN_KEY, accessToken)
    setToken(accessToken)
  }, [])

  const value = useMemo(
    () => ({ token, user, initializing, isAuthenticated: Boolean(token), login, logout }),
    [token, user, initializing, login, logout]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}
