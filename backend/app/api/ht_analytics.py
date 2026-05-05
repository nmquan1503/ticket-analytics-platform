from fastapi import APIRouter, Depends, Query
from typing import Optional, List

from app.api.mock_scaler import mock_scale
from app.schemas.analytics import TicketFilter
from app.services.analytics.ht_service import HTAnalyticService

router = APIRouter(prefix="/ht_analytics", tags=["HT Analytics"])

ht_service = HTAnalyticService()


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
@mock_scale
def analytics_root():
    return {"message": "HT Analytics service is running (MOCK DATA)"}


# ---------------------------------------------------------------
# KPI tổng quan
# ---------------------------------------------------------------
@router.get("/kpi")
@mock_scale
def get_kpi(filter: TicketFilter = Depends(build_filter)):
    return ht_service.get_kpi(filter)
    return {
        "total_tickets": 856,
        "open_tickets": 67,
        "closed_tickets": 720,
        "sos_tickets": 12,
        "required_tickets": 45,
        "on_time_rate": 83.5,
        "total_rejections": 134,
        "total_responses": 678,
        "sla_violations": 23,
        "avg_ticket_age_days": 3.4
    }


# ---------------------------------------------------------------
# Trend theo ngày
# ---------------------------------------------------------------
@router.get("/trend")
@mock_scale
def get_trend(filter: TicketFilter = Depends(build_filter)):
    return ht_service.get_trend(filter)
    return [
        {"ticket_date": "2025-04-25", "cnt": 32, "moving_avg_7d": 32.0, "prev_cnt": None, "change_pct": 0, "cumulative_cnt": 32},
        {"ticket_date": "2025-04-26", "cnt": 28, "moving_avg_7d": 30.0, "prev_cnt": 32, "change_pct": -12.5, "cumulative_cnt": 60},
        {"ticket_date": "2025-04-27", "cnt": 35, "moving_avg_7d": 31.7, "prev_cnt": 28, "change_pct": 25.0, "cumulative_cnt": 95},
        {"ticket_date": "2025-04-28", "cnt": 30, "moving_avg_7d": 31.3, "prev_cnt": 35, "change_pct": -14.3, "cumulative_cnt": 125},
        {"ticket_date": "2025-04-29", "cnt": 33, "moving_avg_7d": 31.6, "prev_cnt": 30, "change_pct": 10.0, "cumulative_cnt": 158},
    ]


# ---------------------------------------------------------------
# So sánh cùng kỳ
# ---------------------------------------------------------------
@router.get("/period_comparison")
@mock_scale
def get_period_comparison(
    filter: TicketFilter = Depends(build_filter),
    period: str = Query("month", description="month, week, quarter")
):
    # return ht_service.get_period_comparison(filter, period)
    return [
        {"period": "2025-01", "cnt": 120, "prev_period": None, "same_period_last_year": None, "mom_change_pct": None, "yoy_change_pct": None},
        {"period": "2025-02", "cnt": 135, "prev_period": 120, "same_period_last_year": 110, "mom_change_pct": 12.5, "yoy_change_pct": 22.73},
        {"period": "2025-03", "cnt": 110, "prev_period": 135, "same_period_last_year": 105, "mom_change_pct": -18.52, "yoy_change_pct": 4.76},
        {"period": "2025-04", "cnt": 150, "prev_period": 110, "same_period_last_year": 130, "mom_change_pct": 36.36, "yoy_change_pct": 15.38},
    ]


# ---------------------------------------------------------------
# Phân phối theo bước xử lý
# ---------------------------------------------------------------
@router.get("/step_distribution")
@mock_scale
def get_step_distribution(filter: TicketFilter = Depends(build_filter)):
    # return ht_service.get_step_distribution(filter)
    return [
        {"step_name": "Phân công/Nhận xử lý", "value": 340},
        {"step_name": "Xác nhận thực hiện xong", "value": 250},
        {"step_name": "Đóng", "value": 180},
        {"step_name": "Đang xử lý", "value": 86},
    ]


# ---------------------------------------------------------------
# Phân phối theo deadline_status
# ---------------------------------------------------------------
@router.get("/deadline_distribution")
@mock_scale
def get_deadline_distribution(filter: TicketFilter = Depends(build_filter)):
    # return ht_service.get_deadline_distribution(filter)
    return [
        {"name": "Đúng hạn", "value": 600},
        {"name": "Quá hạn", "value": 120},
        {"name": "Chưa đến hạn", "value": 136},
    ]


# ---------------------------------------------------------------
# Top queue xử lý
# ---------------------------------------------------------------
@router.get("/top_processing_queues")
@mock_scale
def get_top_processing_queues(
    filter: TicketFilter = Depends(build_filter),
    limit: int = Query(10, description="Số lượng top")
):
    # return ht_service.get_top_processing_queues(filter, limit)
    return [
        {"queue_name": "CSOC-IT", "cnt": 120},
        {"queue_name": "INF-BTHT", "cnt": 95},
        {"queue_name": "SCC", "cnt": 78},
        {"queue_name": "TIN/PNC", "cnt": 65},
        {"queue_name": "BTHT", "cnt": 50},
    ][:limit]


# ---------------------------------------------------------------
# Phân tích thời gian phản hồi (histogram)
# ---------------------------------------------------------------
@router.get("/response_time_analysis")
@mock_scale
def get_response_time_analysis(filter: TicketFilter = Depends(build_filter)):
    # return ht_service.get_response_time_analysis(filter)
    return {
        "statistics": {
            "avg_response": 22.5,
            "median_response": 16.0,
            "p95": 72.0
        },
        "histogram": [
            {"bucket": 1, "low": 0, "high": 12, "freq": 180},
            {"bucket": 2, "low": 12, "high": 24, "freq": 140},
            {"bucket": 3, "low": 24, "high": 36, "freq": 95},
            {"bucket": 4, "low": 36, "high": 48, "freq": 60},
            {"bucket": 5, "low": 48, "high": 60, "freq": 30},
            {"bucket": 6, "low": 60, "high": 72, "freq": 15},
            {"bucket": 7, "low": 72, "high": 84, "freq": 10},
            {"bucket": 8, "low": 84, "high": 96, "freq": 5},
            {"bucket": 9, "low": 96, "high": 108, "freq": 3},
            {"bucket": 10, "low": 108, "high": 120, "freq": 2},
        ]
    }


# ---------------------------------------------------------------
# Pivot SLA theo loại dịch vụ
# ---------------------------------------------------------------
@router.get("/sla_by_service_pivot")
@mock_scale
def get_sla_by_service_pivot(filter: TicketFilter = Depends(build_filter)):
    # return ht_service.get_sla_by_service_pivot(filter)
    return [
        {"service_type": "FTQ - Hỗ trợ quy trình", "on_time": 180, "overdue": 20},
        {"service_type": "DVKH - Nghiệp vụ", "on_time": 160, "overdue": 20},
        {"service_type": "Hosting", "on_time": 130, "overdue": 20},
        {"service_type": "Voice Doanh Nghiệp", "on_time": 110, "overdue": 10},
    ]


# ---------------------------------------------------------------
# Tương quan tuổi thọ ticket và số lần từ chối
# ---------------------------------------------------------------
@router.get("/correlation_age_rejection")
@mock_scale
def get_correlation_age_rejection(filter: TicketFilter = Depends(build_filter)):
    # return ht_service.get_correlation_age_rejection(filter)
    return {
        "corr_age_rejection": 0.52
    }
