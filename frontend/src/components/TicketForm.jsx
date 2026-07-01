import { useState } from 'react'

const issueTypes = ['Hardware', 'Software', 'Network', 'Account', 'Other']
const priorities = ['Low', 'Medium', 'High', 'Critical']
const statuses = ['Open', 'In Progress', 'Resolved', 'Closed']

const initialState = {
  requester_name: '',
  requester_contact: '',
  issue_type: 'Hardware',
  description: '',
  priority: 'Medium',
  status: 'Open',
  asset_id: '',
}

export function TicketForm({ onCreate }) {
  const [form, setForm] = useState(initialState)
  const [error, setError] = useState('')

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    try {
      await onCreate({
        ...form,
        asset_id: form.asset_id ? Number(form.asset_id) : null,
      })
      setForm(initialState)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2>Create ticket</h2>
      <div className="grid two-col">
        <label>
          Requester name
          <input value={form.requester_name} onChange={(e) => updateField('requester_name', e.target.value)} required />
        </label>
        <label>
          Contact info
          <input value={form.requester_contact} onChange={(e) => updateField('requester_contact', e.target.value)} required />
        </label>
        <label>
          Issue type
          <select value={form.issue_type} onChange={(e) => updateField('issue_type', e.target.value)}>
            {issueTypes.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
        <label>
          Priority
          <select value={form.priority} onChange={(e) => updateField('priority', e.target.value)}>
            {priorities.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
        <label>
          Status
          <select value={form.status} onChange={(e) => updateField('status', e.target.value)}>
            {statuses.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
        <label>
          Asset ID
          <input value={form.asset_id} onChange={(e) => updateField('asset_id', e.target.value)} inputMode="numeric" />
        </label>
      </div>
      <label>
        Description
        <textarea value={form.description} onChange={(e) => updateField('description', e.target.value)} rows="4" required />
      </label>
      {error ? <div className="error">{error}</div> : null}
      <button type="submit">Save ticket</button>
    </form>
  )
}
