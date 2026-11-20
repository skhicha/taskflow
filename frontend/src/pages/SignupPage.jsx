import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { api, errorMessage } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { Alert } from '../components/ui'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function SignupPage() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  function validate() {
    const errors = {}
    if (!fullName.trim()) errors.fullName = 'Enter your name.'
    if (!EMAIL_RE.test(email)) errors.email = 'Enter a valid email address.'
    if (password.length < 8) errors.password = 'Password must be at least 8 characters.'
    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!validate()) return
    setSubmitting(true)
    try {
      await api.post('/api/auth/signup', { email, full_name: fullName, password })
      const res = await api.post('/api/auth/login', { email, password })
      login(res.data.access_token)
      navigate('/', { replace: true })
    } catch (err) {
      setError(errorMessage(err, 'Could not create your account.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-screen">
      <div className="auth-card">
        <div className="auth-brand">
          <span className="brand-mark" aria-hidden="true" />
          <span className="brand-name">TaskFlow</span>
        </div>
        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <Alert>{error}</Alert>
          <div className="field">
            <label className="field-label" htmlFor="fullName">
              Full name
            </label>
            <input
              id="fullName"
              className={`input${fieldErrors.fullName ? ' has-error' : ''}`}
              value={fullName}
              autoComplete="name"
              onChange={(e) => setFullName(e.target.value)}
            />
            {fieldErrors.fullName && <span className="field-error">{fieldErrors.fullName}</span>}
          </div>
          <div className="field">
            <label className="field-label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              className={`input${fieldErrors.email ? ' has-error' : ''}`}
              value={email}
              autoComplete="email"
              onChange={(e) => setEmail(e.target.value)}
            />
            {fieldErrors.email && <span className="field-error">{fieldErrors.email}</span>}
          </div>
          <div className="field">
            <label className="field-label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              className={`input${fieldErrors.password ? ' has-error' : ''}`}
              value={password}
              autoComplete="new-password"
              onChange={(e) => setPassword(e.target.value)}
            />
            {fieldErrors.password ? (
              <span className="field-error">{fieldErrors.password}</span>
            ) : (
              <span className="field-hint">At least 8 characters.</span>
            )}
          </div>
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>
        <div className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  )
}
