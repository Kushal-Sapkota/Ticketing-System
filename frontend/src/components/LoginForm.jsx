import { useState } from 'react'

export function LoginForm({ onLogin, loading }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    try {
      await onLogin(email, password)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form className="card auth-card" onSubmit={handleSubmit}>
      <h1>IT Helpdesk</h1>
      <p>Agent login</p>
      <label>
        Email
        <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
      </label>
      <label>
        Password
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required minLength="8" />
      </label>
      {error ? <div className="error">{error}</div> : null}
      <button type="submit" disabled={loading}>
        {loading ? 'Signing in...' : 'Sign in'}
      </button>
    </form>
  )
}
