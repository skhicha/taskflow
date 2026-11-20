import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, errorMessage } from '../api/client'
import { Alert, EmptyState, LoadingRow, formatDate } from '../components/ui'

const PAGE_SIZE = 12

export default function DashboardPage() {
  const [page, setPage] = useState(1)
  const [data, setData] = useState({ items: [], total: 0, pages: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [createError, setCreateError] = useState('')
  const [creating, setCreating] = useState(false)

  const load = useCallback(async (targetPage) => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/api/projects', { params: { page: targetPage, size: PAGE_SIZE } })
      setData(res.data)
    } catch (err) {
      setError(errorMessage(err, 'Could not load your projects.'))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load(page)
  }, [page, load])

  async function handleCreate(e) {
    e.preventDefault()
    if (!name.trim()) {
      setCreateError('Give the project a name.')
      return
    }
    setCreating(true)
    setCreateError('')
    try {
      await api.post('/api/projects', { name: name.trim(), description: description.trim() || null })
      setName('')
      setDescription('')
      setShowForm(false)
      setPage(1)
      load(1)
    } catch (err) {
      setCreateError(errorMessage(err, 'Could not create the project.'))
    } finally {
      setCreating(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Projects</h1>
          <p className="page-subtitle">Everything you own or have been added to as a member.</p>
        </div>
        <div className="page-actions">
          <button type="button" className="btn btn-primary" onClick={() => setShowForm((s) => !s)}>
            New project
          </button>
        </div>
      </div>

      {showForm && (
        <form className="card panel" onSubmit={handleCreate}>
          <div className="panel-title">New project</div>
          <Alert>{createError}</Alert>
          <div className="inline-form">
            <div className="field">
              <label className="field-label" htmlFor="project-name">
                Name
              </label>
              <input
                id="project-name"
                className="input"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoFocus
              />
            </div>
            <div className="field">
              <label className="field-label" htmlFor="project-desc">
                Description (optional)
              </label>
              <input
                id="project-desc"
                className="input"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={creating}>
              {creating ? 'Creating…' : 'Create'}
            </button>
            <button type="button" className="btn btn-ghost" onClick={() => setShowForm(false)}>
              Cancel
            </button>
          </div>
        </form>
      )}

      <Alert>{error}</Alert>

      {loading ? (
        <LoadingRow label="Loading projects…" />
      ) : data.items.length === 0 ? (
        <EmptyState
          title="No projects yet"
          body="Create your first project to start organizing tasks with your team."
          action={
            <button type="button" className="btn btn-primary btn-sm" onClick={() => setShowForm(true)}>
              New project
            </button>
          }
        />
      ) : (
        <>
          <div className="project-grid">
            {data.items.map((project) => (
              <Link key={project.id} to={`/projects/${project.id}`} className="card project-card">
                <div className="project-card-name">{project.name}</div>
                <div className="project-card-desc">{project.description || 'No description yet.'}</div>
                <div className="project-card-meta">
                  <span>Created {formatDate(project.created_at)}</span>
                </div>
              </Link>
            ))}
          </div>
          {data.pages > 1 && (
            <div className="pagination">
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </button>
              <span>
                Page {page} of {data.pages}
              </span>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                disabled={page >= data.pages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
