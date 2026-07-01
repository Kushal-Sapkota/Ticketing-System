export function SummaryCards({ summary }) {
  if (!summary) {
    return null
  }

  return (
    <div className="summary-grid">
      <div className="card metric">
        <span>Open tickets</span>
        <strong>{summary.open_tickets}</strong>
      </div>
      <div className="card metric">
        <span>Tickets by priority</span>
        {summary.tickets_by_priority.map((item) => (
          <div key={item.priority}>
            {item.priority}: {item.count}
          </div>
        ))}
      </div>
      <div className="card metric">
        <span>Tickets per agent</span>
        {summary.tickets_per_agent.map((item) => (
          <div key={item.id}>
            {item.full_name}: {item.ticket_count}
          </div>
        ))}
      </div>
    </div>
  )
}
