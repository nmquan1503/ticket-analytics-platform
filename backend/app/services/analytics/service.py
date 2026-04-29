from app.db.oracle_client import OracleClient
from app.schemas.analytics import TicketFilter


class AnalyticService:
    def __init__(self):
        self.db = OracleClient()

    def _build_filter_clauses(self, filter: TicketFilter, context: str = "sc"):
        additional_joins = ""
        where_parts = []
        params = {}

        # date_range – dùng cột "date" (chữ thường, trong dấu ngoặc kép)
        if filter.date_range is not None:
            where_parts.append('c."date" >= TRUNC(SYSDATE) - :days')
            params["days"] = filter.date_range

        # locations
        if filter.locations:
            additional_joins += " JOIN ticket_location tl ON t.id = tl.ticket_id"
            additional_joins += " JOIN dim_locations l ON tl.location_id = l.id"
            placeholders = ", ".join(f":loc{i}" for i in range(len(filter.locations)))
            where_parts.append(f"l.name IN ({placeholders})")
            for i, loc in enumerate(filter.locations):
                params[f"loc{i}"] = loc

        # branches
        if filter.branches:
            additional_joins += " JOIN ticket_branch tb ON t.id = tb.ticket_id"
            additional_joins += " JOIN dim_branches b ON tb.branch_id = b.id"
            placeholders = ", ".join(f":br{i}" for i in range(len(filter.branches)))
            where_parts.append(f"b.name IN ({placeholders})")
            for i, br in enumerate(filter.branches):
                params[f"br{i}"] = br

        # priorities
        if filter.priorities:
            placeholders = ", ".join(f":prio{i}" for i in range(len(filter.priorities)))
            where_parts.append(f"t.priority IN ({placeholders})")
            for i, prio in enumerate(filter.priorities):
                params[f"prio{i}"] = prio

        where_clause = " AND ".join(where_parts) if where_parts else "1=1"
        return additional_joins, where_clause, params