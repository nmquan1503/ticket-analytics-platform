from typing import Dict, List, Any
from app.services.analytics.service import AnalyticService
from app.schemas.analytics import TicketFilter


class SCAnalyticService(AnalyticService):

    # ================================================================
    # 1. KPI tổng quan (dùng lại bộ lọc của lớp cha)
    # ================================================================
    def get_kpi(self, filter: TicketFilter) -> Dict[str, Any]:
        base = ("FROM fact_sc_tickets s "
                "JOIN fact_tickets t ON s.ticket_id = t.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id "
                "LEFT JOIN fact_ticket_process p ON t.process_id = p.id")
        joins, where_, params = self._build_filter_clauses(filter, context="sc")
        sql = f"""
            SELECT
                COUNT(*) AS total_tickets,
                COUNT(CASE WHEN t.ticket_status IN ('New','Inprogress') THEN 1 END) AS open_tickets,
                COUNT(CASE WHEN t.ticket_status IN ('Resolved','Closed') THEN 1 END) AS closed_tickets,
                SUM(CASE WHEN s.sc_khg_status = 'Có' THEN s.cus_qty ELSE 0 END) AS impacted_cust,
                AVG(CASE WHEN p.actual_time > 0 THEN p.actual_time END) AS avg_actual_time,
                ROUND(
                    COUNT(CASE WHEN t.over_time LIKE '%Đúng hạn%' 
                               AND t.ticket_status IN ('Resolved','Closed') THEN 1 END)
                    / NULLIF(COUNT(CASE WHEN t.ticket_status IN ('Resolved','Closed') THEN 1 END),0)*100,2
                ) AS on_time_rate,
                COUNT(CASE WHEN t.priority = 6 THEN 1 END) AS critical_count,
                COUNT(CASE WHEN c.sc_creation_method = 'SC tạo auto' THEN 1 END) AS auto_created,
                COUNT(CASE WHEN s.sc_natural_disaster = 'Có' THEN 1 END) AS disaster_related
            {base} {joins}
            WHERE {where_}
        """
        row = self.db.fetch_one(sql, params)
        return {k: row[k] if row[k] is not None else 0 for k in row}

    # ================================================================
    # 2. Xu hướng nâng cao (dùng analytic functions)
    # ================================================================
    def get_trend(self, filter: TicketFilter) -> List[Dict[str, Any]]:
        base = ("FROM fact_sc_tickets s "
                "JOIN fact_tickets t ON s.ticket_id = t.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="sc")
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

    # ================================================================
    # 3. So sánh cùng kỳ (YoY / MoM)
    # ================================================================
    def get_period_comparison(self, filter: TicketFilter, period: str = 'month') -> List[Dict[str, Any]]:
        group_expr = {
            'month': 'TRUNC(c."date", \'MM\')',
            'week': 'TRUNC(c."date", \'IW\')',
            'quarter': 'TRUNC(c."date", \'Q\')'
        }.get(period, 'TRUNC(c."date", \'MM\')')

        base = ("FROM fact_sc_tickets s "
                "JOIN fact_tickets t ON s.ticket_id = t.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="sc")
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

    # ================================================================
    # 4. Phân phối thời gian xử lý (histogram + percentile)
    # ================================================================
    def get_processing_time_distribution(self, filter: TicketFilter) -> Dict[str, Any]:
        base = ("FROM fact_sc_tickets s "
                "JOIN fact_tickets t ON s.ticket_id = t.id "
                "JOIN fact_ticket_process p ON t.process_id = p.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="sc")
        sql = f"""
            SELECT
                MIN(p.actual_time) AS min_val,
                MAX(p.actual_time) AS max_val,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY p.actual_time) AS median,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY p.actual_time) AS p95,
                AVG(p.actual_time) AS avg_time,
                STDDEV(p.actual_time) AS stddev_time,
                COUNT(*) AS total_processed
            {base} {joins}
            WHERE p.actual_time > 0 AND {where_}
        """
        stats = self.db.fetch_one(sql, params)

        sql_hist = f"""
            SELECT
                bucket,
                MIN(actual_time) AS low,
                MAX(actual_time) AS high,
                COUNT(*) AS freq
            FROM (
                SELECT p.actual_time,
                       WIDTH_BUCKET(p.actual_time, 0, {stats['p95']}, 10) AS bucket
                {base} {joins}
                WHERE p.actual_time > 0 AND {where_}
            )
            GROUP BY bucket
            ORDER BY bucket
        """
        hist = self.db.fetch_all(sql_hist, params)
        return {"statistics": stats, "histogram": hist}

    # ================================================================
    # 5. Pivot table: ca trực (shift) và loại thiết bị
    # ================================================================
    def get_pivot_device_by_shift(self, filter: TicketFilter) -> List[Dict[str, Any]]:
        base = ("FROM fact_sc_tickets s "
                "JOIN fact_tickets t ON s.ticket_id = t.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id "
                "JOIN dim_device_types dt ON s.device_type_id = dt.id")
        joins, where_, params = self._build_filter_clauses(filter, context="sc")
        sql = f"""
            SELECT * FROM (
                SELECT c."shift", dt.name AS device_type, COUNT(*) AS cnt
                {base} {joins}
                WHERE {where_}
                GROUP BY c."shift", dt.name
            )
            PIVOT (SUM(cnt) FOR "shift" IN ('Ca 1' AS ca1, 'Ca 2' AS ca2))
            ORDER BY device_type
        """
        return self.db.fetch_all(sql, params)

    # ================================================================
    # 6. Tương quan (Correlation)
    # ================================================================
    def get_correlation(self, filter: TicketFilter) -> Dict[str, Any]:
        base = ("FROM fact_sc_tickets s "
                "JOIN fact_tickets t ON s.ticket_id = t.id "
                "JOIN fact_ticket_process p ON t.process_id = p.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="sc")
        sql = f"""
            SELECT
                CORR(p.actual_time, s.suspend_time) AS corr_actual_suspend,
                CORR(p.actual_time, c.sc_creation_time) AS corr_actual_creation
            {base} {joins}
            WHERE p.actual_time > 0 AND s.suspend_time > 0 AND {where_}
        """
        return self.db.fetch_one(sql, params)

    # ================================================================
    # 7. Top N có xếp hạng (RANK)
    # ================================================================
    def get_top_branches_ranked(self, filter: TicketFilter, limit: int = 10) -> List[Dict[str, Any]]:
        base = ("FROM fact_sc_tickets s "
                "JOIN fact_tickets t ON s.ticket_id = t.id "
                "JOIN ticket_branch tb ON t.id = tb.ticket_id "
                "JOIN dim_branches b ON tb.branch_id = b.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="sc")
        sql = f"""
            SELECT name, cnt, rnk FROM (
                SELECT b.branch_name AS name, COUNT(*) AS cnt,
                       RANK() OVER (ORDER BY COUNT(*) DESC) AS rnk
                {base} {joins}
                WHERE {where_}
                GROUP BY b.branch_name
            ) WHERE rnk <= {limit}
            ORDER BY rnk
        """
        return self.db.fetch_all(sql, params)

    # ================================================================
    # 8. Oracle Text Search (cần index CONTEXT)
    # ================================================================
    def search_incidents_by_keyword(self, keyword: str, filter: TicketFilter) -> List[Dict[str, Any]]:
        base = ("FROM fact_sc_tickets s "
                "JOIN fact_tickets t ON s.ticket_id = t.id "
                "JOIN dim_ticket_description d ON s.description_id = d.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="sc")
        sql = f"""
            SELECT t.code, TO_CHAR(c."date", 'YYYY-MM-DD') AS ticket_date, d.description
            {base} {joins}
            WHERE CONTAINS(d.description, :kw, 1) > 0 AND {where_}
            FETCH FIRST 20 ROWS ONLY
        """
        params["kw"] = keyword
        return self.db.fetch_all(sql, params)

    # ================================================================
    # 9. Cây sự cố (CONNECT BY) – chỉ dùng nếu parent là số
    # ================================================================
    def get_incident_tree(self, root_ticket_id: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT t.code, LEVEL, SYS_CONNECT_BY_PATH(t.code, ' -> ') AS path
            FROM fact_sc_tickets s
            JOIN fact_tickets t ON s.ticket_id = t.id
            START WITH s.ticket_id = :root
            CONNECT BY PRIOR s.ticket_id = s.parent
        """
        return self.db.fetch_all(sql, {"root": root_ticket_id})

    # ================================================================
    # 10. Pareto (80/20) cho nhóm sự cố
    # ================================================================
    def get_pareto_issue_groups(self, filter: TicketFilter) -> List[Dict[str, Any]]:
        base = ("FROM fact_sc_tickets s "
                "JOIN fact_tickets t ON s.ticket_id = t.id "
                "JOIN dim_issue_names i ON t.issue_name_id = i.id "
                "JOIN dim_issue_groups ig ON i.issue_group_id = ig.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="sc")
        sql = f"""
            WITH group_counts AS (
                SELECT ig.name, COUNT(*) AS cnt
                {base} {joins}
                WHERE {where_}
                GROUP BY ig.name
            ),
            total AS (
                SELECT SUM(cnt) AS total_cnt FROM group_counts
            )
            SELECT
                gc.name,
                gc.cnt,
                ROUND(gc.cnt * 100.0 / t.total_cnt, 1) AS pct,
                SUM(gc.cnt) OVER (ORDER BY gc.cnt DESC) AS cumulative_cnt,
                ROUND(SUM(gc.cnt * 100.0 / t.total_cnt) OVER (ORDER BY gc.cnt DESC), 1) AS cumulative_pct
            FROM group_counts gc, total t
            ORDER BY gc.cnt DESC
        """
        return self.db.fetch_all(sql, params)

    # ================================================================
    # 11. Ca hiện tại so với ca trước
    # ================================================================
    def get_current_shift_vs_previous(self, filter: TicketFilter) -> Dict[str, Any]:
        base = ("FROM fact_sc_tickets s "
                "JOIN fact_tickets t ON s.ticket_id = t.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="sc")
        sql = f"""
            WITH shift_counts AS (
                SELECT c."shift", TRUNC(c.created_datetime) AS dt, COUNT(*) AS cnt,
                       ROW_NUMBER() OVER (ORDER BY TRUNC(c.created_datetime) DESC, c."shift" DESC) AS rn
                {base} {joins}
                WHERE {where_}
                GROUP BY c."shift", TRUNC(c.created_datetime)
            )
            SELECT "shift", cnt
            FROM shift_counts
            WHERE rn <= 2
            ORDER BY rn
        """
        rows = self.db.fetch_all(sql, params)
        if len(rows) == 2:
            return {"current_shift": rows[0], "previous_shift": rows[1]}
        return {"current_shift": rows[0] if rows else None, "previous_shift": None}

    # ================================================================
    # Các API Machine Learning (giữ nguyên cấu trúc, cập nhật cột)
    # ================================================================
    def get_forecast(self, filter: TicketFilter, days_ahead: int = 7) -> Dict[str, Any]:
        base = ("FROM fact_sc_tickets s "
                "JOIN fact_tickets t ON s.ticket_id = t.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="sc")
        sql_actual = f"""
            SELECT TO_CHAR(c."date", 'YYYY-MM-DD') AS day, COUNT(*) AS cnt
            {base} {joins}
            WHERE {where_}
            GROUP BY c."date"
            ORDER BY c."date"
        """
        actual = self.db.fetch_all(sql_actual, params)
        sql_forecast = """
            SELECT TO_CHAR(day, 'YYYY-MM-DD') AS day, forecast_value AS forecast
            FROM TABLE(DBMS_DATA_MINING.FORECAST(
                model_name => 'SC_FORECAST_ESM',
                steps_ahead => :steps
            ))
        """
        forecast = self.db.fetch_all(sql_forecast, {"steps": days_ahead})
        return {"actual": actual, "forecast": forecast}

    def get_anomalies(self, filter: TicketFilter) -> List[Dict[str, Any]]:
        base = ("FROM fact_sc_tickets s "
                "JOIN fact_tickets t ON s.ticket_id = t.id "
                "JOIN fact_ticket_process p ON t.process_id = p.id "
                "JOIN fact_ticket_creation c ON t.creation_id = c.id")
        joins, where_, params = self._build_filter_clauses(filter, context="sc")
        sql = f"""
            WITH stats AS (
                SELECT
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY p.actual_time) AS q1,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY p.actual_time) AS q3
                {base} {joins}
                WHERE p.actual_time > 0 AND {where_}
            ),
            thresholds AS (
                SELECT q1, q3, q3 - q1 AS iqr,
                       q1 - 1.5 * (q3 - q1) AS lower_bound,
                       q3 + 1.5 * (q3 - q1) AS upper_bound
                FROM stats
            )
            SELECT t.code, TO_CHAR(c."date", 'YYYY-MM-DD') AS ticket_date,
                   p.actual_time,
                   CASE WHEN p.actual_time < lower_bound THEN 'Low'
                        WHEN p.actual_time > upper_bound THEN 'High'
                        ELSE 'Normal' END AS anomaly_type
            {base}, thresholds
            WHERE p.actual_time > 0 AND {where_}
              AND (p.actual_time < lower_bound OR p.actual_time > upper_bound)
            ORDER BY p.actual_time DESC
            FETCH FIRST 30 ROWS ONLY
        """
        return self.db.fetch_all(sql, params)

    def get_clusters(self, filter: TicketFilter) -> List[Dict[str, Any]]:
        try:
            return self.db.fetch_all("""
                SELECT cluster_id, COUNT(*) AS cnt
                FROM (
                    SELECT PREDICTION(SC_CLUSTER_KM USING *) AS cluster_id
                    FROM v_sc_features
                )
                GROUP BY cluster_id
                ORDER BY cluster_id
            """, {})
        except Exception:
            return []

    def get_predicted_priority(self, description: str) -> Dict[str, Any]:
        sql = """
            SELECT PREDICTION(SC_PRIORITY_CLASS USING :desc) AS predicted_priority
            FROM DUAL
        """
        return self.db.fetch_one(sql, {"desc": description})