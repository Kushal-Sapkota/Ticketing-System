export function TicketDetail({ ticket }) {
  if (!ticket) {
    return (
      <div className="card">
        <h2>Ticket details</h2>
        <p>Select a ticket to see the audit trail.</p>
      </div>
    )
  }

  return (
    <div className="card">
      <h2>Ticket details</h2>
      <div className="detail-grid">
        <div><strong>ID:</strong> {ticket.id}</div>
        <div><strong>Status:</strong> {ticket.status}</div>
        <div><strong>Priority:</strong> {ticket.priority}</div>
        <div><strong>Type:</strong> {ticket.issue_type}</div>
        <div><strong>Requester:</strong> {ticket.requester_name}</div>
        <div><strong>Contact:</strong> {ticket.requester_contact}</div>
        <div><strong>Assigned:</strong> {ticket.assigned_agent?.full_name || 'Unassigned'}</div>
      </div>
      <p>{ticket.description}</p>
      <h3>History</h3>
      <div className="history">
        {ticket.history?.length ? (
          ticket.history.map((event) => (
            <div className="history-item" key={event.id}>
              <strong>{event.action}</strong> {event.field_name ? `(${event.field_name})` : ''}
              <div>{event.old_value || '—'} → {event.new_value || '—'}</div>
              <small>
                {event.actor?.full_name || 'System'} · {new Date(event.created_at).toLocaleString()}
              </small>
            </div>
          ))
        ) : (
          <p>No history yet.</p>
        )}
      </div>
    </div>
  )
}
