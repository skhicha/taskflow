import { useEffect, useState } from 'react'
import { Alert } from './ui'

const PRIORITIES = ['low', 'medium', 'high']
const STATUSES = [
  { value: 'todo', label: 'To do' },
  { value: 'in_progress', label: 'In progress' },
  { value: 'done', label: 'Done' },
]

function emptyForm() {
  return { title: '', description: '', priority: 'medium', status: 'todo', assigneeId: '', dueDate: '' }
}

export default function TaskDrawer({ project, task, currentUser, isOwner, onClose, onSubmit, onDelete, busy, error }) {
  const [form, setForm] = useState(emptyForm())
  const [localError, setLocalError] = useState('')

  const isEdit = Boolean(task)
  const isAssignee = isEdit && task.assignee_id === currentUser.id
  const canEditLimited = isEdit && !isOwner && isAssignee
  const readOnly = isEdit && !isOwner && !isAssignee

  useEffect(() => {
    if (task) {
      setForm({
        title: task.title,
        description: task.description || '',
        priority: task.priority,
        status: task.status,
        assigneeId: task.assignee_id != null ? String(task.assignee_id) : '',
        dueDate: task.due_date || '',
      })
    } else {
      setForm(emptyForm())
    }
    setLocalError('')
  }, [task])

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    if (!isEdit && !form.title.trim()) {
      setLocalError('Give the task a title.')
      return
    }
    setLocalError('')

    if (!isEdit) {
      onSubmit({
        title: form.title.trim(),
        description: form.description.trim() || null,
        priority: form.priority,
        assignee_id: form.assigneeId ? Number(form.assigneeId) : null,
        due_date: form.dueDate || null,
      })
      return
    }

    if (canEditLimited) {
      onSubmit({ status: form.status, description: form.description.trim() || null })
      return
    }

    onSubmit({
      title: form.title.trim(),
      description: form.description.trim() || null,
      status: form.status,
      priority: form.priority,
      assignee_id: form.assigneeId ? Number(form.assigneeId) : null,
      due_date: form.dueDate || null,
    })
  }

  return (
    <>
      <div className="scrim" onClick={onClose} />
      <div className="drawer" role="dialog" aria-modal="true" aria-label={isEdit ? 'Edit task' : 'New task'}>
        <div className="drawer-header">
          <h2 className="page-title" style={{ fontSize: 17 }}>
            {isEdit ? 'Task details' : 'New task'}
          </h2>
          <button type="button" className="btn btn-ghost btn-sm" onClick={onClose} aria-label="Close">
            Close
          </button>
        </div>
        <form className="drawer-body" onSubmit={handleSubmit} id="task-form">
          <Alert>{error || localError}</Alert>

          {readOnly && (
            <div className="readonly-note">
              Only the project owner or the assignee can edit this task.
            </div>
          )}

          <div className="field">
            <label className="field-label" htmlFor="task-title">
              Title
            </label>
            <input
              id="task-title"
              className="input"
              value={form.title}
              disabled={readOnly || canEditLimited}
              onChange={(e) => update('title', e.target.value)}
              maxLength={500}
              autoFocus={!isEdit}
            />
          </div>

          <div className="field">
            <label className="field-label" htmlFor="task-description">
              Description
            </label>
            <textarea
              id="task-description"
              className="textarea"
              value={form.description}
              disabled={readOnly}
              onChange={(e) => update('description', e.target.value)}
              maxLength={10000}
            />
          </div>

          <div className="form-row">
            <div className="field">
              <label className="field-label" htmlFor="task-status">
                Status
              </label>
              <select
                id="task-status"
                className="select"
                value={form.status}
                disabled={readOnly || !isEdit}
                onChange={(e) => update('status', e.target.value)}
              >
                {STATUSES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label className="field-label" htmlFor="task-priority">
                Priority
              </label>
              <select
                id="task-priority"
                className="select"
                value={form.priority}
                disabled={readOnly || canEditLimited}
                onChange={(e) => update('priority', e.target.value)}
              >
                {PRIORITIES.map((p) => (
                  <option key={p} value={p}>
                    {p[0].toUpperCase() + p.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="field">
              <label className="field-label" htmlFor="task-assignee">
                Assignee
              </label>
              <select
                id="task-assignee"
                className="select"
                value={form.assigneeId}
                disabled={readOnly || canEditLimited}
                onChange={(e) => update('assigneeId', e.target.value)}
              >
                <option value="">Unassigned</option>
                {project.members.map((m) => (
                  <option key={m.user.id} value={m.user.id}>
                    {m.user.full_name}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label className="field-label" htmlFor="task-due">
                Due date
              </label>
              <input
                id="task-due"
                type="date"
                className="input"
                value={form.dueDate}
                disabled={readOnly || canEditLimited}
                onChange={(e) => update('dueDate', e.target.value)}
              />
            </div>
          </div>
        </form>
        <div className="drawer-footer">
          {isEdit && isOwner ? (
            <button type="button" className="btn btn-danger btn-sm" onClick={onDelete} disabled={busy}>
              Delete task
            </button>
          ) : (
            <span />
          )}
          {!readOnly && (
            <button type="submit" form="task-form" className="btn btn-primary" disabled={busy}>
              {busy ? 'Saving…' : isEdit ? 'Save changes' : 'Create task'}
            </button>
          )}
        </div>
      </div>
    </>
  )
}
