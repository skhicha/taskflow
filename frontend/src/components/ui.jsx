export function Spinner() {
  return <span className="spinner" role="status" aria-label="Loading" />
}

export function LoadingRow({ label = 'Loading…' }) {
  return (
    <div className="loading-row">
      <Spinner />
      <span>{label}</span>
    </div>
  )
}

export function Alert({ children, tone = 'danger' }) {
  if (!children) return null
  return <div className={`alert alert-${tone}`}>{children}</div>
}

export function EmptyState({ title, body, action }) {
  return (
    <div className="empty-state">
      <div className="empty-state-title">{title}</div>
      {body && <div className="empty-state-body">{body}</div>}
      {action}
    </div>
  )
}

const PRIORITY_TONE = { low: 'neutral', medium: 'warning', high: 'danger' }
const STATUS_TONE = { todo: 'neutral', in_progress: 'accent', done: 'success' }
const STATUS_LABEL = { todo: 'To do', in_progress: 'In progress', done: 'Done' }

export function PriorityBadge({ priority }) {
  return <span className={`badge badge-${PRIORITY_TONE[priority] || 'neutral'}`}>{priority}</span>
}

export function StatusBadge({ status }) {
  return (
    <span className={`badge badge-${STATUS_TONE[status] || 'neutral'}`}>
      <span className="badge-dot" />
      {STATUS_LABEL[status] || status}
    </span>
  )
}

export function initialsFor(name) {
  if (!name) return '?'
  const parts = name.trim().split(/\s+/)
  const first = parts[0]?.[0] || ''
  const last = parts.length > 1 ? parts[parts.length - 1][0] : ''
  return (first + last).toUpperCase() || '?'
}

export function Avatar({ name, title }) {
  return (
    <span className="avatar" title={title || name}>
      {initialsFor(name)}
    </span>
  )
}

export function formatDate(value) {
  if (!value) return null
  try {
    return new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  } catch {
    return value
  }
}

export function isOverdue(dueDate, status) {
  if (!dueDate || status === 'done') return false
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return new Date(dueDate) < today
}
