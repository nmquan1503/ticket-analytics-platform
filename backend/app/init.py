#!/usr/bin/env python3
"""
Tạo dữ liệu giả cho Oracle (chỉ bảng nghiệp vụ).
Bỏ qua các bảng hỗ trợ chatbot: keywords, examples, chat_history, sessions.
Tự động disable CHECK constraints để tránh lỗi, gán ID cứng 1..N.
"""

import argparse
import random
import datetime
import oracledb
import logging
import sys
from app.services.chat.bot  import get_embedding

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ------------------------------ Dữ liệu DIM (hardcode) ------------------------------
BRANCHES = [
    (1, 'Khánh Hòa 2', 'KHA2'),
    (2, 'Hà Nội 11', 'HN11'),
    (3, 'Thái Nguyên', 'TNN'),
    (4, 'Tuyên Quang', 'TQG'),
    (5, 'Hải Phòng 3', 'HPG3'),
    (6, 'Huế', 'HUE'),
    (7, 'Khánh Hòa 1', 'KHA1'),
    (8, 'Gia Lai', 'GLI'),
    (9, 'Bình Thuận', 'BTN'),
    (10, 'Hà Nội 9', 'HN9'),
    (11, 'Hưng Yên', 'HYN'),
    (12, 'Bình Dương 2', 'BDG2'),
    (13, 'Hà Nội 3', 'HN3'),
    (14, 'Hải Phòng 2', 'HPG2'),
    (15, 'Hà Nội 13', 'HN13'),
    (16, 'Bình Dương 1', 'BDG1'),
    (17, 'Bắc Ninh', 'BNH'),
    (18, 'Điện Biên', 'DBN'),
    (19, 'Thái Bình', 'TBH'),
    (20, 'An Giang', 'AGG'),
    (21, 'Tây Ninh', 'TNH'),
    (22, 'Hà Nội 4', 'HN4'),
    (23, 'Sài Gòn 2', 'SG2'),
    (24, 'Hà Nội 8', 'HN8'),
    (25, 'Quảng Trị', 'QTI'),
    (26, 'Vũng Tàu', 'VTU'),
    (27, 'Hà Nội 10', 'HN10'),
    (28, 'Hải Phòng 1', 'HPG1'),
    (29, 'Tiền Giang', 'TGG'),
    (30, 'Tất cả CN', 'ALL'),
    (31, 'Long An', 'LAN'),
    (32, 'Hải Dương', 'HDG'),
    (33, 'Hậu Giang', 'HGG'),
    (34, 'Nghệ An', 'NAN'),
    (35, 'Phú Yên', 'PYN'),
    (36, 'Đồng Tháp', 'DTP'),
    (37, 'Quảng Ninh 1', 'QNH1'),
    (38, 'Bình Định', 'BDH'),
    (39, 'Thanh Hóa', 'THA'),
    (40, 'Hà Tĩnh', 'HTH'),
    (41, 'Sài Gòn 1', 'SG1'),
    (42, 'Cần Thơ', 'CTO'),
    (43, 'Phú Thọ', 'PTO'),
    (44, 'Đà Nẵng 2', 'DNG2'),
    (45, 'Quảng Ninh 2', 'QNH2'),
    (46, 'Hà Nội 7', 'HN7'),
    (47, 'Lâm Đồng', 'LDG'),
    (48, 'Hà Nam', 'HNM'),
    (49, 'Sài Gòn 10', 'SG10'),
    (50, 'Hà Nội 2', 'HN2'),
    (51, 'Sài Gòn 4', 'SG4'),
    (52, 'Nam Định', 'NDH'),
    (53, 'Hà Nội 12', 'HN12'),
    (54, 'Ninh Bình', 'NBH'),
    (55, 'Germany-Interxion FRA13', 'FRA13'),
    (56, 'Vĩnh Phúc', 'VPC'),
    (57, 'Bắc Giang', 'BGG'),
    (58, 'Quảng Nam', 'QNM'),
    (59, 'Đồng Nai 1', 'DNI1'),
    (60, 'Đà Nẵng 1', 'DNG1'),
    (61, 'Hong Kong-Equinix', 'HKG'),
    (62, 'Đắk Lắk', 'DLK'),
    (63, 'Sài Gòn 3', 'SG3'),
    (64, 'Lào Cai', 'LCI'),
    (65, 'Lạng Sơn', 'LSN'),
    (66, 'Vĩnh Long', 'VLG'),
    (67, 'Ninh Thuận', 'NTN'),
    (68, 'Quảng Ninh 3', 'QNH3'),
    (69, 'Hà Nội 6', 'HN6'),
    (70, 'Sài Gòn 16', 'SG16'),
    (71, 'Kiên Giang', 'KGG'),
    (72, 'Sài Gòn 13', 'SG13'),
    (73, 'Sài Gòn 11', 'SG11'),
    (74, 'Japan-Equinix', 'JPN'),
    (75, 'Hà Nội 1', 'HN1'),
    (76, 'Đồng Nai 2', 'DNI2'),
    (77, 'Hà Nội 5', 'HN5'),
    (78, 'Quảng Ngãi', 'QNI'),
    (79, 'Hà Nội 14', 'HN14'),
    (80, 'Sóc Trăng', 'STG'),
    (81, 'CoreSite', 'CORE'),
    (82, 'Bến Tre', 'BTE'),
    (83, 'Sài Gòn 7', 'SG7'),
    (84, 'Bạc Liêu', 'BLU'),
    (85, 'Quảng Bình', 'QBH'),
    (86, 'Đồng Nai 3', 'DNI3'),
    (87, 'Trà Vinh', 'TVH'),
    (88, 'Bình Phước', 'BPC'),
    (89, 'Sài Gòn 9', 'SG9'),
    (90, 'Vũng Tàu 2', 'VTU2'),
    (91, 'Vũng Tàu 3', 'VTU3'),
    (92, 'Sơn La', 'SLA'),
    (93, 'Yên Bái', 'YBI'),
    (94, 'Đồng Nai 4', 'DNI4'),
    (95, 'Sài Gòn 12', 'SG12'),
    (96, 'Sài Gòn 6', 'SG6'),
    (97, 'Singapore-Equinix', 'SGP'),
    (98, 'Cà Mau', 'CMU'),
    (99, 'Hòa Bình', 'HBH'),
    (100, 'Kon Tum', 'KTM'),
    (101, 'Hà Giang', 'HAG'),
    (102, 'Sài Gòn 8', 'SG8'),
    (103, 'Sài Gòn 5', 'SG5'),
    (104, 'Cao Bằng', 'CBG'),
    (105, 'Đắk Nông', 'DKG'),
    (106, 'Sài Gòn 14', 'SG14'),
    (107, 'Sài Gòn 7 (phụ)', 'SG7B'),
    (108, 'Sài Gòn 6 (phụ)', 'SG6B'),
    (109, 'Hải Phòng', 'HPG'),
    (110, 'MegaI', 'MEGA'),
    (111, 'Đà Nẵng', 'DNG'),
    (112, 'Quảng Ninh', 'QNH')
]
DEVICE_TYPES = [
    (1, 'OPMS'),
    (2, 'Switch Root'),
    (3, 'Cáp thuê bao'),
    (4, 'Tập điểm'),
    (5, 'IPMS'),
    (6, 'Nguồn'),
    (7, 'Metro Core Router'),
    (8, 'IPMSGS1'),
    (9, 'Port PON'),
    (10, 'Cable Metro DWDM'),
    (11, 'Switch FTTH'),
    (12, 'Tủ Cáp'),
    (13, 'OLT'),
    (14, 'Core Internet Gateway'),
    (15, 'DWDM Cisco'),
    (16, 'UPE'),
    (17, 'POP'),
    (18, 'Metro BroadBand BRAS'),
    (19, 'Metro BroadBand Router Edge'),
    (20, 'Hệ thống Call Center Mới'),
    (21, 'Metro Aggregate Switch'),
    (22, 'Mạch D'),
    (23, 'Core Aggregate Switch'),
    (24, 'Thiết bị monitor Inspector'),
    (25, 'IPMSGS3.1'),
    (26, 'Server-iMonitor'),
    (27, 'DWDM CIENA'),
    (28, 'Đông Bắc Bộ'),
    (29, 'Local Gateway Router'),
    (30, 'AGG Switch'),
    (31, 'Switch 10G'),
    (32, 'Management Switch'),
    (33, 'Server Thomson Software'),
    (34, 'Hệ thống Backend'),
    (35, 'SWITCH IPTV'),
    (36, 'Hệ thống Core Tổng Đài'),
    (37, 'Core CGNAT Router'),
    (38, 'Sandvine'),
    (39, 'ServerK8S'),
    (40, 'Kênh Truyền Hình'),
    (41, 'Encoder'),
    (42, 'PayTV Gateway Router'),
    (43, 'Hệ thống Gateway Cisco 3845'),
    (44, 'SOP System'),
    (45, 'Khách hàng Data Center'),
    (46, 'IPMSGS3.3'),
    (47, 'Mạch A'),
    (48, 'Hosting Access Switch'),
    (49, 'OOB - Out of Band'),
    (50, 'LiveTV'),
    (51, 'Mạch C'),
    (52, 'Windows-Service'),
    (53, 'Route Reflector'),
    (54, 'Enterprise Gateway Router'),
    (55, 'Mạch B'),
    (56, 'STORAGE-VOD'),
    (57, 'Windows-WEB-APP'),
    (58, 'Internal Aggregate Switch'),
    (59, 'Camera'),
    (60, 'Hệ thống ISC - TICKET'),
    (61, 'Vùng 7'),
    (62, 'CSOC Gateway Router'),
    (63, 'AD'),
    (64, 'Management-Proxy'),
    (65, 'SW giám sát'),
    (66, 'FPAY-ZABBIX-CONNECTION'),
    (67, 'Core Aggregate Router'),
    (68, 'BDA Aggreate Switch'),
    (69, 'Vùng 6'),
    (70, 'Unidentified'),
    (71, 'Hệ thống Tổng Đài báo hiệu SS7'),
    (72, 'Proxy'),
    (73, 'TSTV service'),
    (74, 'Tây Bắc Bộ'),
    (75, 'SO'),
    (76, 'Cloud'),
    (77, 'Server Storage'),
    (78, 'Hệ thống VAS-Platform'),
    (79, 'KÊNH BACKBONE'),
    (80, 'Hosting Aggregate Switch'),
    (81, 'Agent Map'),
    (82, 'Hosting Gateway'),
    (83, 'Công cụ giám sát (OPSview)'),
    (84, 'Máy Lạnh Chính Xác'),
    (85, 'FOXPAY Gateway Router'),
    (86, 'F-monitor'),
    (87, 'iVoice Aggregate Switch'),
    (88, 'iVoice Gateway Router'),
    (89, 'Core Domestic Gateway'),
    (90, 'API'),
    (91, 'Dịch vụ CSOC'),
    (92, 'Elasticsearch'),
    (93, 'Auto Ticket'),
    (94, 'Máy lạnh'),
    (95, 'Database'),
    (96, 'Notification'),
    (97, 'SRX Omni Channel'),
    (98, 'Firewall'),
    (99, 'CSOC Aggregate Switch'),
    (100, 'LINUX-MYSQL-DB'),
    (101, 'REDIS'),
    (102, 'DATABASE'),
    (103, 'Probe FPL SLA'),
    (104, 'Hệ thống Frontend'),
    (105, 'Server Control'),
    (106, 'Dịch vụ Khách hàng'),
    (107, 'Kênh Truyền Hình HD'),
    (108, 'ISC-ESXI'),
    (109, 'EM System'),
    (110, 'PrivacyIDEA'),
    (111, 'Application'),
    (112, 'IM'),
    (113, 'EM'),
    (114, 'Switch Local IT'),
    (115, 'Autocall'),
    (116, 'SSO-CNDL Node Exporter'),
    (117, 'AIOps'),
    (118, 'Lỗi hệ thống Database'),
    (119, 'Squid Proxy'),
    (120, 'CDN LIVE'),
    (121, 'MQTT'),
    (122, 'CDN TSTV'),
    (123, 'PROXY API'),
    (124, 'LOGS'),
    (125, 'DNS-ProxyXM'),
    (126, 'Customer'),
    (127, 'Databases'),
    (128, 'Motion'),
    (129, 'STORAGE-CEPH-RAW'),
    (130, 'NVR'),
    (131, 'CDN VOD'),
    (132, 'WOWZA-EDGE'),
    (133, 'Management'),
    (134, 'FPL-Box IPTV'),
    (135, 'CDN-BROADPEAK'),
    (136, 'FPL-ANDROID'),
    (137, 'FPL-Website'),
    (138, 'WOWZA-ORIGIN'),
    (139, 'RAWX - S3'),
    (140, 'Server API FBOX'),
    (141, 'LINUX-REVERSE-PROXY'),
    (142, 'Management Software'),
    (143, 'Service'),
    (144, 'MongoDB'),
    (145, 'Hệ thống Session Border Controller (SBC)'),
    (146, 'Tuyến trực MobiFone'),
    (147, 'Hệ thống RIBBON'),
    (148, 'Enterprise Aggregate Switch'),
    (149, 'K8S'),
    (150, 'HPCN System'),
    (151, 'Auto Call'),
    (152, 'Hadoop'),
    (153, 'ML'),
    (154, 'Octopus'),
    (155, 'Redis'),
    (156, 'Clickhouse'),
    (157, 'Log'),
    (158, 'DSLAM'),
    (159, 'Công cụ giám sát (Cacti)'),
    (160, 'FPL-SmartTV - HTML'),
    (161, 'VasPlatform'),
    (162, 'Queue'),
    (163, 'DIS Switch'),
    (164, 'BOX IPTV'),
    (165, 'Trực Bắc-Nam'),
    (166, 'Internal Tool'),
    (167, 'Kafka software'),
    (168, 'Nguồn DC'),
    (169, 'ServerVPN'),
    (170, 'LINUX-HA-PROXY'),
    (171, 'FOXPAY Aggregate Switch'),
    (172, 'Local Aggregate Switch'),
    (173, 'Windows-MSSQL-DB'),
    (174, 'Probe FTI SLA'),
    (175, 'DB Core'),
    (176, 'FIM'),
    (177, 'Bastion'),
    (178, 'Server-RACA'),
    (179, 'Rancher'),
    (180, 'IDC-HNI-02'),
    (181, 'Omni Agent'),
    (182, 'LAB'),
    (183, 'K8S-APPLICATION'),
    (184, 'Card'),
    (185, 'K8S node'),
    (186, 'SmartTV HTML'),
    (187, 'Kênh Truyền Hình SD'),
    (188, 'Máy phát điện'),
    (189, 'Customer Software'),
    (190, 'K8S-SERVICE-PAYMENT'),
    (191, 'K8S-SERVICE-CONNECTOR-PARTNER'),
    (192, 'Storage'),
    (193, 'Thiết bị khuếch đại autolambda'),
    (194, 'SDH Huawei'),
    (195, 'HPCN system'),
    (196, 'ACCU'),
    (197, 'Kênh thuê riêng'),
    (198, 'ServerWowzaEdge'),
    (199, 'VPN'),
    (200, 'Splunk'),
    (201, 'Core Central BRAS'),
    (202, 'Radius'),
    (203, 'HA gateway'),
    (204, 'RING'),
    (205, 'Server'),
    (206, 'Quạt hút DC'),
    (207, 'Hệ thống dịch vụ'),
    (208, 'Core Service'),
    (209, 'LINUX-KAFKA'),
    (210, 'FCAM Gateway Router'),
    (211, 'PAYMENT'),
    (212, 'PCIDSS'),
    (213, 'ServerCDN'),
    (214, 'BDA Gateway Router'),
    (215, 'DWDM Huawei'),
    (216, 'Banks Service'),
    (217, 'Vùng 4'),
    (218, 'Nguồn AC'),
    (219, 'Lỗi hệ thống Errorsystemchecklist'),
    (220, 'Phân tích cuộc gọi'),
    (221, 'MPMS'),
    (222, 'STORAGE-ECS'),
    (223, 'CM'),
    (224, 'Khách hàng IP LeaseLine'),
    (225, 'DB'),
    (226, 'LINUX-CACHE'),
    (227, 'LINUX-KUBERNETES'),
    (228, 'K8S master'),
    (229, 'Liên tỉnh phía Bắc (khác)'),
    (230, 'SDH Cisco'),
    (231, 'Quốc tế'),
    (232, 'Hardware'),
    (233, 'CLOUD-VOIP system'),
    (234, 'SmartCPE Service'),
    (235, 'Fprotect DNS Service'),
    (236, 'BIGDATA'),
    (237, 'SFTP'),
    (238, 'F-Monitor Service'),
    (239, 'CDN IMAGE'),
    (240, 'VMWare'),
    (241, 'FPL-HE-VERIMATRIX'),
    (242, 'K8S-CASHIN-CASHOUT'),
    (243, 'Server-iSurvey'),
    (244, 'ATS'),
    (245, 'Windows-RADIUS-HCM'),
    (246, 'Server Cache VOD'),
    (247, 'IWARFARE'),
    (248, 'KEEP'),
    (249, 'Service Monitoring'),
    (250, 'Rust Desk'),
    (251, 'LINUX-CORE-DNS'),
    (252, 'PayTV Aggregate Switch'),
    (253, 'Mailbox'),
    (254, 'MTA'),
    (255, 'Công cụ giám sát (NMS)'),
    (256, 'Reverse Proxy'),
    (257, 'Tủ cắt lọc sét'),
    (258, 'TRANSCODE'),
    (259, 'PAYTV-API'),
    (260, 'Tools'),
    (261, 'STORAGE-TSTV'),
    (262, 'Kong')
]
DEVICE_NAMES = [f'NTGP{i:03d}OPMS' for i in range(1, 21)] + [f'HNIP111{i:02d}GC16' for i in range(1, 11)]
HT_ACTIONS = [
    (1, 'Tạm dừng, chờ thông tin'),
    (2, 'Xác nhận'),
    (3, 'Nhận xử lý'),
    (4, 'START PROCESS'),
    (5, 'Tiếp tục xử lý ticket'),
    (6, 'Đóng ticket'),
    (7, 'Chuyển nhân sự khác'),
    (8, 'Không xác nhận'),
    (9, 'Phân công'),
    (10, 'Phân tích yêu cầu'),
    (11, 'Nhận ticket từ mail'),
    (12, 'Hủy'),
    (13, 'Từ chối hỗ trợ'),
    (14, 'Chuyển đơn vị khác'),
    (15, 'Cập nhật quá trình'),
    (16, 'Đợi NV xử lý'),
    (17, 'Xác nhận (AUTO)'),
    (18, 'Cập nhật ghi chú Ticket'),
    (19, 'Gộp ticket'),
    (20, 'Escalate HT')
]
CUSTOMER_TYPES = [
    (1, 'Hosting'),
    (2, 'IDC-VH'),
    (3, 'IP Directs'),
    (4, 'Rack'),
    (5, 'Yêu cầu hướng dẫn quy trình'),
    (6, 'Voice Doanh Nghiệp'),
    (7, 'Khách hàng thuê bao'),
    (8, 'Khách hàng độc lập'),
    (9, 'Nghiệp vụ SR'),
    (10, 'Nghiệp vụ công nợ'),
    (11, 'Hỗ trợ nghiệp vụ CSKH'),
    (12, 'VPLS'),
    (13, 'Chuyển khoản'),
    (14, 'FPT Play Event'),
    (15, 'IPLC'),
    (16, 'Đối tác thu hộ'),
    (17, 'FLI-KH'),
    (18, 'ADSL/FTTH/PON'),
    (19, 'IBB'),
    (20, 'ALL'),
    (21, 'Quầy'),
    (22, 'DWDM'),
    (23, 'TIN PNC'),
    (24, 'Tiền mặt'),
    (25, 'Server Colo'),
    (26, 'L3VPN'),
    (27, 'Khách hàng nội bộ'),
    (28, 'NOC-Datacenter'),
    (29, 'L2VPN'),
    (30, 'FLI-SYS'),
    (31, 'PQA-Chức năng'),
    (32, 'Giám sát'),
    (33, 'Kế hoạch hạ tầng Core-IP'),
    (34, 'Kế hoạch hạ tầng access'),
    (35, 'FTI-Data Center HT'),
    (36, 'Hỗ trợ NOC'),
    (37, 'Hệ thống ISC - TICKET'),
    (38, 'Services'),
    (39, 'Ra vào Data Center'),
    (40, 'Hỗ trợ FPTPLAY'),
    (41, 'Kinh doanh'),
    (42, 'Other'),
    (43, 'FLI - KD'),
    (44, 'SCC-VoIP'),
    (45, 'Thuê sợi quang trắng'),
    (46, 'PQA-Người dùng'),
    (47, 'Database'),
    (48, 'Autoticket'),
    (49, 'Giám sát F-mon'),
    (50, 'Công Nghệ Thông Tin'),
    (51, 'CUS'),
    (52, 'CDN'),
    (53, 'Hỗ trợ CSOC'),
    (54, 'Hỗ trợ NOC-NET'),
    (55, 'CS CUS'),
    (56, 'Ticket liên phòng ban'),
    (57, '1.2. Mạng nội bộ/internet'),
    (58, 'Admin'),
    (59, 'Mail'),
    (60, 'Khác'),
    (61, '7.1. Dịch vụ IT khác'),
    (62, 'ISC - Hệ thống Telesales'),
    (63, 'AOPT'),
    (64, 'IDC-HTMN'),
    (65, 'API Queue'),
    (66, 'Kế hoạch hạ tầng CSOC'),
    (67, 'NOC-NET'),
    (68, 'Mô hình triển khai mới'),
    (69, 'QA CN'),
    (70, 'TIN'),
    (71, 'Hỗ trợ INF'),
    (72, 'INF'),
    (73, 'FPTplay-Datacenter'),
    (74, 'Vận hành'),
    (75, 'PQA-Chính sách'),
    (76, 'Nội Bộ'),
    (77, 'Sản phẩm F-Safe/F-Safe Go'),
    (78, 'Hệ thống ISC - MOBIX'),
    (79, 'IDC-KH'),
    (80, 'Thắc mắc điểm, hạng'),
    (81, 'SDH/OTN'),
    (82, 'Ghi âm Call Center'),
    (83, 'DevOps'),
    (84, 'API Customer'),
    (85, 'PQA-Quy trình chưa phù hợp'),
    (86, 'TLS'),
    (87, 'PQA-Bug'),
    (88, 'Thắc mắc quà tặng'),
    (89, 'FTI Voice'),
    (90, 'DDOS'),
    (91, 'Pay FPT - Napas'),
    (92, '4.1. Voice IP'),
    (93, 'FTI doanh nghiệp'),
    (94, 'Opsview và Cacti'),
    (95, 'SR Khôi phục dịch vụ'),
    (96, 'Quản lý hợp đồng'),
    (97, 'Thông tin chung  - Bảo Trì'),
    (98, 'Server Delicate'),
    (99, 'Thu hồi'),
    (100, 'EInvoice'),
    (101, 'Econtract'),
    (102, 'DEMO TICKET HT'),
    (103, 'Fshare- Datacenter'),
    (104, 'SaleClub'),
    (105, 'SR Chuyển địa điểm cùng tỉnh'),
    (106, 'Tập điểm HOT'),
    (107, 'Hỗ trợ đơn vị khác'),
    (108, 'SR Thanh lý tạm ngừng'),
    (109, 'Camera'),
    (110, 'Hỗ trợ NOC-KTM'),
    (111, 'Kiểm tra QOS'),
    (112, 'Quản lý nhân viên DVKH'),
    (113, 'FPT Play'),
    (114, 'Quy trình/Chính sách'),
    (115, 'Hỗ trợ NOC-TKVH'),
    (116, 'Thu hồ mPOS'),
    (117, 'Voice Cá Nhân'),
    (118, 'Voice PSTN'),
    (119, 'Lỗi nghiệp vụ'),
    (120, 'Chính sách CSKH-Quy trình'),
    (121, 'Member - Napas'),
    (122, 'Thắc mắc tham gia'),
    (123, 'Qr Pay'),
    (124, 'Hi FPT - Napas'),
    (125, 'Quản lý kế toán'),
    (126, 'IPTV'),
    (127, 'VoiP'),
    (128, 'Triển Khai'),
    (129, 'Xử lý lỗi'),
    (130, 'Bảo Trì'),
    (131, 'FShare'),
    (132, 'Voice Quốc Tế'),
    (133, 'SaleClub/Bán mới'),
    (134, 'Hệ thống tính lương hoa hồng DVKH'),
    (135, 'SR thay đổi thông tin KH'),
    (136, 'Ticket'),
    (137, 'FPT Smart Home'),
    (138, 'Tổng Đài Call Center'),
    (139, 'SaleClub/Bán thêm'),
    (140, 'HiFPT - Napas'),
    (141, 'Phân quyền'),
    (142, '1.1. Văn phòng mới/Chuyển văn phòng'),
    (143, 'CallCenter Agent'),
    (144, 'Hỗ trợ IDC'),
    (145, 'Prefix MAC'),
    (146, 'Vật tư TINPNC/ Vật tư quầy'),
    (147, 'Tạo checklist'),
    (148, 'Call Center'),
    (149, 'Vật tư'),
    (150, 'SR Hỗ trợ kỹ thuật'),
    (151, 'CustomerRequest'),
    (152, 'Hệ thống tính lương thu ngân'),
    (153, 'Thông tin chung  - Bảo Trì - Xem báo cáo'),
    (154, 'EvoucherFoxGold'),
    (155, 'Hỗ trợ kỹ thuật/Báo cáo'),
    (156, 'SR Chuyển dịch vụ'),
    (157, 'ISC - OSU4 - P. Hỗ trợ vận hành số 4'),
    (158, 'Phân công'),
    (159, 'Thông tin chung  - Phiếu Triển Khai'),
    (160, 'Thông tin chung  - Triển Khai'),
    (161, 'Giao dịch thiết bị'),
    (162, 'Bàn giao vật tư'),
    (163, 'Domain'),
    (164, 'Mobipay'),
    (165, 'Radius_Hỗ trợ'),
    (166, 'Quản lý block/Chuyên trách hợp đồng'),
    (167, 'Monitor'),
    (168, 'Infratructure'),
    (169, 'Inside'),
    (170, 'Báo cáo chất lượng dịch vụ'),
    (171, 'SR trả trước dịch vụ'),
    (172, 'Thông tin chung/Tần giám sát'),
    (173, 'Bảo trì'),
    (174, 'Kiểm tra logs Radius'),
    (175, 'Radius_Phân quyền'),
    (176, 'IAM account'),
    (177, 'Storage'),
    (178, 'Quản lý block/Xem DS tập điểm'),
    (179, 'Quản lý hợp đồng/DS&LLine/Cước Sử dụng'),
    (180, 'ISC-Datacenter'),
    (181, 'SR Giải đáp hướng dẫn thắc mắc'),
    (182, 'Lỗi hệ thống'),
    (183, 'Phân công/Hạn/Năng lực hạn'),
    (184, 'Message Queue'),
    (185, 'Kiểm tra service API Radius'),
    (186, 'Core IP'),
    (187, 'Hỗ trợ Nội bộ ( NOC)'),
    (188, 'Multisite platform'),
    (189, 'Hệ thống ISC - Omni Agent'),
    (190, 'Đăng nhập IAM/Azure AD/ Quản mật khẩu/ OTP/ Get Token'),
    (191, 'Thông tin chung / Không thể đăng nhập vào SR'),
    (192, '2.2. Hỗ trợ phần mềm'),
    (193, 'Thông tin chung / Không có nút cập nhật'),
    (194, 'SR Khiếu nại phân nàn'),
    (195, 'Thiết bị/Vật tư/Tài sản'),
    (196, 'Tự động xử lý sự cố'),
    (197, 'CGNAT, vCGNAT'),
    (198, 'Thiết bị Juniper IP'),
    (199, 'Automation'),
    (200, 'Omnisell'),
    (201, 'BusinessEvoucher'),
    (202, 'PON'),
    (203, 'Xuất báo cáo'),
    (204, 'Data IP'),
    (205, 'Công cụ'),
    (206, 'BB1, BB3, Bắc Nam'),
    (207, 'Hỗ trợ NOC-OTS'),
    (208, 'BRAS toàn quốc'),
    (209, 'Mạng Truyền dẫn Quốc tế, BB2'),
    (210, 'SMC/MC'),
    (211, 'Báo cáo QLCLDV'),
    (212, 'Cập nhật nhân sự')
]
QUEUE_TYPES = [
    (1, 'Đơn vị THỰC HIỆN'),
    (2, 'Đơn vị TẠO'),
    (3, 'BOT')
]
SERVICE_TYPES = [
    (1, '4. FTI Hosting'),
    (2, 'IDC-VH'),
    (3, '3. FTI LeaseLine/ MPLS/ IPLC/ IEPL'),
    (4, 'FTQ - Hỗ trợ quy trình'),
    (5, '5. FTI Voice'),
    (6, 'FPT Play'),
    (7, 'DVKH - Nghiệp vụ'),
    (8, 'DVKH - Hỗ trợ TTOL'),
    (9, 'FPT Play Event'),
    (10, 'FLI-HTKT'),
    (11, 'Broadband'),
    (12, 'FTQ - Xác minh thông tin'),
    (13, 'Hỗ trợ thực hiện kế hoạch'),
    (14, 'FLI-SYSTEM'),
    (15, 'Hỗ trợ Hi FPT'),
    (16, 'IDC - Hỗ trợ DataCenter'),
    (17, 'FTQ-Hỗ trợ QTDVKH'),
    (18, 'SCC-Hệ thống công cụ'),
    (19, 'FTI DataCenter'),
    (20, 'INF hỗ trợ NOC'),
    (21, 'Hệ thống ISC - TICKET'),
    (22, 'Hệ thống ISC - SYS'),
    (23, 'IDC-Hỗ trợ ra vào Data Center'),
    (24, 'Request NOC-NET hỗ trợ'),
    (25, 'FLI - HTKD'),
    (26, 'SCC-Voice'),
    (27, 'FTQ-Hỗ trợ QTKD'),
    (28, 'FTQ-Hỗ trợ QTTIN/PNC'),
    (29, 'Hệ thống ISC - DBA'),
    (30, 'Hệ thống ISC - SR (Service Request)'),
    (31, 'NOC-IT - Network'),
    (32, 'Request NOC-KHDV hỗ trợ'),
    (33, 'System'),
    (34, 'NOC-IT - Dịch vụ IT khác'),
    (35, 'Hệ thống ISC - Telesales'),
    (36, 'IDC-HTMN'),
    (37, 'CSOC-Hệ thống FSS'),
    (38, 'NOC-NET'),
    (39, 'FTQ - Nghiệm thu chất lượng'),
    (40, 'INF'),
    (41, 'Đề xuất cải tiến'),
    (42, 'Hệ thống FSI - Fsafe'),
    (43, 'Hệ thống ISC - MOBIX'),
    (44, 'IDC-KH'),
    (45, 'Hỗ trợ nghiệp vụ Foxgold'),
    (46, 'Hỗ trợ cập nhật công cụ'),
    (47, 'FoxPay - Hỗ trợ TT Online'),
    (48, 'NOC-IT - Voice IP/Teleprenses/Jabber/Webex'),
    (49, 'OnCX On-premise'),
    (50, 'Hệ thống ISC - Inside'),
    (51, 'Hệ thống ISC - Inside New V5/NextGen'),
    (52, 'Hệ thống ISC - NextGen'),
    (53, 'Hệ thống ISC - EInvoice'),
    (54, 'Hệ thống ISC - Econtract'),
    (55, 'DEMO TICKET HT'),
    (56, 'Hệ thống ISC - SaleClub'),
    (57, 'INF-Phát triển hạ tầng'),
    (58, 'Hệ thống ISC - Camera'),
    (59, 'Hệ thống ISC - Radius'),
    (60, 'Hệ thống ISC - FPT Play'),
    (61, 'CUS - Hỗ trợ TTOL'),
    (62, 'CS - Nghiệp vụ'),
    (63, 'Hỗ trợ nghiệp vụ CUS'),
    (64, 'CS-Quầy'),
    (65, 'Inside'),
    (66, 'SCC-TMR'),
    (67, 'Hỗ trợ cấu hình mới dịch vụ FTI'),
    (68, 'SCC - Hệ thống máy chủ dịch vụ'),
    (69, 'Broadband Mở Bảo'),
    (70, 'FShare'),
    (71, 'Hỗ trợ dịch vụ CPC'),
    (72, 'Báo cáo vấn đề hệ thống'),
    (73, 'FTI Voice'),
    (74, 'Bàn giao ca trực'),
    (75, 'Hệ thống ISC - Inside/Quản lý HTKT'),
    (76, 'Hệ thống ISC - CustomerRequest'),
    (77, 'Hệ thống ISC - EvoucherFoxGold'),
    (78, 'Hệ thống ISC - OSU4 - P. Hỗ trợ vận hành số 4'),
    (79, 'Hệ thống ISC - Mobipay'),
    (80, 'Hệ thống ISC - IAM'),
    (81, 'Hệ thống ISC - Omni Agent'),
    (82, 'NOC-IT - Phần mềm máy tính'),
    (83, 'Request NOC-KTM'),
    (84, 'Hệ thống ISC - Omnisell'),
    (85, 'Hệ thống ISC - BusinessEvoucher'),
    (86, 'Hỗ trợ kiểm soát hạ tầng'),
    (87, 'Request NOC-OTS hỗ trợ'),
    (88, 'FTQ - Chỉ tiêu - số liệu')
]
HT_STEPS = [
    (1, 'Đóng'),
    (2, 'Hủy'),
    (3, 'Phân công/Nhận xử lý'),
    (4, 'Reject'),
    (5, 'Xác nhận thực hiện xong'),
    (6, 'Chờ Phân tích'),
    (7, 'Xác nhận bắt đầu thực hiện'),
    (8, 'Chờ Phân công / Nhận xử lý'),
    (9, 'Chờ Xử lý hoàn tất'),
    (10, 'Xác nhận kết quả hỗ trợ'),
    (11, 'Chờ Review kết quả'),
    (12, 'Xác nhận kịch bản'),
    (13, 'Tạo ticket'),
    (14, 'Close'),
    (15, 'Chờ xử lý hoàn tất'),
    (16, 'Chờ Đóng'),
    (17, 'Create')
]
SUPPORT_TYPES = [
    (1, 'Hỗ trợ nghiệp vụ'),
    (2, 'Hỗ Trợ NOC'),
    (3, 'Hỗ Trợ FPTplay'),
    (4, 'Hỗ trợ khác'),
    (5, 'Hỗ Trợ ISC'),
    (6, 'Sự cố khách hàng'),
    (7, 'Thay đổi cấu hình theo yêu cầu'),
    (8, 'Hỗ Trợ NOC-VH'),
    (9, 'Cấu hình mới'),
    (10, 'Hỗ trợ Database'),
    (11, 'Hỗ Trợ PayTV'),
    (12, 'Hỗ trợ IT'),
    (13, 'Hỗ trợ FSS'),
    (14, 'Cập nhật F‑monitor'),
    (15, 'Hỗ Trợ NOC-NET'),
    (16, 'Hỗ Trợ NOC-OTS'),
    (17, 'Xử lý lỗi F‑monitor')
]
INTERFACE_NAMES = [
    'XGE1/0/17', 'et-1/0/4', 'XGigabitEthernet0/0/5', 'e2/2', 'XGE1/0/2',
    'XGigabitEthernet0/0/14', 'XGigabitEthernet0/0/11', 'XGigabitEthernet0/0/23',
    'XGigabitEthernet0/0/3', 'XGigabitEthernet0/0/4', 'XGigabitEthernet0/0/19',
    'XGigabitEthernet0/0/22', 'XGigabitEthernet0/0/24', 'ge-0/0/8',
    'XGE1/0/23', 'XGigabitEthernet1/0/44', 'XGigabitEthernet1/0/20',
    'XGigabitEthernet0/0/44', 'XGigabitEthernet0/0/7', 'XGigabitEthernet1/0/10',
    '10GE1/1/0/23', '10GE1/1/0/34', '10GE1/1/0/35', 'XGigabitEthernet1/0/23',
    'XGigabitEthernet0/0/13', 'XGigabitEthernet0/0/15', 'XGigabitEthernet1/0/8',
    'xe-0/0/16', 'ae0', 'xe-0/0/11', 'XGigabitEthernet0/0/17',
    'XGigabitEthernet2/0/21', 'XGigabitEthernet2/0/16', 'XGigabitEthernet0/0/16',
    'xe-2/0/2', 'XGigabitEthernet0/0/10', 'XGigabitEthernet1/0/3',
    'XGigabitEthernet0/0/20', 'e1/1', 'XGigabitEthernet0/0/28',
    'XGigabitEthernet0/0/38', 'XGigabitEthernet0/0/27', 'XGigabitEthernet0/0/18',
    'XGigabitEthernet0/0/21', 'XGigabitEthernet1/0/24', 'XGigabitEthernet1/0/32',
    'XGigabitEthernet2/0/25', 'XGE1/0/24', 'XGigabitEthernet0/0/8',
    'ge-1/0/2', 'XGigabitEthernet0/0/2', 'ge-0/0/5', 'XGigabitEthernet0/0/29',
    'XGigabitEthernet0/0/47', 'ae18', 'xe-0/0/17', 'e2/1',
    'XGigabitEthernet1/0/19', 'XGigabitEthernet1/0/11', 'XGigabitEthernet1/0/21',
    'et-0/0/2', 'XGigabitEthernet1/0/13', 'et-2/0/2', 'et-5/0/2',
    'et-16/0/5', 'et-0/0/49', 'et-3/0/5', 'et-9/1/5', 'et-9/2/2',
    'et-4/6/4', 'et-8/0/2', 'et-0/0/51', 'et-1/0/0', 'et-14/0/2',
    'et-2/0/13', 'et-18/6/3', 'et-0/0/0', 'et-0/0/4', 'et-0/0/3',
    'XGigabitEthernet1/0/4', 'xe-4/1/4', 'xe-7/0/6', 'xe-0/0/47',
    'xe-7/2/3', 'xe-1/1/0', 'xe-0/0/72', 'XGigabitEthernet1/0/12',
    'XGigabitEthernet0/0/35', 'XGigabitEthernet1/0/36', 'XGigabitEthernet1/0/14',
    'XGigabitEthernet0/0/6', 'xe-0/0/5', '40GE1/0/1', '40GE0/0/2',
    '40GE1/0/2', '40GE0/0/5', '40GE1/0/3', 'XGigabitEthernet2/0/6',
    'XGE2/0/13', 'e1/4', 'ae13', 'ge-0/0/47', 'ge-0/0/45', 'ae28',
    'xe-1/0/3', 'ae11', 'xe-1/1/2', 'xe-2/2/9 - L3', 'ae20',
    'xe-0/0/13', 'et-5/1/2', 'XGigabitEthernet1/0/1', 'XGigabitEthernet1/0/48',
    'XGE2/0/11', 'XGigabitEthernet4/0/21', 'XGigabitEthernet1/0/6', 'ae30.0',
    '10GE2/1/0/19', 'et-0/0/23', 'et-1/1/3', 'xe-2/0/0', 'ge-0/0/46',
    'ge-0/0/44', 'ge-0/1/3', 'port21-FX-1000', 'XGigabitEthernet0/0/12',
    'XGigabitEthernet0/0/25', 'XGigabitEthernet1/0/28', 'XGigabitEthernet2/0/34',
    'XGE1/0/21', 'XGigabitEthernet2/0/26', 'XGigabitEthernet1/0/16',
    'XGigabitEthernet2/0/5', 'et-0/0/1', 'et-1/0/1', 'et-0/0/25',
    'ge-0/0/9', 'XGigabitEthernet1/0/45', 'ge-1/1/4', 'xe-0/0/27',
    'ge-0/0/2', 'ge-0/1/7', 'XGigabitEthernet2/0/23', 'XGigabitEthernet2/0/9',
    'xe-0/0/7', 'et-4/1/5', 'XGigabitEthernet1/0/7', 'XGE2/0/1',
    'XGigabitEthernet0/0/1', 'ethernet0/4/1', 'ethernet0/4/3',
    'XGigabitEthernet1/0/35', 'XGigabitEthernet1/0/34', 'et-8/7/1',
    'et-10/0/0', 'xe-0/0/53', 'XGigabitEthernet0/0/9', 'e1/2', 'eth1',
    'ge-0/0/3', 'et-1/0/10', 'et-1/4/4', 'XGigabitEthernet2/0/44',
    'XGigabitEthernet2/0/7', 'et-8/1/5', 'et-4/0/5', 'et-8/0/5',
    'XGE1/0/15', 'et-18/0/8', 'ae51', 'et-12/4/3', 'et-17/0/7',
    'et-12/1/3', 'et-9/3/1', 'et-1/2/0', 'et-11/3/4',
    'XGigabitEthernet1/0/42', 'XGigabitEthernet2/0/10', 'XGigabitEthernet2/0/4',
    'Bridge-Aggregation12', 'ge-0/0/7', 'ge-1/0/7', 'XGE2/0/29',
    'XGE1/0/14', 'Gi1/0/25', 'XGigabitEthernet1/0/37', 'XGigabitEthernet1/0/31',
    'XGigabitEthernet1/0/33', 'ge-0/1/0', 'GigabitEthernet0/0/23',
    'XGigabitEthernet1/0/2', 'ge-0/0/6', 'XGigabitEthernet2/0/17',
    'XGigabitEthernet1/0/9', 'ae17', 'et-0/0/10', 'et-6/0/1', 'ae9',
    'GigabitEthernet0/0/9', 'GigabitEthernet0/0/12', 'et-11/0/5',
    'XGigabitEthernet4/0/7', '10GE1/1/0/41', 'XGigabitEthernet2/0/18',
    'XGigabitEthernet1/0/15', 'et-5/1/5', 'et-12/5/0', 'xe-0/0/6',
    'XGigabitEthernet0/0/33', 'et-5/0/11', 'et-8/1/2', 'ae1',
    'et-0/0/30', 'et-4/0/11', 'et-0/0/19', 'et-0/0/24', 'et-4/1/2',
    'et-0/0/18', 'et-6/0/12', 'et-4/0/12', 'et-5/0/12', 'et-13/0/5',
    'et-16/1/3', 'et-0/0/16', 'et-3/0/12', 'et-2/1/5', 'et-1/0/17',
    'et-0/0/17', 'et-10/0/7', 'et-0/0/14', 'et-0/0/54'
]
ISSUE_GROUPS = [
    (1, 'Hệ thống Access'),
    (2, 'Hệ thống Ngoại vi'),
    (3, 'Hệ thống Core IP'),
    (4, 'Hệ thống Đài trạm PMB'),
    (5, 'Hệ thống Tuyến trực'),
    (6, 'Hệ thống Truyền dẫn'),
    (7, 'Hệ thống Ivoice'),
    (8, 'Hệ thống FPT PLAY-HE'),
    (9, 'Hệ thống iMonitor-IDC'),
    (10, 'Hệ thống HiFPT'),
    (11, 'Hệ thống FPT PLAY-System'),
    (12, 'SCC-Hệ thống máy chủ dịch vụ'),
    (13, 'Hệ thống Khách hàng FTI HNI'),
    (14, 'Hệ thống FPT Play'),
    (15, 'Hệ thống ISC - SYSTEM'),
    (16, 'Hệ thống ISC - TICKET'),
    (17, 'Hệ thống CSOC'),
    (18, 'Hệ thống CMR'),
    (19, 'Hệ thống FPAY'),
    (20, 'Hệ thống Đài trạm INF'),
    (21, 'Hệ thống FPT PLAY-BE'),
    (22, 'Hệ thống Khách hàng FTI HCM'),
    (23, 'Hệ thống ISC - SO'),
    (24, 'Hệ thống FMC'),
    (25, 'Hệ thống ISC - Agent Map'),
    (26, 'Hệ thống Giám sát'),
    (27, 'Hệ thống CSOC - SYSTEM'),
    (28, 'Hệ thống ISC - Inside'),
    (29, 'Hệ thống FPT PLAY-CLIENT'),
    (30, 'Hệ thống BOX IPTV'),
    (31, 'Hệ thống CADS'),
    (32, 'Hệ thống FPT PLAY-Software'),
    (33, 'Hệ thống FSD'),
    (34, 'Hệ thống ISC - Omni Agent'),
    (35, 'Hệ thống IPTV'),
    (36, 'Hệ thống ISC - Radius'),
    (37, 'Hệ thống ISC - OMNI'),
    (38, 'Hệ thống ISC'),
    (39, 'Hệ thống ISC - PAYMENT'),
    (40, 'Hệ thống ISC - Errorsystemchecklist'),
    (41, 'Hệ thống INF-CPELAB'),
    (42, 'Hệ thống ISC - Camera'),
    (43, 'Hệ thống Tác chiến điện tử'),
    (44, 'Hệ thống XLSC và HTKT')
]
ISSUE_NAMES = [
    (1, 'SIDE_DOOR_OPENED!', 1),
    (2, 'Switch Root Down Port', 1),
    (3, 'Khách hàng mất kết nối', 2),
    (4, 'Tập điểm Down', 2),
    (5, 'POP_CABINET_TEMP(Khoang_Thiet_Bi)_HIGH', 1),
    (6, 'ALARM_POP_HUMIDITY_HIGH', 1),
    (7, 'Tập điểm công suất thấp', 2),
    (8, 'Nguồn mất điện AC', 1),
    (9, 'Thiết bị port lỗi CRC', 3),
    (10, 'FRONT_DOOR_OPENED!', 1),
    (11, 'Mất điện AC', 4),
    (12, 'Port PON down', 1),
    (13, 'Kênh Down', 5),
    (14, 'ALARM_DOOR_OPENED', 1),
    (15, 'Lỗi nguồn', 1),
    (16, 'KÊNH SUY HAO CAO', 5),
    (17, 'SWITCH Down Port', 1),
    (18, 'Tủ Cáp Down', 2),
    (19, 'Port Down', 1),
    (20, 'Port tập điểm down', 2),
    (21, 'Temperature high', 3),
    (22, 'Port tập điểm suy hao', 2),
    (23, 'Mất bước sóng', 6),
    (24, 'Thiết bị port down', 1),
    (25, 'Treo control plane', 6),
    (26, 'Lỗi MCB Load open', 1),
    (27, 'POP Down', 1),
    (28, 'Cửa phòng thiết bị mở', 4),
    (29, 'Thiết bị port down', 3),
    (30, 'ALARM_L1-N:LOW_VOLTAGE', 1),
    (31, 'ALARM_FLOOD_DETECTED', 1),
    (32, 'Switch Root Down', 1),
    (33, 'ISIS down/flap', 3),
    (34, 'Thiết bị nguồn mất giám sát', 1),
    (35, 'MEMORY high', 7),
    (36, 'Sub out bất thường (>10%)', 3),
    (37, 'Port thu/phát vượt ngưỡng', 3),
    (38, 'Switch Root Cảnh Báo Mất Nguồn', 1),
    (39, 'Low_Voltage', 1),
    (40, 'Module Nguồn DOWN', 1),
    (41, 'Switch Root Port CRC', 1),
    (42, 'LOST_PHASE', 1),
    (43, 'Thiết bị down', 3),
    (44, 'OLT Down', 1),
    (45, 'ALARM_AC1:ERROR1', 1),
    (46, 'BGP Peer down', 3),
    (47, 'AUD-OUTAGE', 8),
    (48, 'ALARM_AC2:ERROR1', 1),
    (49, 'Ram Quá tải', 9),
    (50, 'Route day 0 fail', 6),
    (51, 'Điện áp DC thấp', 1),
    (52, 'Thiết bị down', 6),
    (53, 'Port Uplink CRC', 1),
    (54, 'Lỗi Battery MCB open', 1),
    (55, 'GEN_OVER_LOAD', 1),
    (56, 'Lỗi nguồn điện', 3),
    (57, 'SPD_DAMAGED!!', 1),
    (58, 'Cảnh báo DDOS quốc tế', 3),
    (59, 'ALARM_Control_Mode:CRITICAL', 1),
    (60, 'Short_Circuit', 1),
    (61, 'ERROR OPMS_Lost 100%', 1),
    (62, 'HIGH_PHASE VOLTAGE', 1),
    (63, 'ALARM_T1_HIGH', 1),
    (64, 'Switch Down', 1),
    (65, 'Nghẽn traffic uplink', 1),
    (66, 'Sofware error', 8),
    (67, 'Máy phát điện lỗi', 4),
    (68, 'Lỗi hệ thống REDIS', 10),
    (69, 'Lỗi RAM', 10),
    (70, 'Lỗi hệ thống THIRD PARTY', 10),
    (71, 'Lỗi hệ thống KAFKA', 10),
    (72, 'Lỗi CPU cao', 10),
    (73, 'LOW_WIRE VOLTAGE', 1),
    (74, 'SWITCH ERROR', 8),
    (75, 'Traffic nghẽn', 3),
    (76, 'ALARM_RUNNING', 1),
    (77, 'CPU high', 7),
    (78, 'CPU high', 3),
    (79, 'POP_FAN1_SPEED_LOW', 1),
    (80, 'Drop Queue', 3),
    (81, 'Thiết bị DPI Sandvine lỗi rewrite_failure', 3),
    (82, 'Traffic nghẽn', 1),
    (83, 'Lỗi Highload CPU K8S Deployment Service', 11),
    (84, 'Kênh lỗi Audio hoặc lỗi Video', 8),
    (85, 'Port CRC', 1),
    (86, 'Thiết bị lỗi', 8),
    (87, 'Call cao', 7),
    (88, 'Thiết bị down', 1),
    (89, 'ERROR_app', 12),
    (90, 'Có chuyển động', 4),
    (91, 'Điều hòa lỗi', 4),
    (92, 'Nguồn mất điện AC', 4),
    (93, 'Thiết bị port lỗi CRC', 1),
    (94, 'AC1: ERROR1', 1),
    (95, 'Gắn KVM', 13),
    (96, 'Port PON công suất phát thấp', 1),
    (97, 'Cảnh báo IPMS', 1),
    (98, 'MEMORY high', 3),
    (99, 'Cửa phòng MPĐ mở', 4),
    (100, 'TS-PID', 8),
    (101, 'Control_State: CRITICAL', 1),
    (102, 'No Video', 14),
    (103, 'ALARM_Mode: MANUAL', 1),
    (104, 'Switch Root Port Suy Hao', 1),
    (105, 'Mac Abnormal', 3),
    (106, 'Thiếu cấu hình pool IP', 3),
    (107, 'Cảnh báo mức sử dụng bộ nhớ của server', 15),
    (108, 'Lỗi khi thực hiện chức năng kiểm tra ắc quy', 1),
    (109, 'Cảnh báo lỗi kết nối đến server', 11),
    (110, 'VID-OUTAGE', 8),
    (111, 'Cảnh báo server bị mất kết nối', 15),
    (112, 'Camera mất kết nối', 4),
    (113, 'Lỗi khác', 16),
    (114, 'PORT PON DOWN', 1),
    (115, 'Port PON DEACTIVATION', 1),
    (116, 'Thiết bị chuyển sang PASSIVE', 7),
    (117, 'Sắp hết pool cấp phát', 3),
    (118, 'Thiết bị card down', 6),
    (119, 'CPU high', 17),
    (120, 'Control_Mode:(ZONE1:CRITICAL, ZONE2:CRITICAL,... , ZONEn:CRITICAL )', 1),
    (121, 'Server Down', 18),
    (122, 'Traffic sụt hoặc mất', 3),
    (123, 'Thiết bị card lỗi/down/tự reboot', 3),
    (124, 'ERROR_Lost 100%', 1),
    (125, 'ALARM_FUEL_LOW', 1),
    (126, 'CPU high', 4),
    (127, 'Temperature high', 4),
    (128, 'ERROR_HUMIDITY_SENSOR_DISCONNECTED', 1),
    (129, 'Thiết bị down', 4),
    (130, 'check_tcp_vasagency.napas.vn_port_48775', 19),
    (131, 'Độ ẩm cao', 4),
    (132, 'OLT Temperature HIGH', 1),
    (133, 'POP mất giám sát', 1),
    (134, 'Cảnh báo từ Kibana', 7),
    (135, 'Cảnh báo điện áp thấp', 6),
    (136, 'Over_Cell_Voltage', 1),
    (137, 'Over_Voltage', 1),
    (138, 'Lỗi ắcquy đổ máy phát điện', 4),
    (139, 'Thiết bị port down', 6),
    (140, 'Mất cấu hình, IP', 20),
    (141, 'ERROR_FIRE_SENSOR_DISCONNECTED', 1),
    (142, 'Có cháy', 4),
    (143, 'Down photonic', 6),
    (144, 'Port PON chập chờn', 1),
    (145, 'Luồng E1 lỗi', 7),
    (146, 'ALARM_SMOKE_DETECTED', 1),
    (147, 'Treo service', 7),
    (148, 'Module nguồn lỗi', 1),
    (149, 'Port PON suy hao cao', 1),
    (150, 'AC1: ERROR2', 1),
    (151, 'AC2: ERROR1', 1),
    (152, 'Status code 499 Critical', 21),
    (153, 'Interface flapping', 3),
    (154, 'Lỗi DATABASE', 10),
    (155, 'ALARM_AC4:ERROR1', 1),
    (156, 'Cụm Cache OTT lỗi', 11),
    (157, 'Lỗi Check rectifier', 1),
    (158, 'Reboot thiết bị', 22),
    (159, 'Gắn KVM', 22),
    (160, 'POP_FAN3_SPEED_LOW', 1),
    (161, 'không sử dụng được 1 / nhiều chức năng', 23),
    (162, 'ALARM_ACCU_VOLTAGE_LOW', 1),
    (163, 'Cụm Cache IPTV lỗi', 11),
    (164, 'CPU load Error', 24),
    (165, 'Port Service Down', 11),
    (166, 'Cảnh báo lỗi kết nối đến port service', 11),
    (167, 'Lỗi chưa xác định', 3),
    (168, 'Number of threads high', 7),
    (169, 'Nghẽn traffic pon port', 1),
    (170, 'BLACK-SCREEN', 8),
    (171, 'Loss of TS synchro', 8),
    (172, 'Kênh BackBone Down', 2),
    (173, 'Active input:backup', 8),
    (174, 'Temperature high', 1),
    (175, 'Rectifier Fail', 1),
    (176, 'Lỗi khác', 25),
    (177, 'Circuit Pack Failed', 6),
    (178, 'Kênh Chập Chờn', 5),
    (179, 'Lỗi khác', 26),
    (180, 'MEMORY high', 17),
    (181, 'Protected', 1),
    (182, 'Lỗi Highload MEM K8S Deployment Service', 11),
    (183, 'Critical_Supply_Air_Temp_High', 1),
    (184, 'ELK Không Nhận Log Giám sát Server', 12),
    (185, 'Mất giám sát thiết bị', 4),
    (186, 'ALARM_AC3:ERROR1', 1),
    (187, 'Thiết bị down', 7),
    (188, 'Cảnh báo Highload CPU Load AVG', 11),
    (189, 'Lỗi khác', 27),
    (190, 'Port PON treo', 1),
    (191, 'CPU Error', 18),
    (192, 'POP_FAN2_SPEED_LOW', 1),
    (193, 'RETURN_AIR_TEMP(Quat_hut_ML)_HIGH', 1),
    (194, 'Không nhận nguồn', 20),
    (195, 'Rectifier Fail', 4),
    (196, 'Lỗi không tạo SC', 26),
    (197, 'Hỗ Block', 20),
    (198, 'Database bị lỗi', 6),
    (199, 'Lỗi Juniper Chassis Alarm', 3),
    (200, 'Switch Root cảnh báo CPU High', 1),
    (201, 'Disk OS Used', 18),
    (202, 'Lỗi Pod Service Container API', 11),
    (203, 'Lỗi Battery MCB open', 4),
    (204, 'Thiết bị nguồn mất giám sát', 4),
    (205, 'No Audio', 14),
    (206, 'UCM-CCX Other Services', 7),
    (207, 'Temperature high', 6),
    (208, 'Lỗi full ổ cứng, phân vùng OS', 15),
    (209, 'check_tcp_abtrip.vn_port_443', 19),
    (210, 'Cảnh báo lỗi đồng bộ time NTP', 11),
    (211, 'Dịch vụ FPL có Jitter tăng cao', 3),
    (212, 'Lỗi hệ thống Hi FPT', 10),
    (213, 'Switch Treo', 1),
    (214, 'Lỗi Rectifier Fan Fail', 1),
    (215, 'Lỗi thiết bị CLS', 4),
    (216, 'CPU ERROR', 8),
    (217, 'BGP Peer down', 1),
    (218, 'Memory high', 7),
    (219, 'Treo session PPPoE', 3),
    (220, 'ALARM_VOLTAGE_UNBALANCE', 1),
    (221, 'PROGRAM-OUTAGE', 8),
    (222, 'Kênh Bị Down', 8),
    (223, 'Active input switch:backup is active', 8),
    (224, 'Thiết bị down', 8),
    (225, 'ACCU_CABINET_TEMP(Khoang_ACCU)_HIGH', 1),
    (226, 'ERROR MLCX_Lost 100%', 1),
    (227, 'KHG mất kết nối diện rộng', 26),
    (228, 'Số lượng lớn KHG ở 1 khu vực ko truy cập được mạng hoặc mất số dịch vụ cụ thể', 3),
    (229, 'Kênh bị rút hình giật hình', 8),
    (230, 'Nhiệt độ phòng MPĐ tăng cao', 4),
    (231, 'Thiết bị thiếu cấu hình vlan', 1),
    (232, 'Lỗi chưa xác định', 1),
    (233, 'Mất kết nối (Lỗi quảng bá, loop routing...)', None),
    (234, 'Giám sát BTBD hệ thống điều hòa', None),
    (235, 'Truy cập chậm (độ trễ cao, packet loss, optimize..)', None),
    (236, 'Đăng ký truy cập DC', None),
    (237, 'Yêu cầu hướng dẫn quy trình', None),
    (238, 'Lỗi tool Chuyển IP cho KHG', None),
    (239, '[Website] Lỗi thanh toán', None),
    (240, '[App (Smart Phone)] Không xem được K+', None),
    (241, '[App (Smart Phone)] KH yêu cầu Hủy gói và Hoàn tiền', None),
    (242, 'Xử lý yêu cầu SR', None),
    (243, 'Chuyển trường, chia lại đặt cọc', None),
    (244, 'Khác', None),
    (245, '[App (Smart TV)] Lỗi âm thanh', None),
    (246, 'Kênh bị flapping', None),
    (247, 'Nhận hàng hóa được gửi về NOC-CGY', None),
    (248, '[App (Smart Phone)] Vấn đề khác', None),
    (249, 'Kích thanh toán', None),
    (250, 'Gửi thanh toán, đặt cọc tiền mặt', None),
    (251, 'Kiểm tra cước hóa đơn, khoản thu', None),
    (252, 'Điều chỉnh kỳ hạn hóa đơn', None),
    (253, '[App (Smart TV)] Không đăng nhập được tài khoản', None),
    (254, 'Giảm trừ cước dịch vụ', None),
    (255, 'Giám sát chương trình truyền hình trực tiếp', None),
    (256, 'Chập chờn (flapping)', None),
    (257, 'Kiểm tra giao dịch', None),
    (258, 'KH cần hỗ trợ thông tin khác', None),
    (259, '[Box OTT] Không active được Dịch vụ', None),
    (260, 'Hướng dẫn xuất hóa đơn', None),
    (261, 'Hết giao dịch', None),
    (262, '[CMR] Kiểm tra chuyển động (thumbnail - video không sẵn sàng)', None),
    (263, 'KH down/up không đủ băng thông', None),
    (264, 'Xử lý tranh chấp', None),
    (265, 'Add lại tên sale trên hợp đồng, hóa đơn', None)
]
LOCATIONS = [
    (1, '06. Khánh Hòa'),
    (2, '01. Hà Nội'),
    (3, '11. Tây Bắc Bộ'),
    (4, '04. Hải Phòng'),
    (5, '13. Tây Nguyên và Miền Trung'),
    (6, '14. Đông Nam Bộ'),
    (7, '12. Đông Bắc Bộ'),
    (8, '09. Bình Dương'),
    (9, '15. Tây Nam Bộ'),
    (10, '07. Hồ Chí Minh'),
    (11, '10. Vũng Tàu'),
    (12, '03. Hải Dương'),
    (13, '02. Quảng Ninh'),
    (14, '05. Đà Nẵng'),
    (15, 'Quốc tế'),
    (16, '08. Đồng Nai'),
    (17, 'Vùng 5'),
    (18, 'Vùng 1'),
    (19, 'Tất cả'),
    (20, 'Vùng 3'),
    (21, 'Vùng 2'),
    (22, 'Vùng 7'),
    (23, 'Vùng 4'),
    (24, 'Vùng 6')
]
POPS = [
    (1, 'NTGP015'),
    (2, 'HNIP591'),
    (3, 'TQGP031'),
    (4, 'HPGP044'),
    (5, 'HUEP028'),
    (6, 'NTGP051'),
    (7, 'GLIP038'),
    (8, 'BTNP004'),
    (9, 'HNIP688'),
    (10, 'BDGP064'),
    (11, 'HNIP291'),
    (12, 'HNIP327'),
    (13, 'HNIP278'),
    (14, 'BDGP010'),
    (15, 'HNIP283'),
    (16, 'BNHP050'),
    (17, 'DBNP002'),
    (18, 'TBHP022'),
    (19, 'AGGP054'),
    (20, 'TNHP038'),
    (21, 'HUEP090'),
    (22, 'BNHP025'),
    (23, 'HNIP420'),
    (24, 'QTIP022'),
    (25, 'BRUP072'),
    (26, 'HPGM001'),
    (27, 'TGGP028'),
    (28, 'NTGP012'),
    (29, 'LANP036'),
    (30, 'HDGP099'),
    (31, 'TNNP053'),
    (32, 'HGGP019'),
    (33, 'HNIP656'),
    (34, 'HPGP123'),
    (35, 'HGGP016'),
    (36, 'PYNP012'),
    (37, 'HPGP045'),
    (38, 'DTPP027'),
    (39, 'QNHP017'),
    (40, 'BDHP049'),
    (41, 'HUEP087'),
    (42, 'NTGP048'),
    (43, 'HYNP085'),
    (44, 'HNIP627'),
    (45, 'HTHP031'),
    (46, 'LANP023'),
    (47, 'HNIP766'),
    (48, 'CTOP054'),
    (49, 'LANP040'),
    (50, 'HNIP135'),
    (51, 'HPGP086'),
    (52, 'HPGP031'),
    (53, 'HPGP012'),
    (54, 'HPGP055'),
    (55, 'BDGP051'),
    (56, 'HNIP205'),
    (57, 'THAP062'),
    (58, 'HPGP017'),
    (59, 'QNHP003'),
    (60, 'HPGP006'),
    (61, 'QNHP121'),
    (62, 'HPGP015'),
    (63, 'HPGP058'),
    (64, 'HPGP018'),
    (65, 'HPGP013'),
    (66, 'HPGP060'),
    (67, 'HPGP105'),
    (68, 'BTNP023'),
    (69, 'PTOP028'),
    (70, 'DNGP148'),
    (71, 'QNHP100'),
    (72, 'HPGP063'),
    (73, 'HNIP465'),
    (74, 'HUEP108'),
    (75, 'LDGP041'),
    (76, 'HUEP104'),
    (77, 'HCMP543'),
    (78, 'TNHM001'),
    (79, 'TNHP021'),
    (80, 'TNHP004'),
    (81, 'DTPP020'),
    (82, 'HTHP011'),
    (83, 'TGGP011'),
    (84, 'HCMP515'),
    (85, 'BNHP018'),
    (86, 'HNIP013'),
    (87, 'HCMP021'),
    (88, 'HNIP405'),
    (89, 'HNIP250'),
    (90, 'HPGP074'),
    (91, 'HNIP415'),
    (92, 'THAP036'),
    (93, 'THAP031'),
    (94, 'THAP017'),
    (95, 'THAP027'),
    (96, 'THAP026'),
    (97, 'THAP024'),
    (98, 'THAP074'),
    (99, 'THAP007'),
    (100, 'NDHP019'),
    (101, 'THAP040'),
    (102, 'HPGP002'),
    (103, 'HNIP668'),
    (104, 'HUEP118'),
    (105, 'BRUP024'),
    (106, 'QNHP044'),
    (107, 'QNHP088'),
    (108, 'HUEP120'),
    (109, 'QNHP086'),
    (110, 'HNIP511'),
    (111, 'NBHP022'),
    (112, 'HUEP103'),
    (113, 'BNHP007'),
    (114, 'HCMP569'),
    (115, 'QNHP087'),
    (116, 'QNHP005'),
    (117, 'CTOP074'),
    (118, 'HCMP671'),
    (119, 'QNHP041'),
    (120, 'QNHP043'),
    (121, 'QNHP085'),
    (122, 'HCMP378'),
    (123, 'QNHP042'),
    (124, 'QNHP046'),
    (125, 'BNHP062'),
    (126, 'VPCP047'),
    (127, 'HCMP680'),
    (128, 'HPGP036'),
    (129, 'BGGP008'),
    (130, 'HNIP548'),
    (131, 'QNHP016'),
    (132, 'BNHP076'),
    (133, 'QNMP060'),
    (134, 'QNMP073'),
    (135, 'NANP084'),
    (136, 'DNIP016'),
    (137, 'THAP021'),
    (138, 'DNGM001'),
    (139, 'NTGP030'),
    (140, 'HNMP007'),
    (141, 'HNMP023'),
    (142, 'HNIM011'),
    (143, 'HCMP263'),
    (144, 'HNMP021'),
    (145, 'HGGP004'),
    (146, 'HGGP013'),
    (147, 'DLKP006'),
    (148, 'GLIW001'),
    (149, 'HCMP709'),
    (150, 'BGGP046'),
    (151, 'HCMP298'),
    (152, 'HNIP261'),
    (153, 'QNMP062'),
    (154, 'HNIB014'),
    (155, 'HCMP192'),
    (156, 'DNIP004'),
    (157, 'LCIP009'),
    (158, 'THAP038'),
    (159, 'HNIP549'),
    (160, 'HNIP761'),
    (161, 'BDGP058'),
    (162, 'HNIB018'),
    (163, 'HNIP484'),
    (164, 'HUEP114'),
    (165, 'VLGP028'),
    (166, 'BRUP079'),
    (167, 'BRUP003'),
    (168, 'BDGP062'),
    (169, 'HNIP594'),
    (170, 'BTNP021'),
    (171, 'HUEP136'),
    (172, 'HNMP009'),
    (173, 'HNMP010'),
    (174, 'HNMP008'),
    (175, 'HNMP006'),
    (176, 'HNMM001'),
    (177, 'HNMP018'),
    (178, 'HNMP015'),
    (179, 'NANP048'),
    (180, 'NANP089'),
    (181, 'NTNP030'),
    (182, 'QNHP069'),
    (183, 'NANP092'),
    (184, 'QNHP068'),
    (185, 'QNHP070'),
    (186, 'QNHP118'),
    (187, 'HNIP486'),
    (188, 'NTNP033'),
    (189, 'DLKP011'),
    (190, 'NTNP029'),
    (191, 'BDGP071'),
    (192, 'HNIP343'),
    (193, 'HNIP313'),
    (194, 'HCMB427'),
    (195, 'TNNP059'),
    (196, 'LANP047'),
    (197, 'KGGP015'),
    (198, 'HNIP628'),
    (199, 'HUEM001'),
    (200, 'BDGP073'),
    (201, 'HCMM002'),
    (202, 'KGGP009'),
    (203, 'LDGP057'),
    (204, 'HUEP117'),
    (205, 'BDGP029'),
    (206, 'HNIP361'),
    (207, 'BDGP007'),
    (208, 'DBNP006'),
    (209, 'HNIP247'),
    (210, 'HNIB001'),
    (211, 'HCMP222'),
    (212, 'LDGM001'),
    (213, 'HUEP089'),
    (214, 'BNHM001'),
    (215, 'HNIB055'),
    (216, 'DNGP137'),
    (217, 'HCMP332'),
    (218, 'HCMP242'),
    (219, 'DNIP120'),
    (220, 'HDGP074'),
    (221, 'HDGP088'),
    (222, 'HDGP089'),
    (223, 'HDGP098'),
    (224, 'LANP038'),
    (225, 'HNIP448'),
    (226, 'AGGP009'),
    (227, 'HNIP020')
]
PROCESSING_UNITS = [
    (1, 'Hạ tầng'),
    (2, 'Thuê bao'),
    (3, 'SCC'),
    (4, 'INF-BTHT'),
    (5, 'P.HT4'),
    (6, 'PMB-QLVH'),
    (7, 'SCC-VoIP'),
    (8, 'FPL-HeadEnds'),
    (9, 'IDC-VHMB'),
    (10, 'CSOC-IT'),
    (11, 'NOC-TKVH'),
    (12, 'FTQ-PQA'),
    (13, 'HIFPT-VH'),
    (14, 'SOC-FPL-System'),
    (15, 'FTI-SD'),
    (16, 'SCC-Sys'),
    (17, 'ISC-SYS'),
    (18, 'ISC-TICKET'),
    (19, 'SOC-System'),
    (20, 'SOC-SYSTEM-FLI'),
    (21, 'FPAY-SYS'),
    (22, 'FLI-System'),
    (23, 'P.HT3'),
    (24, 'FPL-Backend'),
    (25, 'IDC-VHMN'),
    (26, 'P.HT2'),
    (27, 'SOC-FPL-SYSTEM'),
    (28, 'FMC'),
    (29, 'FTI-IDC-HCM'),
    (30, 'ISCTT-SR-CDD'),
    (31, 'INF-KTMNV MB'),
    (32, 'ISC'),
    (33, 'IDC-VHMN02'),
    (34, 'P.HT1'),
    (35, 'INF-HT1-DC'),
    (36, 'INF-QLTKVH MB'),
    (37, 'PMB-TKVHDT'),
    (38, 'TIN-HTDN'),
    (39, 'SCC-RnD'),
    (40, 'FPL-Distributor'),
    (41, 'BDA Camera'),
    (42, 'SCC-Tool'),
    (43, 'INF-KTHT'),
    (44, 'CADS-SYSTEM'),
    (45, 'FTI-IDC-HN'),
    (46, 'FTI-KT HN'),
    (47, 'FTI VOICE'),
    (48, 'FPAY-VH247'),
    (49, 'FLI-HTKT'),
    (50, 'FPL-Client'),
    (51, 'ISC-KD-LUONG TINPNC'),
    (52, 'PNC'),
    (53, 'VLGTU'),
    (54, 'CADS-DATA'),
    (55, 'ISC-AgentMap'),
    (56, 'NOC-OTS'),
    (57, 'ISC-OmniAgent'),
    (58, 'THATU'),
    (59, 'ISC-ServiceOps'),
    (60, 'FPT Play'),
    (61, 'FSD'),
    (62, 'NOC-KTM'),
    (63, 'SCC-QA'),
    (64, 'ISC-SP-Radius'),
    (65, 'ISC-KD-PHAN CONG'),
    (66, 'ISC-PAYMENT'),
    (67, 'INF-BTHT2'),
    (68, 'FTI-KT-HCM'),
    (69, 'ISCTT-SR-HTKT'),
    (70, 'ISC-RII'),
    (71, 'BGGBGD'),
    (72, 'ISCTT-SR'),
    (73, 'INF-BTHT1'),
    (74, 'INF-KTMNV MN'),
    (75, 'INF-BTHT3'),
    (76, 'IDC-HTMB'),
    (77, 'INF-CPELAB'),
    (78, 'FPL-Bigdata'),
    (79, 'ISC-CMR'),
    (80, 'CSOC-GPGS'),
    (81, 'FPL-Content'),
    (82, 'NOC-NET'),
    (83, 'TIN'),
    (84, 'QUANLY_THONGTHUONG_Hệ thống Giám sát'),
    (85, 'BLUTU'),
    (86, 'ISC-SP-IAM'),
    (87, 'ISC-DBA')
]
QUEUES = [
    (1, 'SCC'),
    (2, 'TIN'),
    (3, 'INF-BTHT'),
    (4, 'PNC'),
    (5, 'TIN-HTDN'),
    (6, 'P.HT4'),
    (7, 'FTQ-PQA'),
    (8, 'SCC-RnD'),
    (9, 'FTI-SD'),
    (10, 'P.HT2'),
    (11, 'FTI-IDC-HN'),
    (12, 'P.HT1'),
    (13, 'P.HT3'),
    (14, 'PKT-HN14'),
    (15, 'PMB-QLVH'),
    (16, 'DVKH - Ho tro TTOL'),
    (17, 'FTI-IDC-HCM'),
    (18, 'PKT-HN11'),
    (19, 'SCC-VoIP'),
    (20, 'FPL-HeadEnds'),
    (21, 'IDC-VHMB'),
    (22, 'CSOC-IT'),
    (23, 'INF-QLTKVH MB'),
    (24, 'INF-KTHT'),
    (25, 'NOC-TKVH'),
    (26, 'HIFPT-VH'),
    (27, 'SOC-FPL-System'),
    (28, 'SCC-Sys'),
    (29, 'ISC-SYS'),
    (30, 'INF-BTHT2'),
    (31, 'PKT-HN13'),
    (32, 'ISC-TICKET'),
    (33, 'SOC-System'),
    (34, 'SOC-SYSTEM-FLI'),
    (35, 'FPAY-SYS'),
    (36, 'FLI-System'),
    (37, 'FPL-Backend'),
    (38, 'IDC-VHMN'),
    (39, 'SOC-FPL-SYSTEM'),
    (40, 'FMC'),
    (41, 'ISCTT-SR-CDD'),
    (42, 'INF-KTMNV MB'),
    (43, 'ISC'),
    (44, 'IDC-VHMN02'),
    (45, 'INF-HT1-DC'),
    (46, 'INF-BTHT3'),
    (47, 'PMB-TKVHDT'),
    (48, 'FTI-KT HN'),
    (49, 'FTI VOICE'),
    (50, 'SOC'),
    (51, 'DVKH - CN'),
    (52, 'FPT Play'),
    (53, 'FTI-KT-HCM'),
    (54, 'CS-QUAY'),
    (55, 'FTI-KSTK'),
    (56, 'CS'),
    (57, 'DVKH - Nghiep vu'),
    (58, 'FTQ'),
    (59, 'CUS'),
    (60, 'FTI-CS'),
    (61, 'FLI- HTKD - CS'),
    (62, 'FTQ-PQC-HCM'),
    (63, 'FPL-Distributor'),
    (64, 'IDC-HTMB'),
    (65, 'NOC-KHDV'),
    (66, 'FTEL'),
    (67, 'NOC-KTM'),
    (68, 'TINPNC-SIMN'),
    (69, 'FTQ-PQC-VUNG'),
    (70, 'FTQ-PQC-HN'),
    (71, 'NOC-QI'),
    (72, 'FES'),
    (73, 'IDC-KH'),
    (74, 'INF-KSTK'),
    (75, 'CSKH'),
    (76, 'INDO'),
    (77, 'FLI- HTKD - Kho'),
    (78, 'FLI-HTKT'),
    (79, 'IDC-HTMN'),
    (80, 'INF-CPELAB'),
    (81, 'FPAY-VH247'),
    (82, 'FLI- HTKD - HCNS'),
    (83, 'FTI-KH-HCM'),
    (84, 'FAF'),
    (85, 'FPL-Client'),
    (86, 'SCC-QA'),
    (87, 'ISC-CallCenter-ExtensionWarning'),
    (88, 'MKT-ChinhSach'),
    (89, 'INF-KTMNV MN'),
    (90, 'FIP'),
    (91, 'FHR'),
    (92, 'FPT PLAY-QA'),
    (93, 'FOXGOLD'),
    (94, 'ISC-ServiceOps'),
    (95, 'ISC-DBA'),
    (96, 'ISCTT-SR'),
    (97, 'ISC-EInvoice'),
    (98, 'ISCTT-SR-TL-TN'),
    (99, 'ISC-SU02-VH'),
    (100, 'INF-BTHT1'),
    (101, 'INF-TKHT'),
    (102, 'FTQ-TEST-CHANG'),
    (103, 'ISC-Building'),
    (104, 'ISC-KD-VAT TU'),
    (105, 'BDA Camera'),
    (106, 'DSC'),
    (107, 'FSI-Support'),
    (108, 'QUANLY_THONGTHUONG_Hệ thống Container'),
    (109, 'ISC-INSIDE'),
    (110, 'INF-KHMN'),
    (111, 'ISC-Telesale'),
    (112, 'QUANLY_KHANCAP_PILOT_Hệ thống FOXPAY'),
    (113, 'ISC-CMR'),
    (114, 'TICKET_SYSTEM'),
    (115, 'CADS-SYSTEM'),
    (116, 'IIDDT1'),
    (117, 'FPL-Bigdata'),
    (118, 'FSD'),
    (119, 'FTI-DEM'),
    (120, 'FPLAY-OTT'),
    (121, 'IIDDT2'),
    (122, 'ISCTT-SR-KPDV'),
    (123, 'ISC-KD-TKBT'),
    (124, 'SCC-Tool'),
    (125, 'ISC-Econtract'),
    (126, 'ISC-SaleClub'),
    (127, 'ISC-SP-Radius'),
    (128, 'INF-KHHT MB'),
    (129, 'ISC-FPL'),
    (130, 'ISC-KD-Contract'),
    (131, 'NOC-NET'),
    (132, 'HBHBGD'),
    (133, 'NOC-OTS'),
    (134, 'TGGTU'),
    (135, 'PKT-HN10'),
    (136, 'PKT-HN8'),
    (137, 'AGGTU'),
    (138, 'ISCTT-SR-CDV'),
    (139, 'FSHARE'),
    (140, 'ISCTT-SR-HTKT'),
    (141, 'FTI-QA'),
    (142, 'ISCTT-SR-TTKH'),
    (143, 'HYNTU'),
    (144, 'CSOC-GPGS'),
    (145, 'ISC-KD-PHAN CONG'),
    (146, 'ISC-KD-LUONG TINPNC'),
    (147, 'VLGTU'),
    (148, 'CADS-DATA'),
    (149, 'ISC-AgentMap'),
    (150, 'PKT-HN9'),
    (151, 'PKT-HN7'),
    (152, 'PKT-HN12'),
    (153, 'ISC-OmniAgent'),
    (154, 'THATU'),
    (155, 'ISC-PAYMENT'),
    (156, 'ISC-RII'),
    (157, 'BGGBGD'),
    (158, 'ISC-CR'),
    (159, 'ISC-EVC'),
    (160, 'SG13TU'),
    (161, 'ISC-MOBIX'),
    (162, 'ISC-INSIDEv4'),
    (163, 'FPL-QC'),
    (164, 'FPL-Content'),
    (165, 'ISC-Mobipay'),
    (166, 'XAutoTicketTest'),
    (167, 'ISC-SP-IAM'),
    (168, 'ISC-OSU4'),
    (169, 'ISCTT-SR-Tra-Truoc'),
    (170, 'INF-CN'),
    (171, 'ISCTT-SR-KNDV'),
    (172, 'FAD-CSVC'),
    (173, 'TQGBGD'),
    (174, 'QUANLY_THONGTHUONG_PILOT_Hệ thống FOXPAY'),
    (175, 'CBGBGD'),
    (176, 'QUANLY_THONGTHUONG_Hệ thống Giám sát'),
    (177, 'QUANLY_THONGTHUONG_Hệ thống FoxPay'),
    (178, 'ISC-OSU2'),
    (179, 'ISCTT-SR-GDHD'),
    (180, 'BLUTU'),
    (181, 'ISC-PORTNET'),
    (182, 'QUANLY_KHANCAP_Hệ thống FPT Play'),
    (183, 'ISC-KHTN'),
    (184, 'TNNTU'),
    (185, 'ISC-QLCS'),
    (186, 'ISC-KD-BAO CAO'),
    (187, 'ISC-DKOL'),
    (188, 'ISC-KD-TLTSD')
]
REASONS = [
    (1, 'Bộ OPMS Cảnh Báo', 'Cảnh báo đóng, mở cửa'),
    (2, 'Đứt cable', 'Đứt cáp'),
    (3, 'Đứt cáp thuê bao', 'Điện lực thanh thải, cắt cáp, chập cháy cáp, phá hoại'),
    (4, 'Bảo trì có kế hoạch', 'Bảo trì có kế hoạch'),
    (5, 'Lỗi tập điểm', 'Điện lực quy hoạch'),
    (6, 'Chưa xác định được nguyên nhân', 'Chưa xác định được nguyên nhân'),
    (7, 'Lỗi core tại tập điểm', 'Lỗi core tại tập điểm'),
    (8, 'Bộ IPMS Cảnh Báo', 'Cảnh báo sensor IPMS'),
    (9, 'Đứt cáp thuê bao', 'Chưa xác định được nguyên nhân'),
    (10, 'Lỗi măng xông', 'Lỗi core tại măng xông, phải hàn nối lại'),
    (11, 'Mất điện lưới', 'Điện lực cắt điện'),
    (12, 'Lỗi đầu xa', 'Lỗi do phía đối tác đầu xa'),
    (13, 'Đứt cáp 8 core hàn 2 đầu', 'Đứt cáp do chập cháy ĐL phong tỏa'),
    (14, 'Lỗi core dẫn tới bộ chia cấp 1', 'Lỗi core tại MX'),
    (15, 'Lỗi bộ chia', 'Bộ chia suy hao, phải thay thế'),
    (16, 'Cảnh báo sai', 'cảnh báo sai'),
    (17, 'Đứt cáp 24 core hàn 2 đầu', 'Đứt cáp do đứt cắt, không chuyển hướng được, phải trồng cột mới'),
    (18, 'Lỗi core đầu vào bộ chia tại tập điểm', 'Core đứt trong tập điểm, phải hàn nối lại'),
    (19, 'Pigtail đầu ra của bộ chia đứt', 'Pigtail đầu ra của bộ chia đứt, phải hàn nối lại'),
    (20, 'Đứt cáp', 'Đứt cáp'),
    (21, 'Lỗi thiết bị', 'Lỗi Fantray, filter gây quá nhiệt'),
    (22, 'Lỗi core đầu vào bộ chia tại tập điểm', 'Core cong gập trong tập điểm, không phải hàn nối lại'),
    (23, 'Đứt cable 24 core hàn 2 đầu', 'Đứt cáp do chập cháy điện lực phong tỏa'),
    (24, 'Ngoại vi', 'Cáp down/up không rõ nguyên nhân, bước sóng tự khôi phục'),
    (25, 'Đứt cáp 24 core hàn 2 đầu', 'Đứt cáp ban đêm'),
    (26, 'Đứt cáp 12 core hàn 2 đầu', 'Đứt cáp phải do chập cháy'),
    (27, 'Đứt cáp 24 core hàn 2 đầu', 'Đứt cáp phải do chập cháy'),
    (28, 'Lỗi logic', 'Lỗi treo control plane'),
    (29, 'CB thiết bị đang ở trạng thái OFF', 'Bảo trì có kế hoạch'),
    (30, 'Đứt cáp 12 core hàn 2 đầu', 'Đứt cáp do tỉa cây xanh'),
    (31, 'Lỗi thao tác', 'Nhân sự mở cửa XLSC'),
    (32, 'Chưa xác định được nguyên nhân', 'Chưa xác định được nguyên nhân'),
    (33, 'Bộ IPMS Cảnh Báo', 'Cảnh báo máy phát điện'),
    (34, 'Lỗi Tủ cáp', 'Thay casset trong Tủ cáp'),
    (35, 'Đứt cáp 12 core hàn 1 đầu', 'Gập cáp, phải hàn nối lại cáp'),
    (36, 'Lỗi kênh, cáp', 'Lỗi do phía đối tác đầu xa'),
    (37, 'Lỗi logic', 'Không xác định, thiết bị tự hoạt động trở lại'),
    (38, 'Lỗi ngoại vi', 'Đứt cáp do đơn vị cá nhân tác động'),
    (39, 'Lỗi môi trường hoạt động', 'Lỗi hệ thống điều hòa gây quá nhiệt'),
    (40, 'Lỗi thiết bị', 'Lỗi nguồn'),
    (41, 'Đứt cáp 12 core hàn 2 đầu', 'Đứt cáp do chập cháy ĐL phong tỏa'),
    (42, 'Lỗi cáp', 'Lỗi Core Cable'),
    (43, 'Mất điện, accu chạy kiệt', 'Không chạy được MPĐ do mưa bão, thiên tai'),
    (44, 'Hệ thống tự hoạt động trở lại', 'Hệ thống tự hoạt động trở lại'),
    (45, 'Bộ OPMS Cảnh Báo', 'Cảnh báo mất pha AC'),
    (46, 'Lỗi ngoại vi', 'Lỗi core cáp'),
    (47, 'Cảnh báo phân đoạn access', 'KHG ảnh hưởng do OLT down'),
    (48, 'Đứt cable 12 core hàn 2 đầu', 'Đứt cáp do đứt cắt'),
    (49, 'Bảo trì có kế hoạch', 'Quy hoạch thiết bị'),
    (50, 'Lỗi dây nhảy quang phải thay thế', 'Lỗi dây nhảy quang phải thay thế'),
    (51, 'Lỗi logic', 'Lỗi cấu hình logic'),
    (52, 'Mất điện', 'Điện Lực cắt điện'),
    (53, 'Lỗi core đầu vào bộ chia tại tập điểm', 'Core cong gập trong tập điểm, phải hàn nối lại'),
    (54, 'Mất điện AC', 'Mất điện lưới'),
    (55, 'Không có thành phần audio trong luồng kênh', 'Lỗi source multicast'),
    (56, 'Bộ IPMS Cảnh Báo', 'Cảnh báo lỗi hệ thống lạnh'),
    (57, 'Lỗi logic', 'Nhiều connection cùng thời điểm'),
    (58, 'Bảo trì có kế hoạch', 'Kiểm tra accu định kỳ'),
    (59, 'Lỗi thiết bị', 'Lỗi chassic'),
    (60, 'Lỗi logic', 'Lỗi cấu hình'),
    (61, 'Đứt cáp 24 core hàn 2 đầu', 'Đứt cáp do chập cháy ĐL phong tỏa'),
    (62, 'Lỗi thiết bị', 'Lỗi Module PON PORT'),
    (63, 'Bảo trì có kế hoạch', 'Reboot thiết bị'),
    (64, 'Automat accu đang ở trạng thái mở', 'Bảo trì có kế hoạch'),
    (65, 'Bộ IPMS Cảnh Báo', 'Cảnh báo dòng điện thực tế  ở 85% dòng điện định mức của máy phát điện.'),
    (66, 'Bộ IPMS Cảnh Báo', 'Cảnh báo mất pha AC'),
    (67, 'Bảo trì có kế hoạch', 'Nâng cấp hệ thống'),
    (68, 'Đứt cáp 4 core hàn 2 đầu', 'Đứt cáp do thiên tai, thời tiết xấu (bắt khả kháng)'),
    (69, 'Lỗi phần cứng thiết bị', 'Lỗi nguồn của thiết bị'),
    (70, 'Bộ OPMS Cảnh Báo', 'Cảnh báo thiết bị CLS'),
    (71, 'Lỗi logic', 'Lỗi bị tấn công DDOS'),
    (72, 'Mất điện AC', 'Không có nguồn backup'),
    (73, 'Lỗi thiết bị, phần tử của OPMS', 'Lỗi mất kết nối OPMS'),
    (74, 'Lỗi logic', 'Lỗi do phía đối tác đầu xa'),
    (75, 'Lỗi kênh, cáp', 'Lỗi kênh phân đoạn quốc tế'),
    (76, 'Bộ IPMS Cảnh Báo', 'Cảnh báo điện áp pha cao'),
    (77, 'Đứt cáp 12 core hàn 2 đầu', 'Đứt cáp ban đêm'),
    (78, 'Mất điện lưới', 'Mất điện lưới, accu xả'),
    (79, 'Đứt cáp 16 core hàn 2 đầu', 'Đứt cáp do chập cháy ĐL phong tỏa'),
    (80, 'Đứt cable', 'Bảo trì/theo dõi có kế hoạch'),
    (81, 'Traffic cảnh báo cao', 'Traffic cảnh báo cao'),
    (82, 'Đứt cáp 24 core hàn 2 đầu', 'Đứt cáp do đứt cắt (chuyển hướng được)'),
    (83, 'Software error', 'Lỗi network connection'),
    (84, 'Lỗi thiết bị', 'Lỗi ATS'),
    (85, 'Đứt cáp 24 core hàn 2 đầu', 'Đứt cáp do thiên tai, thời tiết xấu (bắt khả kháng)'),
    (86, 'Chưa rõ nguyên nhân sụt user', 'Chưa rõ nguyên nhân sụt user'),
    (87, 'Lỗi kênh, cáp', 'Lỗi kênh truyền dẫn'),
    (88, 'REDIS không kết nối được', 'Lỗi phần cứng'),
    (89, 'Lỗi phần cứng', 'Lỗi RAM'),
    (90, 'Lỗi đồng bộ data', 'Không đồng bộ được data'),
    (91, 'KAFKA không kết nối được', 'Lỗi phần cứng'),
    (92, 'Lỗi phần cứng', 'Lỗi CPU'),
    (93, 'Bộ IPMS Cảnh Báo', 'Cảnh báo điện áp dây thấp'),
    (94, 'Lỗi thiết bị', 'Lỗi Module'),
    (95, 'Lỗi logic', 'Lệch tải IPLC'),
    (96, 'Đứt cáp 8 core hàn 2 đầu', 'Đứt cáp ban đêm'),
    (97, 'Bộ OPMS Cảnh Báo', 'Cảnh báo lỗi hệ thống lạnh, làm mát'),
    (98, 'Đứt cáp 24 core hàn 2 đầu', 'Đứt cáp phải do xe kéo'),
    (99, 'Lỗi thiết bị', 'Lỗi Port PON'),
    (100, 'Lỗi logic', 'Lệch tải do LSP'),
    (101, 'Khu vực mất điện diện rộng', 'Khu vực mất điện diện rộng'),
    (102, 'Lỗi logic', 'Lỗi kết nối đến server Monitor'),
    (103, 'Lỗi măng xông', 'Lỗi core tại măng xông, không phải hàn nối lại'),
    (104, 'Lỗi bộ chia', 'Lỗi bộ chia'),
    (105, 'Lỗi ngoại vi', 'Lỗi Core Cable'),
    (106, 'Kênh truyền hình HD', 'Nội dung của đài'),
    (107, 'Encoder', 'Lỗi network connection'),
    (108, 'Pigtail đầu ra của bộ chia lỗi', 'Pigtail đầu ra của bộ chia lỗi, phải hàn nối lại'),
    (109, 'FTI- Call bình thường', 'FTI- Sale xác nhận KHG có thực hiện cuộc gọi'),
    (110, 'Lỗi thiết bị', 'Lỏ dây LAN kết nối'),
    (111, 'Lỗi ngoại vi', 'Lỗi core lộ trên cáp'),
    (112, 'Lỗi thiết bị', 'Lỗi module quang'),
    (113, 'Mất điện diện rộng', 'Mất điện diện rộng'),
    (114, 'Lỗi thiết bị', 'Lỗi card RE'),
    (115, 'Lỗi ngoại vi', 'Đứt cáp'),
    (116, 'Lỗi app', 'Lỗi app'),
    (117, 'Lỗi bộ chia', 'Bộ chia hỏng, phải thay thế'),
    (118, 'Đứt cáp 8 core hàn 2 đầu', 'Đứt cáp phải do chập cháy'),
    (119, 'Coupler hỏng', 'Coupler hỏng'),
    (120, 'Đứt cáp 16 core hàn 2 đầu', 'Đứt cáp do thiên tai, thời tiết xấu (bắt khả kháng)'),
    (121, 'Lỗi thiết bị', 'Lỗi PON chip'),
    (122, 'Lỗi bộ chia', 'Pigtail đầu vào của bộ chia đứt gãy, phải hàn nối lại'),
    (123, 'Đứt cáp 12 core hàn 2 đầu', 'Đứt cáp do điện lực quy hoạch'),
    (124, 'Lỗi cảm biến', 'Nhân sự vào trạm bảo trì có KH'),
    (125, 'Đứt cáp 8 core hàn 2 đầu', 'Đứt cáp do thiên tai, thời tiết xấu (bắt khả kháng)'),
    (126, 'Coupler suy hao', 'Coupler suy hao'),
    (127, 'Đứt cáp 24 core hàn 2 đầu', 'Đứt cáp do điện lực quy hoạch'),
    (128, 'Đứt cáp 16 core hàn 2 đầu', 'Đứt cáp do côn trùng, chuột, sâu cắn'),
    (129, 'Đứt cáp 12 core hàn 2 đầu', 'Đứt cáp phải do xe kéo'),
    (130, 'Đứt cáp thuê bao', 'Bảo trì có kế hoạch'),
    (131, 'Lỗi thiết bị', 'Lỗi module PON'),
    (132, 'Automat accu đang ở trạng thái mở', 'Automat lỗi'),
    (133, 'Đứt cáp 8 core hàn 1 đầu', 'Đứt cáp phải do xe kéo'),
    (134, 'Bảo trì có kế hoạch', 'Bảo trì định kỳ POP'),
    (135, 'Đứt cáp 12 core hàn 2 đầu', 'Đứt cáp do thiên tai, thời tiết xấu (bắt khả kháng)'),
    (136, 'Kênh truyền hình HD', 'Nhảy source nhà đài'),
    (137, 'Logic', 'Lỗi cấu hình'),
    (138, 'Lỗi phần cứng', 'Lỗi tự thiết bị'),
    (139, 'Lỗi module', 'Module phát thấp'),
    (140, 'Lỗi logic', 'Lỗi bị tấn công DDoS'),
    (141, 'Đứt cáp 24 core hàn 2 đầu', 'Đứt cáp ngầm do công trường thi công, xe múc làm bể ống ngầm'),
    (142, 'Cảnh báo lỗi hệ thống lạnh', 'ACC đang hoạt động ở mode CRITICAL'),
    (143, 'Đứt cáp 8 core hàn 2 đầu', 'Đứt cáp do điện lực quy hoạch'),
    (144, 'Đứt cáp 24 core hàn 1 đầu', 'Đứt cáp do côn trùng, chuột, sâu cắn'),
    (145, 'Lỗi tập điểm', 'Mất trạm tập điểm'),
    (146, 'Lỗi logic', 'Lỗi hệ thống cảnh báo'),
    (147, 'Lỗi thiết bị', 'Lỗi module quang, thay module'),
    (148, 'Tác nhân bên ngoài', 'Do người thao tác'),
    (149, 'Lỗi phân đoạn uplink', 'Đứt cáp'),
    (150, 'Đứt cáp 12 core hàn 1 đầu', 'Đứt cáp do điện lực quy hoạch'),
    (151, 'Đứt cáp 12 core hàn 1 đầu', 'Đứt cáp do tỉa cây xanh'),
    (152, 'Chập cháy hộp', 'Chập cháy hộp'),
    (153, 'Ghi nhận các thay đổi thông tin của các cặp PID của luồng kênh', 'Lỗi source multicast'),
    (154, 'Automat accu đang ở trạng thái mở', 'Cảnh báo sai'),
    (155, 'Lỗi dây nhảy quang phải thay', 'Lỗi dây nhảy quang phải thay'),
    (156, 'Gập cáp', 'Gập core cáp tại măng xông không hàn nối lại'),
    (157, 'Cảnh báo phân đoạn access', 'Khu vực KHG bị mất điện'),
    (158, 'Lỗi core cáp', 'Lỗi cáp'),
    (159, 'Đứt cable 12 core hàn 2 đầu', 'Đứt cáp do điện lực quy hoạch'),
    (160, 'Lỗi logic', 'Traffic nghẽn qua fabric'),
    (161, 'Lỗi core đầu vào bộ chia cấp 1 tại tập điểm', 'Core cong gập trong tập điểm, phải hàn nối lại'),
    (162, 'Lỗi cấu hình ban đầu', 'Lỗi thiết kế, quy hoạch'),
    (163, 'Lỗi truyền dẫn', 'Lỗi tự thiết bị'),
    (164, 'Lỗi tập điểm', 'Tập điểm vỡ nát'),
    (165, 'Đứt cáp 16 core hàn 2 đầu', 'Đứt cáp ban đêm'),
    (166, 'Đứt cáp 24 core hàn 2 đầu', 'Đứt cáp do tỉa cây xanh'),
    (167, 'Lỗi core đầu vào bộ chia tại tập điểm', 'Mối hàn trong tập điểm suy hao, phải hàn lại'),
    (168, 'Đứt cable 24 core hàn 2 đầu', 'Đứt cáp do điện lực quy hoạch'),
    (169, 'Chưa xác định được nguyên nhân', 'Chưa xác định được nguyên nhân'),
    (170, 'Gập cáp', 'Gập cáp không hàn nối lại'),
    (171, 'Đứt cáp 8 core hàn 1 đầu', 'Đứt cáp do tỉa cây xanh'),
    (172, 'Đứt cáp 16 core hàn 2 đầu', 'Đứt cáp phải do xe kéo'),
    (173, 'Đứt cáp 8 core hàn 1 đầu', 'Đứt cáp do điện lực quy hoạch'),
    (174, 'Lỗi bộ chia', 'Mất trạm bộ chia'),
    (175, 'Lỗi module', 'Lỗi module'),
    (176, 'Đứt cáp 8 core hàn 2 đầu', 'Đứt cáp do côn trùng, chuột, sâu cắn'),
    (177, 'Lỗi thiết bị', 'Lỗi Core Cable'),
    (178, 'Lỗi phần cứng thiết bị', 'Lỗi port'),
    (179, 'Lỗi core dẫn tới bộ chia cấp 1', 'Lỗi core lộ trên cáp đồi được core'),
    (180, 'Lỗi kiểm tra ắc quy', 'Nguyên nhân khác'),
    (181, 'Đứt cáp 12 core hàn 2 đầu', 'Đứt cáp do côn trùng, chuột, sâu cắn'),
    (182, 'Đứt cáp 24 core hàn 2 đầu', 'Đứt cáp ngầm (thông thường)'),
    (183, 'SWITCH DOWN PORT', 'Tác nhân bên ngoài'),
    (184, 'Encoder', 'Lỗi hardware (CPU, RAM, HDD, Quạt)'),
    (185, 'Lỗi ngoại vi', 'Lỗi core cáp tại măng xông'),
    (186, 'Lỗi port', 'Bảo trì/theo dõi có kế hoạch'),
    (187, 'Không có thành phần video trong luồng kênh', 'Lỗi source multicast'),
    (188, 'Đứt cáp 8 core hàn 2 đầu', 'Đứt cáp phải do xe kéo'),
    (189, 'Bộ chia cấp 1 lỗi', 'Bộ chia hỏng, phải thay thế'),
    (190, 'Cảnh báo  máy phát điện', 'Nhiên liệu quá thấp'),
    (191, 'Đứt cáp 12 core hàn 1 đầu', 'Đứt cáp do côn trùng, chuột, sâu cắn'),
    (192, 'Mất điện lưới', 'Máy phát điện hỏng'),
    (193, 'Lỗi kênh, cáp', 'Lỗi dây nhảy nối DC, nhà trạm'),
    (194, 'Đứt cáp 12 core hàn 2 đầu', 'Đứt cáp phải do phá hoại'),
    (195, 'Đứt cáp 12 core hàn 2 đầu', 'Đứt cáp do đứt cắt (chuyển hướng được)'),
    (196, 'Lỗi kiểm tra ắc quy', 'Kết nối ắc quy không đảm bảo'),
    (197, 'Đứt cáp 24 core hàn 2 đầu', 'Đứt cáp phải do phá hoại'),
    (198, 'Lỗi core đầu vào bộ chia tại tập điểm', 'Lỗi core nhiệt, phải thay thế'),
    (199, 'Đứt cáp 8 core hàn 1 đầu', 'Tất cáp tại măng xông, phải hàn nối lại toàn bộ'),
    (200, 'Port Khách hàng', 'Khách hàng tắt thiết bị không sử dụng'),
    (201, 'Logic', 'Nguyên nhân khác'),
    (202, 'Đứt cáp 2 core hàn 2 đầu', 'Đứt cáp phải do chập cháy'),
    (203, 'Lỗi core cable', 'Bảo trì/theo dõi có kế hoạch'),
    (204, 'Lỗi coupler', 'Lỗi coupler'),
    (205, 'Lỗi măng xông', 'Mất trạm măng xông, phải thay thế'),
    (206, 'Lỗi logic', 'Hệ thống tự hoạt động trở lại')
]
REGIONS = [(1, 'MB'), (2, 'MN'), (3, "Other")]
STAFFS = [
    (1, 'Nguyen Minh Quan', 'QuanNM96@gmail.com'),
    (2, 'Le Van Manh', 'ManhLV6@gmail.com'),
    (3, 'Tran Thi Huong', 'HuongTT@gmail.com'),
    (4, 'Pham Van Tuan', 'TuanPV@gmail.com'),
    (5, 'Hoang Thi Lan', 'LanHT88@gmail.com'),
    (6, 'Dang Van Hung', 'HungDV@gmail.com'),
    (7, 'Do Thi Mai', 'MaiDT@gmail.com'),
    (8, 'Bui Quang Huy', 'HuyBQ@gmail.com'),
    (9, 'Ngo Thi Nga', 'NgaNT@gmail.com'),
    (10, 'Vu Van Thanh', 'ThanhVV@gmail.com'),
    (11, 'Mai Thi Phuong', 'PhuongMT@gmail.com'),
    (12, 'Truong Van Khoa', 'KhoaTV@gmail.com'),
    (13, 'Phan Thi Thao', 'ThaoPT@gmail.com'),
    (14, 'Ho Van Nam', 'NamHV@gmail.com'),
    (15, 'Ly Thi Cam', 'CamLT@gmail.com'),
    (16, 'Trinh Van An', 'AnTV@gmail.com'),
    (17, 'Lam Thi Hong', 'HongLT@gmail.com'),
    (18, 'Nghiem Van Son', 'SonNV@gmail.com'),
    (19, 'Ngo Quang Trung', 'TrungNQ@gmail.com'),
    (20, 'Cao Thi Thu', 'ThuCT@gmail.com')
]
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

# ------------------------------ Disable constraints ------------------------------
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
    logger.info("Cleaning old data from business tables...")
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
        cursor.execute("INSERT INTO dim_issue_names (id, name, issue_group_id) VALUES (:1, :2, :3)", [inid, inname, ingid])
    for lid, lname in LOCATIONS:
        cursor.execute(f"INSERT INTO dim_locations (id, name) VALUES ({lid}, {sql_quote(lname)})")
    for pid, pname in POPS:
        cursor.execute(f"INSERT INTO dim_pops (id, name) VALUES ({pid}, {sql_quote(pname)})")
    for puid, puname in PROCESSING_UNITS:
        cursor.execute(f"INSERT INTO dim_processing_units (id, name) VALUES ({puid}, {sql_quote(puname)})")
    for qid, qname in QUEUES:
        cursor.execute(f"INSERT INTO dim_queues (id, name) VALUES ({qid}, {sql_quote(qname)})")
    for rid, rname, rdetail in REASONS:
        cursor.execute("INSERT INTO dim_reasons (id, name, detail) VALUES (:1, :2, :3)", [rid, rname, rdetail])
    for regid, regname in REGIONS:
        cursor.execute(f"INSERT INTO dim_regions (id, name) VALUES ({regid}, {sql_quote(regname)})")
    for sid, sname, smail in STAFFS:
        cursor.execute(f"INSERT INTO dim_staffs (id, name, mail) VALUES ({sid}, {sql_quote(sname)}, {sql_quote(smail)})")
    cursor.connection.commit()
    logger.info("DIM inserted.")

# ------------------------------ Generate FACT ------------------------------
def generate_fact_data(num_tickets, cursor):
    logger.info(f"Generating {num_tickets} tickets...")

    # Lấy tất cả ID từ chính các danh sách DIM
    branch_ids         = [b[0] for b in BRANCHES]
    device_type_ids    = [d[0] for d in DEVICE_TYPES]
    device_ids         = list(range(1, len(DEVICE_NAMES)+1))
    action_ids         = [a[0] for a in HT_ACTIONS]
    customer_type_ids  = [c[0] for c in CUSTOMER_TYPES]
    queue_type_ids     = [q[0] for q in QUEUE_TYPES]
    service_type_ids   = [s[0] for s in SERVICE_TYPES]
    step_ids           = [s[0] for s in HT_STEPS]
    support_type_ids   = [s[0] for s in SUPPORT_TYPES]
    interface_ids      = list(range(1, len(INTERFACE_NAMES)+1))
    issue_name_ids     = [i[0] for i in ISSUE_NAMES]
    location_ids       = [l[0] for l in LOCATIONS]
    pop_ids            = [p[0] for p in POPS]
    processing_unit_ids= [u[0] for u in PROCESSING_UNITS]
    queue_ids          = [q[0] for q in QUEUES]
    reason_ids         = [r[0] for r in REASONS]
    region_ids         = [r[0] for r in REGIONS]
    staff_ids          = [s[0] for s in STAFFS]

    # Thời gian: 2 tháng trước -> hiện tại
    now = datetime.datetime.now()
    start_ref = now - datetime.timedelta(days=60)
    end_ref = now

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

        # fact_ticket_time
        issue_date = random_date(start_ref, end_ref)
        inprogress_date = issue_date + datetime.timedelta(minutes=random.randint(5, 60))
        resolved_date = inprogress_date + datetime.timedelta(minutes=random.randint(30, 300))
        closed_date = resolved_date + datetime.timedelta(minutes=random.randint(0, 60))
        estimate_date = issue_date + datetime.timedelta(hours=random.randint(1, 8))
        expect_end_date = resolved_date + datetime.timedelta(minutes=random.randint(-30, 30))
        required_date = resolved_date + datetime.timedelta(minutes=random.randint(-60, 60))
        full_data_date = inprogress_date + datetime.timedelta(minutes=random.randint(10, 120))
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

        # fact_ticket_creation
        created_datetime = issue_date + datetime.timedelta(minutes=random.randint(0, 15))
        sc_creation_method = random.choice(['SC tạo auto', 'SC tạo manual (SC tạo tay)'])
        sc_creation_time = round(random.uniform(0.1, 5.0), 1)
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

        # fact_ticket_process
        process_name = f"Process_{code}"
        process_staff_id = random.choice(staff_ids)
        processing_unit_id = random.choice(processing_unit_ids)
        queue_create_id = random.choice(queue_ids)
        queue_process_id = random.choice(queue_ids)
        change_queue_time = random.randint(5, 120)
        actual_time = random.randint(10, 300)
        cursor.execute(f"""
            INSERT INTO fact_ticket_process (
                id, process_name, process_staff_id, processing_unit_id,
                queue_create_id, queue_process_id, change_queue_time, actual_time
            ) VALUES (
                {i}, {sql_quote(process_name)}, {process_staff_id}, {processing_unit_id},
                {queue_create_id}, {queue_process_id}, {change_queue_time}, {actual_time}
            )
        """)

        # fact_tickets
        over_time = random.choice(['Đúng hạn', 'Trễ hạn', 'RESOLVED - Đúng hạn'])
        reason_id = random.choice(reason_ids)
        priority = random_priority()
        ticket_status = random_ticket_status()
        issue_name_id = random.choice(issue_name_ids)
        required_time = random.randint(30, 480)
        cursor.execute(f"""
            INSERT INTO fact_tickets (
                id, code, process_id, time_id, creation_id, closed_id,
                over_time, reason_id, priority, ticket_status, issue_name_id, required_time
            ) VALUES (
                {i}, {sql_quote(code)}, {i}, {i}, {i}, {i},
                {sql_quote(over_time)}, {reason_id}, {priority}, {sql_quote(ticket_status)},
                {issue_name_id}, {required_time}
            )
        """)

        # fact_sc_tickets hoặc fact_ht_tickets
        if is_sc:
            cus_qty = random.randint(0, 500) if random.random() < 0.5 else 0
            device_type_id = random.choice(device_type_ids)
            suspend_time = random.randint(30, 600) if random.random() < 0.8 else 0
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
                    {i}, {i}, {cus_qty}, {device_type_id}, {suspend_time},
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
            rejection_count = random.randint(0, 3)
            response_count = random.randint(1, 5)
            sla_violation_count = str(random.randint(0, 3)) if random.random() < 0.7 else 'Không'
            priority_handling_desc = random_boolean()
            is_escalated = random_boolean()
            scenario_confirmed = random_boolean()
            ticket_age_days = round(random.uniform(0.5, 30.0), 1)
            cursor.execute(f"""
                INSERT INTO fact_ht_tickets (
                    ticket_id, title, commitment_desc, required, is_ticket_open,
                    sos_ticket_flag, customer_type_id, service_type_id, support_type_id,
                    step_id, deadline_status, rejection_count, response_count,
                    sla_violation_count, priority_handling_desc, is_escalated,
                    scenario_confirmed, ticket_age_days
                ) VALUES (
                    {i}, {sql_quote(title)}, {sql_quote(commitment_desc)}, {sql_quote(required)},
                    {sql_quote(is_ticket_open)}, {sql_quote(sos_ticket_flag)}, {customer_type_id},
                    {service_type_id}, {support_type_id}, {step_id}, {sql_quote(deadline_status)},
                    {rejection_count}, {response_count}, {sql_quote(sla_violation_count)},
                    {sql_quote(priority_handling_desc)}, {sql_quote(is_escalated)},
                    {sql_quote(scenario_confirmed)}, {ticket_age_days}
                )
            """)

        # Các bảng liên kết
        # ticket_branch
        chosen_branches = random.sample(branch_ids, k=random.randint(1, min(3, len(branch_ids))))
        for b in chosen_branches:
            cursor.execute(f"INSERT INTO ticket_branch (ticket_id, branch_id) VALUES ({i}, {b})")

        # ticket_device
        if random.random() < 0.7:
            chosen_devices = random.sample(device_ids, k=random.randint(1, min(2, len(device_ids))))
            for d in chosen_devices:
                cursor.execute(f"INSERT INTO ticket_device (ticket_id, device_id) VALUES ({i}, {d})")

        # ticket_interface
        if random.random() < 0.7:
            chosen_interfaces = random.sample(interface_ids, k=random.randint(1, min(2, len(interface_ids))))
            for iface in chosen_interfaces:
                cursor.execute(f"INSERT INTO ticket_interface (ticket_id, interface_id) VALUES ({i}, {iface})")

        # ticket_location
        chosen_locs = random.sample(location_ids, k=random.randint(1, min(2, len(location_ids))))
        for loc in chosen_locs:
            cursor.execute(f"INSERT INTO ticket_location (ticket_id, location_id) VALUES ({i}, {loc})")

        # ticket_pop
        chosen_pops = random.sample(pop_ids, k=random.randint(1, min(2, len(pop_ids))))
        for p in chosen_pops:
            cursor.execute(f"INSERT INTO ticket_pop (ticket_id, pop_id) VALUES ({i}, {p})")

        # ht_ticket_history (chỉ cho HT)
        if not is_sc:
            for j in range(random.randint(2, 5)):
                hist_desc = f"History {j+1} for {code}"
                updated_date = inprogress_date + datetime.timedelta(minutes=random.randint(0, 60*(j+1)))
                hist_status = random.choice(['New','Inprogress','Resolved','Closed','Rejected','CREATE','Pending'])
                action_id = random.choice(action_ids)
                staff_id = random.choice(staff_ids)
                step_id = random.choice(step_ids)
                queue_type_id = random.choice(queue_type_ids)
                created_date = updated_date - datetime.timedelta(minutes=random.randint(1, 30))
                updated_queue_id = random.choice(queue_ids)
                response_time = round(random.uniform(0.5, 60.0), 2)
                commitment_desc = random_boolean()
                cursor.execute(f"""
                    INSERT INTO ht_ticket_history (
                        description, updated_date, ht_ticket_status, ht_ticket_id,
                        action_id, staff_id, step_id, queue_type_id, created_date,
                        updated_queue_id, response_time_minutes, commitment_description
                    ) VALUES (
                        {sql_quote(hist_desc)}, {sql_quote(updated_date)}, {sql_quote(hist_status)}, {i},
                        {action_id}, {staff_id}, {step_id}, {queue_type_id}, {sql_quote(created_date)},
                        {updated_queue_id}, {response_time}, {sql_quote(commitment_desc)}
                    )
                """)

        if i % 100 == 0:
            cursor.connection.commit()
            logger.info(f"Committed {i} tickets")

    cursor.connection.commit()
    logger.info(f"Finished {num_tickets} tickets.")
import array
def update_examples_embeddings(cursor):
    logger.info("Bắt đầu cập nhật embedding cho bảng EXAMPLES...")
    cursor.execute("SELECT rowid, question FROM examples WHERE emb IS NULL FOR UPDATE")
    rows = cursor.fetchall()
    total = len(rows)
    logger.info(f"Số dòng cần cập nhật: {total}")

    if total == 0:
        logger.info("Không có dòng nào cần cập nhật.")
        return

    update_sql = "UPDATE examples SET emb = :1 WHERE rowid = :2"
    count = 0

    for rid, question in rows:
        try:
            text = question.read() if hasattr(question, 'read') else str(question)

            emb_list = get_embedding(text)  # list float

            cursor.execute(update_sql, [emb_list, rid])

            count += 1
            logger.debug(f"Đã cập nhật dòng {count}/{total}")

            # 🚀 commit batch cho nhanh
            if count % 50 == 0:
                cursor.connection.commit()

        except Exception as e:
            logger.error(f"Lỗi khi cập nhật dòng {rid}: {e}")
            continue

    cursor.connection.commit()
    logger.info(f"Hoàn tất: đã cập nhật {count}/{total} dòng.")


def update_schema_embeddings(cursor):
    logger.info("Tạo embedding cho schema (table_embeddings, column_embeddings)...")

    cursor.execute("DELETE FROM table_embeddings")
    cursor.execute("DELETE FROM column_embeddings")
    logger.info("Đã xóa dữ liệu cũ.")

    # ---------- Table embedding ----------
    cursor.execute("""
        SELECT t.table_name, c.comments
        FROM user_tables t
        LEFT JOIN user_tab_comments c ON t.table_name = c.table_name
        WHERE t.table_name NOT IN (
            'EXAMPLES', 'SESSIONS', 'CHAT_HISTORY', 'KEYWORDS', 'UNIQUE_VALUE_COLUMNS',
            'PLUS_VALUE_COLUMNS', 'COLUMN_EMBEDDINGS', 'TABLE_EMBEDDINGS',
            'REDO_DB', 'REDO_LOG', 'HELP', 'SQLPLUS_PRODUCT_PROFILE'
        )
        AND t.table_name NOT LIKE 'MVIEW$_%'
        AND t.table_name NOT LIKE 'MVIEW$_ADV%'
        AND t.table_name NOT LIKE 'AQ$%'
        AND t.table_name NOT LIKE 'AQ$_%'
        AND t.table_name NOT LIKE 'SCHEDULER$_%'
        AND t.table_name NOT LIKE 'OL$%'
        AND t.table_name NOT LIKE 'DR$%'
        AND t.table_name NOT LIKE 'BIN$%'
        AND t.table_name NOT LIKE 'SYS_%'
    """)
    tables = cursor.fetchall()
    logger.info(f"Số bảng cần xử lý: {len(tables)}")

    insert_table = "INSERT INTO table_embeddings (table_name, emb) VALUES (:1, :2)"

    for table_name, comment in tables:
        text = comment if comment else table_name
        if hasattr(text, 'read'):
            text = text.read()
        
        text = text.split("|")[0]
        text = text.strip("UNIQUE_VALUES.").strip("UNIQUE+VALUES.")
        emb_list = get_embedding(text)
        cursor.execute(insert_table, [table_name, emb_list])

    # ---------- Column embedding ----------
    cursor.execute("""
        SELECT col.table_name, col.column_name, cc.comments
        FROM user_tab_columns col
        LEFT JOIN user_col_comments cc
            ON col.table_name = cc.table_name AND col.column_name = cc.column_name
        WHERE col.table_name NOT IN (
            'EXAMPLES', 'SESSIONS', 'CHAT_HISTORY', 'KEYWORDS', 'UNIQUE_VALUE_COLUMNS',
            'PLUS_VALUE_COLUMNS', 'COLUMN_EMBEDDINGS', 'TABLE_EMBEDDINGS',
            'REDO_DB', 'REDO_LOG', 'HELP', 'SQLPLUS_PRODUCT_PROFILE'
        )
        AND t.table_name NOT LIKE 'MVIEW$_%'
        AND t.table_name NOT LIKE 'MVIEW$_ADV%'
        AND t.table_name NOT LIKE 'AQ$%'
        AND t.table_name NOT LIKE 'AQ$_%'
        AND t.table_name NOT LIKE 'SCHEDULER$_%'
        AND t.table_name NOT LIKE 'OL$%'
        AND t.table_name NOT LIKE 'DR$%'
        AND t.table_name NOT LIKE 'BIN$%'
        AND t.table_name NOT LIKE 'SYS_%'
    """)
    columns = cursor.fetchall()
    logger.info(f"Số cột cần xử lý: {len(columns)}")

    insert_col = "INSERT INTO column_embeddings (table_name, column_name, emb) VALUES (:1, :2, :3)"

    for table_name, column_name, comment in columns:
        text = comment if comment else column_name
        if hasattr(text, 'read'):
            text = text.read()
        text = text.split("|")[0]
        text = text.strip("UNIQUE_VALUES.").strip("UNIQUE+VALUES.")
        emb_list = get_embedding(text)
        cursor.execute(insert_col, [table_name, column_name, emb_list])

    cursor.connection.commit()
    logger.info("Hoàn tất tạo embedding cho schema.")

# ------------------------------ Main ------------------------------
def main():
    parser = argparse.ArgumentParser(description="Generate fake data")
    parser.add_argument("--num_tickets", type=int, default=500, help="Number of tickets")
    parser.add_argument("--user", default="system", help="Oracle username")
    parser.add_argument("--password", default="oracle", help="Oracle password")
    parser.add_argument("--dsn", default="localhost:1521/XEPDB1", help="Oracle DSN")
    args = parser.parse_args()

    try:
        connection = oracledb.connect(user=args.user, password=args.password, dsn=args.dsn)
        cursor = connection.cursor()
        logger.info("Connected to Oracle")

        cleanup_data(cursor)
        disable_check_constraints(cursor)
        insert_dimensions(cursor)
        generate_fact_data(args.num_tickets, cursor)
        update_examples_embeddings(cursor)
        update_schema_embeddings(cursor)

        cursor.close()
        connection.close()
        logger.info("Done.")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()