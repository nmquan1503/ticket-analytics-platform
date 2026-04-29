from pydantic import BaseModel
from typing import List, Optional

class TicketFilter(BaseModel):
    date_range: Optional[int] = None
    locations: Optional[List[str]] = None
    branches: Optional[List[str]] = None
    priorities: Optional[List[int]] = None

class Ticket(BaseModel):
    ticket_id: int
    status: str
    location: str
    branch_name: str
    actual_time: int
    suspend_time: int
    rejection_count: int
    sla_status: str


class TicketResponse(BaseModel):
    data: List[Ticket]
    total: int