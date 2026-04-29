#!/usr/bin/env python3
"""
Tạo dữ liệu giả cho Oracle, gán ID cứng 1..N, không dùng bind variables.
Tự động disable tất cả CHECK constraints để tránh lỗi.
"""

import argparse
import random
import datetime
import oracledb
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ------------------------------ Dữ liệu DIM (hardcode) ------------------------------
BRANCHES = [(1, 'Khánh Hòa 2', 'KHA2'), (2, 'Hà Nội 10', 'HN10'), (3, 'Hồ Chí Minh 1', 'HCM1'),
            (4, 'Đà Nẵng 5', 'DAN5'), (5, 'Cần Thơ 3', 'CTO3')]
DEVICE_TYPES = [(1, 'OPMS'), (2, 'OLT'), (3, 'POP'), (4, 'Metro'), (5, 'BRAS')]
DEVICE_NAMES = [f'NTGP{i:03d}OPMS' for i in range(1, 21)] + [f'HNIP111{i:02d}GC16' for i in range(1, 11)]
HT_ACTIONS = [(1, 'Xác nhận'), (2, 'START PROCESS'), (3, 'Chuyển queue'), (4, 'Cập nhật thông tin'), (5, 'Tạm dừng')]
CUSTOMER_TYPES = [(1000, 'Hosting'), (1001, 'Voice Doanh Nghiệp'), (1002, 'FTTH'), (1003, 'Leased Line')]
QUEUE_TYPES = [(1, 'Đơn vị TẠO'), (2, 'Đơn vị THỰC HIỆN')]
SERVICE_TYPES = [(1000, 'FTQ - Hỗ trợ quy trình'), (1001, 'DVKH - Nghiệp vụ'), (1002, 'Kỹ thuật hạ tầng')]
HT_STEPS = [(1000, 'Đóng'), (1001, 'Phân công/Nhận xử lý'), (1002, 'Chờ phản hồi'), (1003, 'Xác nhận thực hiện xong')]
SUPPORT_TYPES = [(1000, 'Hỗ trợ nghiệp vụ'), (1001, 'Hỗ trợ kỹ thuật')]
INTERFACE_NAMES = ['XGE1/0/17', 'et-1/1/1', 'GigabitEthernet0/1', 'TenGigE0/0/0/1']
ISSUE_GROUPS = [(1, 'Hệ thống Access'), (2, 'Hệ thống Core IP'), (3, 'Hệ thống truyền dẫn')]
ISSUE_NAMES = [(1, 'Khách hàng mất kết nối', 1), (2, 'POP down', 2), (3, 'OLT bị treo', 1),
               (4, 'BRAS overload', 2), (5, 'Suốt cáp quang', 3)]
LOCATIONS = [(1, '01. Hà Nội'), (2, '15. Tây Nam Bộ'), (3, '04. Hải Phòng'), (4, '07. Đà Nẵng')]
POPS = [(1, 'POP-HN1'), (2, 'POP-HCM1'), (3, 'POP-DN1'), (4, 'POP-CTO1')]
PROCESSING_UNITS = [(1, 'Hạ tầng'), (2, 'Thuê bao'), (3, 'INF'), (4, 'TIN/PNC')]
QUEUES = [(1, 'CSOC-IT'), (2, 'SCC'), (3, 'INF-BTHT'), (4, 'TIN')]
REASONS = [(1, 'Bộ OPMS Cảnh Báo', 'Cảnh báo đóng, mở cửa'),
           (2, 'Mất điện', 'Mất điện cục bộ tại POP'),
           (3, 'Lỗi cấu hình', 'Cấu hình sai trên thiết bị'),
           (4, 'Quá tải', 'Lưu lượng vượt ngưỡng')]
REGIONS = [(1, 'MB'), (2, 'MN')]
STAFFS = [(1, 'Nguyen Minh Quan', 'QuanNM96@fpt.com'),
          (2, 'Le Van Manh', 'ManhLV6@fpt.com'),
          (3, 'Tran Thi Huong', 'HuongTT@fpt.com'),
          (4, 'Pham Van Tuan', 'TuanPV@fpt.com')]

# ------------------------------ Helper ------------------------------
def random_date(start, end):
    delta = end - start
    return start + datetime.timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def random_shift():
    return 'Ca 1' if random.random() < 0.5 else 'Ca 2'

def random_ticket_status():
    return random.choice(['Closed','Inprogress','New','Rejected','Resolved','Pending','Verified'])

def random_priority():
    return random.randint(1, 6)

def random_boolean():
    return 'Có' if random.random() < 0.7 else 'Không'

def generate_ticket_code(ticket_type, index):
    return f"{ticket_type}{index:06d}"

def sql_quote(val):
    """Chuyển giá trị thành chuỗi SQL an toàn."""
    if val is None:
        return 'NULL'
    if isinstance(val, str):
        escaped = val.replace("'", "''")
        return f"'{escaped}'"
    if isinstance(val, datetime.datetime):
        return f"TO_DATE('{val.strftime('%Y-%m-%d %H:%M:%S')}', 'YYYY-MM-DD HH24:MI:SS')"
    if isinstance(val, datetime.date):
        return f"TO_DATE('{val.strftime('%Y-%m-%d')}', 'YYYY-MM-DD')"
    if isinstance(val, bool):
        return '1' if val else '0'
    if isinstance(val, (int, float)):
        return str(val)
    return f"'{str(val)}'"

# ------------------------------ Disable all CHECK constraints ------------------------------
def disable_check_constraints(cursor):
    logger.info("Disabling all CHECK constraints...")
    cursor.execute("""
        SELECT 'ALTER TABLE ' || owner || '.' || table_name || ' DISABLE CONSTRAINT ' || constraint_name
        FROM all_constraints
        WHERE owner = USER AND constraint_type = 'C'
    """)
    rows = cursor.fetchall()
    for row in rows:
        try:
            cursor.execute(row[0])
        except Exception as e:
            logger.warning(f"Failed to disable {row[0]}: {e}")
    cursor.connection.commit()
    logger.info(f"Disabled {len(rows)} CHECK constraints.")

# ------------------------------ Cleanup ------------------------------
def cleanup_data(cursor):
    logger.info("Cleaning old data...")
    tables = [
        "ht_ticket_history", "ticket_pop", "ticket_location", "ticket_interface",
        "ticket_device", "ticket_branch", "fact_ht_tickets", "fact_sc_tickets",
        "fact_tickets", "fact_ticket_process", "fact_ticket_creation",
        "dim_ticket_close", "fact_ticket_time", "dim_ticket_description",
        "dim_branches", "dim_device_types", "dim_devices", "dim_ht_actions",
        "dim_ht_customer_types", "dim_ht_queue_types", "dim_ht_service_types",
        "dim_ht_steps", "dim_ht_support_types", "dim_interfaces", "dim_issue_groups",
        "dim_issue_names", "dim_locations", "dim_pops", "dim_processing_units",
        "dim_queues", "dim_reasons", "dim_regions", "dim_staffs"
    ]
    for tbl in tables:
        try:
            cursor.execute(f"DELETE FROM {tbl}")
        except Exception as e:
            logger.warning(f"Could not delete from {tbl}: {e}")
    cursor.connection.commit()
    logger.info("Cleanup done.")

# ------------------------------ Insert DIM ------------------------------
def insert_dimensions(cursor):
    logger.info("Inserting DIM data...")
    for bid, bname, code in BRANCHES:
        cursor.execute(f"INSERT INTO dim_branches (id, branch_name, code) VALUES ({bid}, {sql_quote(bname)}, {sql_quote(code)})")
    for did, dname in DEVICE_TYPES:
        cursor.execute(f"INSERT INTO dim_device_types (id, name) VALUES ({did}, {sql_quote(dname)})")
    for i, name in enumerate(DEVICE_NAMES, 1):
        cursor.execute(f"INSERT INTO dim_devices (id, name) VALUES ({i}, {sql_quote(name)})")
    for aid, aname in HT_ACTIONS:
        cursor.execute(f"INSERT INTO dim_ht_actions (id, name) VALUES ({aid}, {sql_quote(aname)})")
    for cid, cname in CUSTOMER_TYPES:
        cursor.execute(f"INSERT INTO dim_ht_customer_types (id, name) VALUES ({cid}, {sql_quote(cname)})")
    for qid, qname in QUEUE_TYPES:
        cursor.execute(f"INSERT INTO dim_ht_queue_types (id, name) VALUES ({qid}, {sql_quote(qname)})")
    for sid, sname in SERVICE_TYPES:
        cursor.execute(f"INSERT INTO dim_ht_service_types (id, name) VALUES ({sid}, {sql_quote(sname)})")
    for stid, stname in HT_STEPS:
        cursor.execute(f"INSERT INTO dim_ht_steps (id, name) VALUES ({stid}, {sql_quote(stname)})")
    for suid, suname in SUPPORT_TYPES:
        cursor.execute(f"INSERT INTO dim_ht_support_types (id, name) VALUES ({suid}, {sql_quote(suname)})")
    for i, iname in enumerate(INTERFACE_NAMES, 1):
        cursor.execute(f"INSERT INTO dim_interfaces (id, name) VALUES ({i}, {sql_quote(iname)})")
    for igid, igname in ISSUE_GROUPS:
        cursor.execute(f"INSERT INTO dim_issue_groups (id, name) VALUES ({igid}, {sql_quote(igname)})")
    for inid, inname, ingid in ISSUE_NAMES:
        cursor.execute(f"INSERT INTO dim_issue_names (id, name, issue_group_id) VALUES ({inid}, {sql_quote(inname)}, {ingid})")
    for lid, lname in LOCATIONS:
        cursor.execute(f"INSERT INTO dim_locations (id, name) VALUES ({lid}, {sql_quote(lname)})")
    for pid, pname in POPS:
        cursor.execute(f"INSERT INTO dim_pops (id, name) VALUES ({pid}, {sql_quote(pname)})")
    for puid, puname in PROCESSING_UNITS:
        cursor.execute(f"INSERT INTO dim_processing_units (id, name) VALUES ({puid}, {sql_quote(puname)})")
    for qid, qname in QUEUES:
        cursor.execute(f"INSERT INTO dim_queues (id, name) VALUES ({qid}, {sql_quote(qname)})")
    for rid, rname, rdetail in REASONS:
        cursor.execute(f"INSERT INTO dim_reasons (id, name, detail) VALUES ({rid}, {sql_quote(rname)}, {sql_quote(rdetail)})")
    for regid, regname in REGIONS:
        cursor.execute(f"INSERT INTO dim_regions (id, name) VALUES ({regid}, {sql_quote(regname)})")
    for sid, sname, smail in STAFFS:
        cursor.execute(f"INSERT INTO dim_staffs (id, name, mail) VALUES ({sid}, {sql_quote(sname)}, {sql_quote(smail)})")
    cursor.connection.commit()
    logger.info("DIM inserted.")

# ------------------------------ Tạo FACT (ID cứng) ------------------------------
def generate_fact_data(num_tickets, cursor):
    logger.info(f"Generating {num_tickets} tickets (direct ID assignment)...")

    branch_ids = [1,2,3,4,5]
    device_type_ids = [1,2,3,4,5]
    device_ids = list(range(1, len(DEVICE_NAMES)+1))
    action_ids = [1,2,3,4,5]
    customer_type_ids = [1000,1001,1002,1003]
    queue_type_ids = [1,2]
    service_type_ids = [1000,1001,1002]
    step_ids = [1000,1001,1002,1003]
    support_type_ids = [1000,1001]
    interface_ids = list(range(1, len(INTERFACE_NAMES)+1))
    issue_name_ids = [1,2,3,4,5]
    location_ids = [1,2,3,4]
    pop_ids = [1,2,3,4]
    processing_unit_ids = [1,2,3,4]
    queue_ids = [1,2,3,4]
    reason_ids = [1,2,3,4]
    region_ids = [1,2]
    staff_ids = [1,2,3,4]

    start_ref = datetime.datetime(2024,1,1)
    end_ref   = datetime.datetime(2025,12,31)

    for i in range(1, num_tickets+1):
        is_sc = random.choice([True, False])
        ticket_type = 'SC' if is_sc else 'HT'
        code = generate_ticket_code(ticket_type, i)

        # dim_ticket_description
        first_desc = f"First description for {code}"
        desc = f"Detail description for {code}"
        cursor.execute(f"""
            INSERT INTO dim_ticket_description (id, first_description, description)
            VALUES ({i}, {sql_quote(first_desc)}, {sql_quote(desc)})
        """)
        desc_id = i

        # fact_ticket_time
        issue_date = random_date(start_ref, end_ref)
        inprogress_date = issue_date + datetime.timedelta(minutes=random.randint(5,60))
        resolved_date = inprogress_date + datetime.timedelta(minutes=random.randint(30,300))
        closed_date = resolved_date + datetime.timedelta(minutes=random.randint(0,60))
        estimate_date = issue_date + datetime.timedelta(hours=random.randint(1,8))
        expect_end_date = resolved_date + datetime.timedelta(minutes=random.randint(-30,30))
        required_date = resolved_date + datetime.timedelta(minutes=random.randint(-60,60))
        full_data_date = inprogress_date + datetime.timedelta(minutes=random.randint(10,120))
        cursor.execute(f"""
            INSERT INTO fact_ticket_time (
                id, closed_date, estimate_date, expect_end_date,
                inprogress_date, issue_date, resolved_date, required_date, full_data_date
            ) VALUES (
                {i}, {sql_quote(closed_date)}, {sql_quote(estimate_date)}, {sql_quote(expect_end_date)},
                {sql_quote(inprogress_date)}, {sql_quote(issue_date)}, {sql_quote(resolved_date)},
                {sql_quote(required_date)}, {sql_quote(full_data_date)}
            )
        """)
        time_id = i

        # fact_ticket_creation
        created_datetime = issue_date + datetime.timedelta(minutes=random.randint(0,15))
        sc_creation_method = random.choice(['SC tạo auto', 'SC tạo manual (SC tạo tay)'])
        sc_creation_time = round(random.uniform(0.1,5.0),1)
        created_staff_id = random.choice(staff_ids)
        date_created = created_datetime.date()
        week_created = f"W{date_created.isocalendar()[1]} - {date_created.year}"
        month_created = date_created.strftime("%m/%Y")
        period_created = f"{random.choice(['1H','2H'])} - {date_created.year}"
        year_created = date_created.year
        shift_created = random_shift()
        cursor.execute(f"""
            INSERT INTO fact_ticket_creation (
                id, sc_creation_method, sc_creation_time, created_staff_id,
                created_datetime, "date", "week", "month", "period", "year", "shift"
            ) VALUES (
                {i}, {sql_quote(sc_creation_method)}, {sc_creation_time}, {created_staff_id},
                {sql_quote(created_datetime)}, {sql_quote(date_created)}, {sql_quote(week_created)},
                {sql_quote(month_created)}, {sql_quote(period_created)}, {year_created}, {sql_quote(shift_created)}
            )
        """)
        creation_id = i

        # dim_ticket_close
        closed_shift = random_shift()
        closed_day = resolved_date.date()
        closed_week = f"W{closed_day.isocalendar()[1]} - {closed_day.year}"
        closed_month = closed_day.strftime("%m/%Y")
        closed_year = closed_day.year
        cursor.execute(f"""
            INSERT INTO dim_ticket_close (
                id, closed_shift, closed_day, closed_week, closed_month, closed_year
            ) VALUES (
                {i}, {sql_quote(closed_shift)}, {sql_quote(closed_day)}, {sql_quote(closed_week)},
                {sql_quote(closed_month)}, {closed_year}
            )
        """)
        closed_id = i

        # fact_ticket_process
        process_name = f"Process_{code}"
        process_staff_id = random.choice(staff_ids)
        processing_unit_id = random.choice(processing_unit_ids)
        queue_create_id = random.choice(queue_ids)
        queue_process_id = random.choice(queue_ids)
        change_queue_time = random.randint(5,120)
        actual_time = random.randint(10,300)
        cursor.execute(f"""
            INSERT INTO fact_ticket_process (
                id, process_name, process_staff_id, processing_unit_id,
                queue_create_id, queue_process_id, change_queue_time, actual_time
            ) VALUES (
                {i}, {sql_quote(process_name)}, {process_staff_id}, {processing_unit_id},
                {queue_create_id}, {queue_process_id}, {change_queue_time}, {actual_time}
            )
        """)
        process_id = i

        # fact_tickets
        over_time = random.choice(['Đúng hạn', 'Trễ hạn', 'RESOLVED - Đúng hạn'])
        reason_id = random.choice(reason_ids)
        priority = random_priority()
        ticket_status = random_ticket_status()
        issue_name_id = random.choice(issue_name_ids)
        required_time = random.randint(30,480)
        cursor.execute(f"""
            INSERT INTO fact_tickets (
                id, code, process_id, time_id, creation_id, closed_id,
                over_time, reason_id, priority, ticket_status, issue_name_id, required_time
            ) VALUES (
                {i}, {sql_quote(code)}, {process_id}, {time_id}, {creation_id}, {closed_id},
                {sql_quote(over_time)}, {reason_id}, {priority}, {sql_quote(ticket_status)},
                {issue_name_id}, {required_time}
            )
        """)
        ticket_id = i

        # fact_sc_tickets or fact_ht_tickets
        if is_sc:
            cus_qty = random.randint(0,500) if random.random()<0.5 else 0
            device_type_id = random.choice(device_type_ids)
            suspend_time = random.randint(30,600) if random.random()<0.8 else 0
            sc_khg_status = random_boolean()
            sc_report_status = random_boolean()
            sc_type = random.choice(['Khách quan', 'Chủ quan', ''])
            region_id = random.choice(region_ids)
            sc_inf_explanation_status = random_boolean()
            sc_natural_disaster = random_boolean()
            parent = f"Parent note for {code}"
            cursor.execute(f"""
                INSERT INTO fact_sc_tickets (
                    ticket_id, description_id, cus_qty, device_type_id, suspend_time,
                    sc_khg_status, sc_report_status, sc_type, region_id,
                    sc_inf_explanation_status, sc_natural_disaster, parent
                ) VALUES (
                    {ticket_id}, {desc_id}, {cus_qty}, {device_type_id}, {suspend_time},
                    {sql_quote(sc_khg_status)}, {sql_quote(sc_report_status)}, {sql_quote(sc_type)},
                    {region_id}, {sql_quote(sc_inf_explanation_status)}, {sql_quote(sc_natural_disaster)},
                    {sql_quote(parent)}
                )
            """)
        else:
            title = f"Support ticket {code}"
            commitment_desc = random_boolean()
            required = random_boolean()
            is_ticket_open = random_boolean()
            sos_ticket_flag = random_boolean()
            customer_type_id = random.choice(customer_type_ids)
            service_type_id = random.choice(service_type_ids)
            support_type_id = random.choice(support_type_ids)
            step_id = random.choice(step_ids)
            deadline_status = random.choice(['Đúng hạn', 'Quá hạn'])
            rejection_count = random.randint(0,3)
            response_count = random.randint(1,5)
            sla_violation_count = str(random.randint(0,3)) if random.random()<0.7 else 'Không'
            priority_handling_desc = random_boolean()
            is_escalated = random_boolean()
            scenario_confirmed = random_boolean()
            ticket_age_days = round(random.uniform(0.5,30.0),1)
            cursor.execute(f"""
                INSERT INTO fact_ht_tickets (
                    ticket_id, title, commitment_desc, required, is_ticket_open,
                    sos_ticket_flag, customer_type_id, service_type_id, support_type_id,
                    step_id, deadline_status, rejection_count, response_count,
                    sla_violation_count, priority_handling_desc, is_escalated,
                    scenario_confirmed, ticket_age_days
                ) VALUES (
                    {ticket_id}, {sql_quote(title)}, {sql_quote(commitment_desc)}, {sql_quote(required)},
                    {sql_quote(is_ticket_open)}, {sql_quote(sos_ticket_flag)}, {customer_type_id},
                    {service_type_id}, {support_type_id}, {step_id}, {sql_quote(deadline_status)},
                    {rejection_count}, {response_count}, {sql_quote(sla_violation_count)},
                    {sql_quote(priority_handling_desc)}, {sql_quote(is_escalated)},
                    {sql_quote(scenario_confirmed)}, {ticket_age_days}
                )
            """)

        # Các bảng liên kết (tránh trùng khóa chính)
        # ticket_branch
        chosen_branches = random.sample(branch_ids, k=random.randint(1,3))
        for b in chosen_branches:
            cursor.execute(f"INSERT INTO ticket_branch (ticket_id, branch_id) VALUES ({ticket_id}, {b})")
        # ticket_device
        if random.random() < 0.7:
            chosen_devices = random.sample(device_ids, k=random.randint(1,2))
            for d in chosen_devices:
                cursor.execute(f"INSERT INTO ticket_device (ticket_id, device_id) VALUES ({ticket_id}, {d})")
        # ticket_interface
        if random.random() < 0.7:
            chosen_interfaces = random.sample(interface_ids, k=random.randint(1,2))
            for iface in chosen_interfaces:
                cursor.execute(f"INSERT INTO ticket_interface (ticket_id, interface_id) VALUES ({ticket_id}, {iface})")
        # ticket_location
        chosen_locs = random.sample(location_ids, k=random.randint(1,2))
        for loc in chosen_locs:
            cursor.execute(f"INSERT INTO ticket_location (ticket_id, location_id) VALUES ({ticket_id}, {loc})")
        # ticket_pop
        chosen_pops = random.sample(pop_ids, k=random.randint(1,2))
        for p in chosen_pops:
            cursor.execute(f"INSERT INTO ticket_pop (ticket_id, pop_id) VALUES ({ticket_id}, {p})")

        # ht_ticket_history (chỉ cho HT)
        if not is_sc:
            for j in range(random.randint(2,5)):
                hist_desc = f"History {j+1} for {code}"
                updated_date = inprogress_date + datetime.timedelta(minutes=random.randint(0,60*(j+1)))
                hist_status = random.choice(['New','Inprogress','Resolved','Closed','Rejected','CREATE','Pending'])
                action_id = random.choice(action_ids)
                staff_id = random.choice(staff_ids)
                step_id = random.choice(step_ids)
                queue_type_id = random.choice(queue_type_ids)
                created_date = updated_date - datetime.timedelta(minutes=random.randint(1,30))
                updated_queue_id = random.choice(queue_ids)
                response_time = round(random.uniform(0.5,60.0),2)
                commitment_desc = random_boolean()
                cursor.execute(f"""
                    INSERT INTO ht_ticket_history (
                        description, updated_date, ht_ticket_status, ht_ticket_id,
                        action_id, staff_id, step_id, queue_type_id, created_date,
                        updated_queue_id, response_time_minutes, commitment_description
                    ) VALUES (
                        {sql_quote(hist_desc)}, {sql_quote(updated_date)}, {sql_quote(hist_status)}, {ticket_id},
                        {action_id}, {staff_id}, {step_id}, {queue_type_id}, {sql_quote(created_date)},
                        {updated_queue_id}, {response_time}, {sql_quote(commitment_desc)}
                    )
                """)

        if i % 100 == 0:
            cursor.connection.commit()
            logger.info(f"Committed {i} tickets")

    cursor.connection.commit()
    logger.info(f"Finished {num_tickets} tickets.")

# ------------------------------ Main ------------------------------
def main():
    parser = argparse.ArgumentParser(description="Generate fake data with direct IDs and no CHECK constraints")
    parser.add_argument("--num_tickets", type=int, default=100, help="Number of tickets")
    parser.add_argument("--user", default="system", help="Oracle username")
    parser.add_argument("--password", default="oracle", help="Oracle password")
    parser.add_argument("--dsn", default="localhost:1521/XEPDB1", help="Oracle DSN")
    args = parser.parse_args()

    try:
        connection = oracledb.connect(user=args.user, password=args.password, dsn=args.dsn)
        cursor = connection.cursor()
        logger.info("Connected to Oracle")

        # Xóa dữ liệu cũ
        cleanup_data(cursor)
        # Vô hiệu hóa tất cả CHECK constraints
        disable_check_constraints(cursor)
        # Insert DIM
        insert_dimensions(cursor)
        # Insert FACT
        generate_fact_data(args.num_tickets, cursor)

        cursor.close()
        connection.close()
        logger.info("Done.")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()