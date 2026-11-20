import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, errorMessage } from '../api/client'
import { useAuth } from '../context/AuthContext'
import TaskDrawer from '../components/TaskDrawer'
import {
  Alert,
  Avatar,
  EmptyState,
  LoadingRow,
  PriorityBadge,
  formatDate,
  isOverdue,
} from '../components/ui'

const COLUMNS = [
  { key: 'todo', label: 'To do' },
  { key: 'in_progress', label: 'In progress' },
  { key: 'done', label: 'Done' },
]

const TASK_PAGE_SIZE = 100

export default function ProjectPage() {
  const { id } = useParams()
  const projectId = Number(id)
  const navigate = useNavigate()
  const { user } = useAuth()

  const [project, setProject] = useState(null)
  const [tasksData, setTasksData] = useState({ items: [], total: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [accessDenied, setAccessDenied] = useState(false)

  const [activeTask, setActiveTask] = useState(undefined) // undefined = closed, null = create, object = edit
  const [drawerBusy, setDrawerBusy] = useState(false)
  const [drawerError, setDrawerError] = useState('')

  const [memberEmail, setMemberEmail] = useState('')
  const [memberError, setMemberError] = useState('')
  const [addingMember, setAddingMember] = useState(false)
  const [showMemberForm, setShowMemberForm] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    setAccessDenied(false)
    try {
      const [projectRes, tasksRes] = await Promise.all([
        api.get(`/api/projects/${projectId}`),
        api.get(`/api/projects/${projectId}/tasks`, { params: { page: 1, size: TASK_PAGE_SIZE } }),
      ])
      setProject(projectRes.data)
      setTasksData(tasksRes.data)
    } catch (err) {
      if (err?.response?.status === 403 || err?.response?.status === 404) {
        setAccessDenied(true)
      } else {
        setError(errorMessage(err, 'Could not load this project.'))
      }
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    load()
  }, [load])

  const isOwner = project ? project.owner_id === user.id : false

  async function handleDeleteProject() {
    if (!window.confirm('Delete this project and all of its tasks? This cannot be undone.')) return
    try {
      await api.delete(`/api/projects/${projectId}`)
      navigate('/')
    } catch (err) {
      setError(errorMessage(err, 'Could not delete this project.'))
    }
  }

  async function handleAddMember(e) {
    e.preventDefault()
    setMemberError('')
    if (!memberEmail.trim()) {
      setMemberError('Enter a member email.')
      return
    }
    setAddingMember(true)
    try {
      await api.post(`/api/projects/${projectId}/members`, { email: memberEmail.trim() })
      setMemberEmail('')
      setShowMemberForm(false)
      load()
    } catch (err) {
      setMemberError(errorMessage(err, 'Could not add that member.'))
    } finally {
      setAddingMember(false)
    }
  }

  async function handleTaskSubmit(payload) {
    setDrawerBusy(true)
    setDrawerError('')
    try {
      if (activeTask) {
        await api.patch(`/api/tasks/${activeTask.id}`, payload)
      } else {
        await api.post(`/api/projects/${projectId}/tasks`, payload)
      }
      setActiveTask(undefined)
      load()
    } catch (err) {
      setDrawerError(errorMessage(err, 'Could not save this task.'))
    } finally {
      setDrawerBusy(false)
    }
  }

  async function handleTaskDelete() {
    if (!activeTask) return
    if (!window.confirm('Delete this task?')) return
    setDrawerBusy(true)
    try {
      await api.delete(`/api/tasks/${activeTask.id}`)
      setActiveTask(undefined)
      load()
    } catch (err) {
      setDrawerError(errorMessage(err, 'Could not delete this task.'))
    } finally {
      setDrawerBusy(false)
    }
  }

  if (loading) {
    return <LoadingRow label="Loading project…" />
  }

  if (accessDenied) {
    return (
      <EmptyState
        title="You don't have access to this project"
        body="Ask the project owner to add you as a member, or go back to your projects."
        action={
          <Link className="btn btn-secondary btn-sm" to="/">
            Back to projects
          </Link>
        }
      />
    )
  }

  if (!project) {
    return <Alert>{error}</Alert>
  }

  const tasksByStatus = COLUMNS.reduce((acc, col) => {
    acc[col.key] = tasksData.items.filter((t) => t.status === col.key)
    return acc
  }, {})

  return (
    <div>
      <div className="breadcrumb">
        <Link to="/">Projects</Link> / {project.name}
      </div>
      <div className="page-header">
        <div>
          <h1 className="page-title">
            {project.name}
            {isOwner && <span className="badge badge-accent owner-tag">Owner</span>}
          </h1>
          {project.description && <p className="page-subtitle">{project.description}</p>}
        </div>
        <div className="page-actions">
          <button type="button" className="btn btn-primary" onClick={() => setActiveTask(null)}>
            New task
          </button>
          {isOwner && (
            <button type="button" className="btn btn-danger" onClick={handleDeleteProject}>
              Delete project
            </button>
          )}
        </div>
      </div>

      <Alert>{error}</Alert>

      <div className="card panel">
        <div className="panel-title">Members</div>
        <div className="member-list">
          {project.members.map((m) => (
            <span key={m.user.id} className="member-chip">
              <Avatar name={m.user.full_name} />
              {m.user.full_name}
              {m.role === 'owner' && <span className="badge badge-neutral">owner</span>}
            </span>
          ))}
        </div>
        {isOwner && (
          <div style={{ marginTop: 12 }}>
            {showMemberForm ? (
              <form className="inline-form" onSubmit={handleAddMember}>
                <div className="field">
                  <label className="field-label" htmlFor="member-email">
                    Member email
                  </label>
                  <input
                    id="member-email"
                    type="email"
                    className="input"
                    value={memberEmail}
                    onChange={(e) => setMemberEmail(e.target.value)}
                    autoFocus
                  />
                </div>
                <button type="submit" className="btn btn-primary btn-sm" disabled={addingMember}>
                  {addingMember ? 'Adding…' : 'Add member'}
                </button>
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => setShowMemberForm(false)}>
                  Cancel
                </button>
              </form>
            ) : (
              <button type="button" className="btn btn-secondary btn-sm" onClick={() => setShowMemberForm(true)}>
                Add member
              </button>
            )}
            {memberError && <div className="field-error" style={{ marginTop: 8 }}>{memberError}</div>}
          </div>
        )}
      </div>

      {tasksData.items.length === 0 ? (
        <EmptyState
          title="No tasks yet"
          body="Add the first task to start tracking work on this project."
          action={
            <button type="button" className="btn btn-primary btn-sm" onClick={() => setActiveTask(null)}>
              New task
            </button>
          }
        />
      ) : (
        <div className="board">
          {COLUMNS.map((col) => (
            <div className="board-column" key={col.key}>
              <div className="board-column-header">
                <span className="board-column-title">{col.label}</span>
                <span className="board-column-count">{tasksByStatus[col.key].length}</span>
              </div>
              <div className="board-cards">
                {tasksByStatus[col.key].length === 0 && (
                  <div className="field-hint" style={{ padding: '0 4px' }}>
                    No tasks here yet.
                  </div>
                )}
                {tasksByStatus[col.key].map((task) => {
                  const assignee = project.members.find((m) => m.user.id === task.assignee_id)
                  const overdue = isOverdue(task.due_date, task.status)
                  return (
                    <button
                      key={task.id}
                      type="button"
                      className="task-card"
                      onClick={() => setActiveTask(task)}
                    >
                      <div className="task-card-title">{task.title}</div>
                      <div className="task-card-footer">
                        <div className="task-card-badges">
                          <PriorityBadge priority={task.priority} />
                          {task.due_date && (
                            <span className={`task-card-due${overdue ? ' overdue' : ''}`}>
                              {formatDate(task.due_date)}
                            </span>
                          )}
                        </div>
                        {assignee && <Avatar name={assignee.user.full_name} title={assignee.user.full_name} />}
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {tasksData.total > TASK_PAGE_SIZE && (
        <p className="field-hint" style={{ marginTop: 16 }}>
          Showing the first {TASK_PAGE_SIZE} of {tasksData.total} tasks.
        </p>
      )}

      {activeTask !== undefined && (
        <TaskDrawer
          project={project}
          task={activeTask}
          currentUser={user}
          isOwner={isOwner}
          onClose={() => {
            setActiveTask(undefined)
            setDrawerError('')
          }}
          onSubmit={handleTaskSubmit}
          onDelete={handleTaskDelete}
          busy={drawerBusy}
          error={drawerError}
        />
      )}
    </div>
  )
}
