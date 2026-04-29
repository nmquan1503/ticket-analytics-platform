from typing import Dict, List, Any
from app.services.analytics.service import AnalyticService
from app.schemas.analytics import TicketFilter

class HTAnalyticService(AnalyticService):
    # ----------------------------------------------------------------
    # 1. KPI tổng quan
    # ----------------------------------------------------------------
    def get_kpi(self, filter: TicketFilter) -> Dict[str, Any]:
        base = ("FROM fact_ht_tickets h "
                "JOIN fact_tickets t ON h.ticket_id = t.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="ht")
        sql = f"""
            SELECT
                COUNT(*) AS total_tickets,
                COUNT(CASE WHEN t.ticket_status IN ('New','Inprogress') THEN 1 END) AS open_tickets,
                COUNT(CASE WHEN t.ticket_status IN ('Resolved','Closed') THEN 1 END) AS closed_tickets,
                COUNT(CASE WHEN h.sos_ticket_flag = 'Có' THEN 1 END) AS sos_tickets,
                COUNT(CASE WHEN h.required = 'Có' THEN 1 END) AS required_tickets,
                ROUND(
                    COUNT(CASE WHEN h.deadline_status = 'Đúng hạn'
                               AND t.ticket_status IN ('Resolved','Closed') THEN 1 END)
                    / NULLIF(COUNT(CASE WHEN t.ticket_status IN ('Resolved','Closed') THEN 1 END),0)*100,2
                ) AS on_time_rate,
                SUM(h.rejection_count) AS total_rejections,
                SUM(h.response_count) AS total_responses,
                COUNT(CASE WHEN h.sla_violation_count != 'Không' THEN 1 END) AS sla_violations,
                AVG(h.ticket_age_days) AS avg_ticket_age_days
            {base} {joins}
            WHERE {where_}
        """
        row = self.db.fetch_one(sql, params)
        return {k: row[k] if row[k] is not None else 0 for k in row}

    # ----------------------------------------------------------------
    # 2. Xu hướng theo ngày
    # ----------------------------------------------------------------
    def get_trend(self, filter: TicketFilter) -> List[Dict[str, Any]]:
        base = ("FROM fact_ht_tickets h "
                "JOIN fact_tickets t ON h.ticket_id = t.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="ht")
        sql = f"""
            SELECT
                TO_CHAR(day, 'YYYY-MM-DD') AS ticket_date,
                cnt,
                ROUND(AVG(cnt) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS moving_avg_7d,
                LAG(cnt,1) OVER (ORDER BY day) AS prev_cnt,
                ROUND((cnt - LAG(cnt,1) OVER (ORDER BY day)) * 100.0 /
                      NULLIF(LAG(cnt,1) OVER (ORDER BY day),0), 2) AS change_pct,
                SUM(cnt) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_cnt
            FROM (
                SELECT c."date" AS day, COUNT(*) AS cnt
                {base} {joins}
                WHERE {where_}
                GROUP BY c."date"
            )
            ORDER BY day
        """
        return self.db.fetch_all(sql, params)

    # ----------------------------------------------------------------
    # 3. So sánh cùng kỳ
    # ----------------------------------------------------------------
    def get_period_comparison(self, filter: TicketFilter, period: str = 'month') -> List[Dict[str, Any]]:
        group_expr = {
            'month': 'TRUNC(c."date", \'MM\')',
            'week': 'TRUNC(c."date", \'IW\')',
            'quarter': 'TRUNC(c."date", \'Q\')'
        }.get(period, 'TRUNC(c."date", \'MM\')')
        base = ("FROM fact_ht_tickets h "
                "JOIN fact_tickets t ON h.ticket_id = t.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="ht")
        sql = f"""
            WITH monthly AS (
                SELECT {group_expr} AS period_start, COUNT(*) AS cnt
                {base} {joins}
                WHERE {where_}
                GROUP BY {group_expr}
            )
            SELECT
                TO_CHAR(period_start, 'YYYY-MM-DD') AS period,
                cnt,
                LAG(cnt, 1) OVER (ORDER BY period_start) AS prev_period,
                LAG(cnt, 12) OVER (ORDER BY period_start) AS same_period_last_year,
                ROUND((cnt - LAG(cnt,1) OVER (ORDER BY period_start)) * 100.0 /
                      NULLIF(LAG(cnt,1) OVER (ORDER BY period_start),0), 2) AS mom_change_pct,
                ROUND((cnt - LAG(cnt,12) OVER (ORDER BY period_start)) * 100.0 /
                      NULLIF(LAG(cnt,12) OVER (ORDER BY period_start),0), 2) AS yoy_change_pct
            FROM monthly
            ORDER BY period_start
        """
        return self.db.fetch_all(sql, params)

    # ----------------------------------------------------------------
    # 4. Phân phối theo bước xử lý
    # ----------------------------------------------------------------
    def get_step_distribution(self, filter: TicketFilter) -> List[Dict[str, Any]]:
        base = ("FROM fact_ht_tickets h "
                "JOIN fact_tickets t ON h.ticket_id = t.id "
                "JOIN dim_ht_steps s ON h.step_id = s.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="ht")
        sql = f"""
            SELECT s.name AS step_name, COUNT(*) AS value
            {base} {joins}
            WHERE {where_}
            GROUP BY s.name
            ORDER BY value DESC
        """
        return self.db.fetch_all(sql, params)

    # ----------------------------------------------------------------
    # 5. Phân phối theo deadline_status
    # ----------------------------------------------------------------
    def get_deadline_distribution(self, filter: TicketFilter) -> List[Dict[str, Any]]:
        base = ("FROM fact_ht_tickets h "
                "JOIN fact_tickets t ON h.ticket_id = t.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="ht")
        sql = f"""
            SELECT h.deadline_status AS name, COUNT(*) AS value
            {base} {joins}
            WHERE {where_}
            GROUP BY h.deadline_status
            ORDER BY value DESC
        """
        return self.db.fetch_all(sql, params)

    # ----------------------------------------------------------------
    # 6. Top queue xử lý (dùng RANK)
    # ----------------------------------------------------------------
    def get_top_processing_queues(self, filter: TicketFilter, limit: int = 10) -> List[Dict[str, Any]]:
        base = ("FROM fact_ht_tickets h "
                "JOIN fact_tickets t ON h.ticket_id = t.id "
                "JOIN fact_ticket_process p ON t.process_id = p.id "
                "JOIN dim_queues q ON p.queue_process_id = q.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="ht")
        sql = f"""
            SELECT q.name AS queue_name, COUNT(*) AS cnt,
                   RANK() OVER (ORDER BY COUNT(*) DESC) AS rnk
            {base} {joins}
            WHERE {where_}
            GROUP BY q.name
            ORDER BY cnt DESC
            FETCH FIRST {limit} ROWS ONLY
        """
        return self.db.fetch_all(sql, params)

    # ----------------------------------------------------------------
    # 7. Phân tích thời gian phản hồi (histogram từ lịch sử)
    # ----------------------------------------------------------------
    def get_response_time_analysis(self, filter: TicketFilter) -> Dict[str, Any]:
        base = ("FROM fact_ht_tickets h "
                "JOIN fact_tickets t ON h.ticket_id = t.id "
                "JOIN ht_ticket_history hist ON h.ticket_id = hist.ht_ticket_id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="ht")
        sql = f"""
            SELECT
                AVG(hist.response_time_minutes) AS avg_response,
                MEDIAN(hist.response_time_minutes) AS median_response,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY hist.response_time_minutes) AS p95
            {base} {joins}
            WHERE hist.response_time_minutes IS NOT NULL AND {where_}
        """
        stats = self.db.fetch_one(sql, params)
        # Histogram với WIDTH_BUCKET
        sql_hist = f"""
            SELECT bucket,
                   MIN(response_time_minutes) AS low,
                   MAX(response_time_minutes) AS high,
                   COUNT(*) AS freq
            FROM (
                SELECT hist.response_time_minutes,
                       WIDTH_BUCKET(hist.response_time_minutes, 0, 120, 10) AS bucket
                {base} {joins}
                WHERE hist.response_time_minutes IS NOT NULL AND {where_}
            )
            GROUP BY bucket
            ORDER BY bucket
        """
        hist = self.db.fetch_all(sql_hist, params)
        return {"statistics": stats, "histogram": hist}

    # ----------------------------------------------------------------
    # 8. Pivot SLA theo loại dịch vụ
    # ----------------------------------------------------------------
    def get_sla_by_service_pivot(self, filter: TicketFilter) -> List[Dict[str, Any]]:
        base = ("FROM fact_ht_tickets h "
                "JOIN fact_tickets t ON h.ticket_id = t.id "
                "JOIN dim_ht_service_types srv ON h.service_type_id = srv.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="ht")
        sql = f"""
            SELECT * FROM (
                SELECT srv.name AS service_type, h.deadline_status, COUNT(*) AS cnt
                {base} {joins}
                WHERE {where_}
                GROUP BY srv.name, h.deadline_status
            )
            PIVOT (SUM(cnt) FOR deadline_status IN ('Đúng hạn' AS on_time, 'Quá hạn' AS overdue))
            ORDER BY service_type
        """
        return self.db.fetch_all(sql, params)

    # ----------------------------------------------------------------
    # 9. Tương quan giữa tuổi thọ ticket & số lần từ chối
    # ----------------------------------------------------------------
    def get_correlation_age_rejection(self, filter: TicketFilter) -> Dict[str, Any]:
        base = ("FROM fact_ht_tickets h "
                "JOIN fact_tickets t ON h.ticket_id = t.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="ht")
        sql = f"""
            SELECT CORR(h.ticket_age_days, h.rejection_count) AS corr_age_rejection
            {base} {joins}
            WHERE {where_}
        """
        return self.db.fetch_one(sql, params)