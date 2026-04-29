from fastapi import APIRouter, Depends, Query, Body
from typing import Optional, List

from app.schemas.analytics import TicketFilter
from app.services.analytics.sc_service import SCAnalyticService

router = APIRouter(prefix="/sc_analytics", tags=["SC Analytics"])

sc_service = SCAnalyticService()
# sc_service = None

def build_filter(
    date_range: Optional[int] = Query(None, description="Số ngày gần nhất (vd: 7, 30)"),
    locations: Optional[List[str]] = Query(None, description="Danh sách khu vực"),
    branches: Optional[List[str]] = Query(None, description="Danh sách chi nhánh"),
    priorities: Optional[List[int]] = Query(None, description="Danh sách mức ưu tiên (1-6)"),
) -> TicketFilter:
    return TicketFilter(
        date_range=date_range,
        locations=locations,
        branches=branches,
        priorities=priorities
    )


@router.get("/")
def analytics_root():
    return {"message": "SC Analytics service is running (MOCK DATA)"}


# ---------------------------------------------------------------
# KPI
# ---------------------------------------------------------------
@router.get("/kpi")
def get_kpi(filter: TicketFilter = Depends(build_filter)):
    # return sc_service.get_kpi(filter)
    return {
        "total_tickets": 1247,
        "open_tickets": 89,
        "closed_tickets": 1023,
        "impacted_cust": 15420,
        "avg_actual_time": 45.3,
        "on_time_rate": 87.2,
        "critical_count": 32,
        "auto_created": 712,
        "disaster_related": 15
    }


# ---------------------------------------------------------------
# Trend
# ---------------------------------------------------------------
@router.get("/trend")
def get_trend(filter: TicketFilter = Depends(build_filter)):
    # return sc_service.get_trend(filter)
    return [
        {"date": "2025-04-21", "cnt": 42, "moving_avg_7d": 42.0, "prev_cnt": None, "change_pct": 0, "cumulative_cnt": 42},
        {"date": "2025-04-22", "cnt": 38, "moving_avg_7d": 40.0, "prev_cnt": 42, "change_pct": -9.52, "cumulative_cnt": 80},
        {"date": "2025-04-23", "cnt": 45, "moving_avg_7d": 41.7, "prev_cnt": 38, "change_pct": 18.42, "cumulative_cnt": 125},
        {"date": "2025-04-24", "cnt": 40, "moving_avg_7d": 41.3, "prev_cnt": 45, "change_pct": -11.11, "cumulative_cnt": 165},
        {"date": "2025-04-25", "cnt": 43, "moving_avg_7d": 41.6, "prev_cnt": 40, "change_pct": 7.50, "cumulative_cnt": 208},
    ]


# ---------------------------------------------------------------
# So sánh cùng kỳ
# ---------------------------------------------------------------
@router.get("/period_comparison")
def get_period_comparison(
    filter: TicketFilter = Depends(build_filter),
    period: str = Query("month", description="month, week, quarter")
):
    # return sc_service.get_period_comparison(filter, period)
    return [
        {"period": "2025-01", "cnt": 120, "prev_period": None, "same_period_last_year": None, "mom_change_pct": None, "yoy_change_pct": None},
        {"period": "2025-02", "cnt": 135, "prev_period": 120, "same_period_last_year": 110, "mom_change_pct": 12.5, "yoy_change_pct": 22.73},
        {"period": "2025-03", "cnt": 110, "prev_period": 135, "same_period_last_year": 105, "mom_change_pct": -18.52, "yoy_change_pct": 4.76},
        {"period": "2025-04", "cnt": 150, "prev_period": 110, "same_period_last_year": 130, "mom_change_pct": 36.36, "yoy_change_pct": 15.38},
    ]


# ---------------------------------------------------------------
# Phân phối thời gian xử lý
# ---------------------------------------------------------------
@router.get("/processing_time_distribution")
def get_processing_time_distribution(filter: TicketFilter = Depends(build_filter)):
    # return sc_service.get_processing_time_distribution(filter)
    return {
        "statistics": {
            "min_val": 5,
            "max_val": 480,
            "median": 38.5,
            "p95": 210.0,
            "avg_time": 52.7,
            "stddev_time": 68.4,
            "total_processed": 1045
        },
        "histogram": [
            {"bucket": 1, "low": 0, "high": 36, "freq": 320},
            {"bucket": 2, "low": 36, "high": 72, "freq": 285},
            {"bucket": 3, "low": 72, "high": 108, "freq": 155},
            {"bucket": 4, "low": 108, "high": 144, "freq": 98},
        ]
    }


# ---------------------------------------------------------------
# Pivot table
# ---------------------------------------------------------------
@router.get("/pivot_device_by_shift")
def get_pivot_device_by_shift(filter: TicketFilter = Depends(build_filter)):
    # return sc_service.get_pivot_device_by_shift(filter)
    return [
        {"device_type": "OPMS", "ca1": 120, "ca2": 95},
        {"device_type": "OLT", "ca1": 85, "ca2": 72},
        {"device_type": "POP", "ca1": 60, "ca2": 48},
    ]


# ---------------------------------------------------------------
# Tương quan
# ---------------------------------------------------------------
@router.get("/correlation")
def get_correlation(filter: TicketFilter = Depends(build_filter)):
    # return sc_service.get_correlation(filter)
    return {
        "corr_actual_suspend": 0.68,
        "corr_actual_creation": -0.22
    }


# ---------------------------------------------------------------
# Top N có xếp hạng
# ---------------------------------------------------------------
@router.get("/top_branches_ranked")
def get_top_branches_ranked(
    filter: TicketFilter = Depends(build_filter),
    limit: int = Query(10, description="Số lượng top")
):
    # return sc_service.get_top_branches_ranked(filter, limit)
    all_branches = [
        {"name": "Khánh Hòa 2", "cnt": 134, "rnk": 1},
        {"name": "Hà Nội 10", "cnt": 128, "rnk": 2},
        {"name": "Hà Nội 11", "cnt": 112, "rnk": 3},
        {"name": "HCM 5", "cnt": 105, "rnk": 4},
        {"name": "Đà Nẵng 3", "cnt": 98, "rnk": 5},
    ]
    return all_branches[:limit]


# ---------------------------------------------------------------
# Oracle Text Search
# ---------------------------------------------------------------
@router.get("/search_incidents")
def search_incidents(
    keyword: str = Query(..., description="Từ khóa tìm kiếm"),
    filter: TicketFilter = Depends(build_filter)
):
    # return sc_service.search_incidents_by_keyword(keyword, filter)
    return [
        {"code": "SC20250401001", "ticket_date": "2025-04-01", "description": f"Kết quả cho '{keyword}': Mất kết nối POP-HN1"},
        {"code": "SC20250402015", "ticket_date": "2025-04-02", "description": f"'{keyword}' xuất hiện trong cảnh báo B2B"},
    ]


# ---------------------------------------------------------------
# Cây sự cố
# ---------------------------------------------------------------
@router.get("/incident_tree")
def get_incident_tree(root_ticket_id: int = Query(...)):
    # return sc_service.get_incident_tree(root_ticket_id)
    return [
        {"code": "SC20250401001", "level": 1, "path": "SC20250401001"},
        {"code": "SC20250401002", "level": 2, "path": "SC20250401001 -> SC20250401002"},
    ]


# ---------------------------------------------------------------
# Pareto
# ---------------------------------------------------------------
@router.get("/pareto_issue_groups")
def get_pareto_issue_groups(filter: TicketFilter = Depends(build_filter)):
    # return sc_service.get_pareto_issue_groups(filter)
    return [
        {"name": "Hệ thống Access", "cnt": 450, "pct": 30.0, "cumulative_cnt": 450, "cumulative_pct": 30.0},
        {"name": "Hệ thống Core IP", "cnt": 300, "pct": 20.0, "cumulative_cnt": 750, "cumulative_pct": 50.0},
        {"name": "Hệ thống Metro Ethernet", "cnt": 200, "pct": 13.3, "cumulative_cnt": 950, "cumulative_pct": 63.3},
    ]


# ---------------------------------------------------------------
# Ca hiện tại vs ca trước
# ---------------------------------------------------------------
@router.get("/current_shift_vs_previous")
def get_current_shift_vs_previous(filter: TicketFilter = Depends(build_filter)):
    # return sc_service.get_current_shift_vs_previous(filter)
    return {
        "current_shift": {"shift": "Ca 2", "cnt": 45},
        "previous_shift": {"shift": "Ca 1", "cnt": 38}
    }


# ---------------------------------------------------------------
# AI/ML Insights (mock)
# ---------------------------------------------------------------
@router.get("/forecast")
def get_forecast(
    filter: TicketFilter = Depends(build_filter),
    days_ahead: int = Query(7, description="Số ngày dự báo")
):
    # return sc_service.get_forecast(filter, days_ahead)
    return {
        "actual": [
            {"day": "2025-04-25", "cnt": 42},
            {"day": "2025-04-26", "cnt": 38},
        ],
        "forecast": [
            {"day": "2025-04-30", "forecast": 41},
            {"day": "2025-05-01", "forecast": 39},
        ]
    }


@router.get("/anomalies")
def get_anomalies(filter: TicketFilter = Depends(build_filter)):
    # return sc_service.get_anomalies(filter)
    return [
        {"code": "SC20250428003", "ticket_date": "2025-04-28", "actual_time": 720, "anomaly_type": "High"},
        {"code": "SC20250429015", "ticket_date": "2025-04-29", "actual_time": 5, "anomaly_type": "Low"},
    ]


@router.get("/clusters")
def get_clusters(filter: TicketFilter = Depends(build_filter)):
    # return sc_service.get_clusters(filter)
    return [
        {"cluster_id": 1, "cnt": 340},
        {"cluster_id": 2, "cnt": 280},
    ]


@router.post("/predicted_priority")
def predicted_priority(description: str = Body(..., embed=True)):
    # return sc_service.get_predicted_priority(description)
    return {"predicted_priority": "3"}