import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { request } from '../api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('helpdesk_token') || '')
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(token))

  useEffect(() => {
    if (!token) {
      setUser(null)
      setLoading(false)
      localStorage.removeItem('helpdesk_token')
      return
    }

    localStorage.setItem('helpdesk_token', token)
    request('/auth/me', {}, token)
      .then(setUser)
      .catch(() => {
        setToken('')
        setUser(null)
        localStorage.removeItem('helpdesk_token')
      })
      .finally(() => setLoading(false))
  }, [token])

  async function login(email, password) {
    const response = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    setToken(response.access_token)
  }

  function logout() {
    setToken('')
    setUser(null)
    localStorage.removeItem('helpdesk_token')
  }

  const value = useMemo(
    () => ({ token, user, login, logout, setUser, loading, isAuthenticated: Boolean(token && user) }),
    [token, user, loading]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
