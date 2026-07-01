from enum import Enum


class AgentRole(str, Enum):
    agent = "agent"
    admin = "admin"


class AvailabilityStatus(str, Enum):
    available = "available"
    busy = "busy"
    offline = "offline"


class IssueType(str, Enum):
    hardware = "Hardware"
    software = "Software"
    network = "Network"
    account = "Account"
    other = "Other"


class PriorityLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class TicketStatus(str, Enum):
    open = "Open"
    in_progress = "In Progress"
    resolved = "Resolved"
    closed = "Closed"


class TicketEventAction(str, Enum):
    created = "created"
    status_changed = "status_changed"
    assigned = "assigned"
