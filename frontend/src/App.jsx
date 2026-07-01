import { useEffect, useMemo, useState } from 'react'
import { request } from './api.js'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
import { LoginForm } from './components/LoginForm.jsx'
import { SummaryCards } from './components/SummaryCards.jsx'
import { TicketForm } from './components/TicketForm.jsx'
import { TicketDetail } from './components/TicketDetail.jsx'

function Dashboard() {
  const { token, user, logout, setUser } = useAuth()
  const [tickets, setTickets] = useState([])
  const [agents, setAgents] = useState([])
  const [summary, setSummary] = useState(null)
  const [filters, setFilters] = useState({ status: '', priority: '', assigned_agent_id: '' })
  const [selectedTicket, setSelectedTicket] = useState(null)
  const [message, setMessage] = useState('')

  async function loadData() {
    const query = new URLSearchParams()
    if (filters.status) query.set('status', filters.status)
    if (filters.priority) query.set('priority', filters.priority)
    if (filters.assigned_agent_id) query.set('assigned_agent_id', filters.assigned_agent_id)

    const [ticketData, agentData, summaryData] = await Promise.all([
      request(`/tickets?${query.toString()}`, {}, token),
      request('/agents/available', {}, token),
      request('/dashboard/summary', {}, token),
    ])
    setTickets(ticketData)
    setAgents(agentData)
    setSummary(summaryData)
  }

  useEffect(() => {
    loadData().catch((err) => setMessage(err.message))
  }, [filters.status, filters.priority, filters.assigned_agent_id, token])

  async function createTicket(payload) {
    await request(
      '/tickets',
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      token
    )
    setMessage('Ticket created')
    await loadData()
  }

  async function updateStatus(ticketId, status) {
    await request(
      `/tickets/${ticketId}/status`,
      {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      },
      token
    )
    await loadData()
  }

  async function assignTicket(ticketId, assigned_agent_id) {
    await request(
      `/tickets/${ticketId}/assignment`,
      {
        method: 'PATCH',
        body: JSON.stringify({ assigned_agent_id: Number(assigned_agent_id) }),
      },
      token
    )
    setMessage('Assignment notification published')
    await loadData()
  }

  async function toggleAvailability(value) {
    const updated = await request(
      '/agents/me/availability',
      {
        method: 'PATCH',
        body: JSON.stringify({ availability: value }),
      },
      token
    )
    setUser(updated)
    await loadData()
  }

  const statusOptions = useMemo(() => ['Open', 'In Progress', 'Resolved', 'Closed'], [])
  const priorityOptions = useMemo(() => ['Low', 'Medium', 'High', 'Critical'], [])

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>IT Helpdesk Ticketing System</h1>
          <p>Manual intake, assignment, and tracking for support desk operations.</p>
        </div>
        <div className="topbar-actions">
          <label>
            My availability
            <select value={user?.availability || 'available'} onChange={(e) => toggleAvailability(e.target.value)}>
              <option value="available">Available</option>
              <option value="busy">Busy</option>
              <option value="offline">Offline</option>
            </select>
          </label>
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      {message ? <div className="banner">{message}</div> : null}

      <SummaryCards summary={summary} />

      <div className="layout">
        <div className="main-column">
          <TicketForm onCreate={createTicket} />

          <section className="card">
            <div className="section-head">
              <h2>Tickets</h2>
              <div className="filter-row">
                <select value={filters.status} onChange={(e) => setFilters((current) => ({ ...current, status: e.target.value }))}>
                  <option value="">All statuses</option>
                  {statusOptions.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
                <select value={filters.priority} onChange={(e) => setFilters((current) => ({ ...current, priority: e.target.value }))}>
                  <option value="">All priorities</option>
                  {priorityOptions.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
                <select
                  value={filters.assigned_agent_id}
                  onChange={(e) => setFilters((current) => ({ ...current, assigned_agent_id: e.target.value }))}
                >
                  <option value="">All agents</option>
                  {agents.map((agent) => (
                    <option key={agent.id} value={agent.id}>
                      {agent.full_name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="ticket-table">
              {tickets.map((ticket) => (
                <div className="ticket-row" key={ticket.id}>
                  <button className="ticket-title" onClick={() => setSelectedTicket(ticket)}>
                    <strong>{ticket.requester_name}</strong>
                    <span>
                      {ticket.issue_type} · {ticket.priority} · {ticket.status}
                    </span>
                  </button>
                  <div className="ticket-meta">
                    <span>{ticket.assigned_agent?.full_name || 'Unassigned'}</span>
                    <select value={ticket.status} onChange={(e) => updateStatus(ticket.id, e.target.value)}>
                      {statusOptions.map((item) => (
                        <option key={item} value={item}>
                          {item}
                        </option>
                      ))}
                    </select>
                    <select
                      value={ticket.assigned_agent?.id || ''}
                      onChange={(e) => e.target.value && assignTicket(ticket.id, e.target.value)}
                    >
                      <option value="">Assign agent</option>
                      {agents.map((agent) => (
                        <option key={agent.id} value={agent.id}>
                          {agent.full_name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              ))}
              {!tickets.length ? <p>No tickets match the current filters.</p> : null}
            </div>
          </section>
        </div>

        <div className="side-column">
          <TicketDetail ticket={selectedTicket} />

          <section className="card">
            <h2>Agent availability</h2>
            <div className="availability-list">
              {summary?.agent_availability?.map((agent) => (
                <div key={agent.id} className="availability-item">
                  <strong>{agent.full_name}</strong>
                  <span>{agent.availability}</span>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

function App() {
  const auth = useAuth()
  return auth.isAuthenticated ? <Dashboard /> : <LoginForm onLogin={auth.login} loading={auth.loading} />
}

export default function Root() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  )
}
