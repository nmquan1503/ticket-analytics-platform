const LOCATION_BRANCH_MAP = {
  '01. Hà Nội': ['Hà Nội 1', 'Hà Nội 10'],
  '06. Khánh Hòa': ['Khánh Hòa 2'],
  '04. Đà Nẵng': ['Đà Nẵng'],
  '12. Hồ Chí Minh': ['Hồ Chí Minh 5'],
  '15. Tây Nam Bộ': ['Cần Thơ'],
  '02. Đông Bắc Bộ': ['Hải Phòng', 'Hà Giang']
};

const LOCATIONS = Object.keys(LOCATION_BRANCH_MAP);
const BRANCHES = Object.values(LOCATION_BRANCH_MAP).flat();
const STAFFS = ['Nguyễn Minh Quân', 'Lê Văn Mạnh', 'Trần Thị Thảo', 'Phạm Hoàng Nam', 'Đỗ Trung Kiên', 'Vũ Hải Yến'];
const ISSUE_GROUPS = ['Hệ thống Access', 'Core IP', 'Truyền dẫn', 'Nguồn điện', 'Hệ thống OLT'];
const REASONS = ['Đứt cáp quang', 'Nhiễu tín hiệu', 'Mất điện lưới', 'Lỗi phần cứng', 'Cảnh báo tự động', 'Quá tải thiết bị'];
const QUEUES = ['SCC (Vận hành mạng)', 'INF-BTHT (Bảo trì nội bộ)', 'CSOC-IT (An toàn TT)', 'NOC (Core Network)', 'CNO (Kỹ thuật VN)'];
const CUSTOMER_TYPES = ['Khách hàng Doanh nghiệp', 'Hosting', 'Voice Doanh Nghiệp', 'Tập đoàn', 'Khách cá nhân VIP'];
const SERVICE_TYPES = ['FTQ - Hỗ trợ quy trình', 'DVKH - Nghiệp vụ', 'Triển khai bảo trì', 'Xử lý phản ánh'];

export const PRIORITIES = [1, 2, 3, 4, 5, 6];

export const STATUSES = [
  { name: 'New', color: '#6366f1' },       // Indigo
  { name: 'Inprogress', color: '#f59e0b' }, // Amber
  { name: 'Resolved', color: '#10b981' },   // Emerald
  { name: 'Closed', color: '#64748b' }      // Slate
];

// Generate mock tickets
const generateMockTickets = (mode) => {
  return Array.from({ length: 150 }).map((_, i) => {
    const statusObj = STATUSES[Math.floor(Math.random() * STATUSES.length)];
    const createdDate = new Date();
    createdDate.setDate(createdDate.getDate() - Math.floor(Math.random() * 365)); 

    const location = LOCATIONS[Math.floor(Math.random() * LOCATIONS.length)];
    const availableBranches = LOCATION_BRANCH_MAP[location];
    const branch = availableBranches[Math.floor(Math.random() * availableBranches.length)];
    
    return {
      ticket_id: i + 1,
      code: `${mode}${25102500000 + i}`,
      status: statusObj.name,
      branch_name: branch,
      location: location,
      created_date: createdDate.toISOString().split('T')[0],
      cus_qty: Math.floor(Math.random() * 500),
      // Giả lập logic: thời gian thao tác (actual) luôn thấp hơn thời gian gián đoạn ròng (suspend)
      actual_time: Math.floor(Math.random() * 180), // minutes
      suspend_time: Math.floor(Math.random() * 180) + 30, // Khách hàng luôn chết mạng lâu hơn thao tác xử lý

      staff_name: STAFFS[Math.floor(Math.random() * STAFFS.length)],
      sla_status: Math.random() > 0.2 ? 'Đúng hạn' : 'Quá hạn',
      type: mode, // SC or HT

      // Analytics Fields (Phase 1)
      priority: PRIORITIES[Math.floor(Math.random() * PRIORITIES.length)],
      sos_ticket_flag: Math.random() > 0.85 ? 'Có' : 'Không',
      reason: REASONS[Math.floor(Math.random() * REASONS.length)],
      issue_group: ISSUE_GROUPS[Math.floor(Math.random() * ISSUE_GROUPS.length)],

      // Deep Dive Fields (Phase 2 based on Full SQL Schema)
      sc_type: Math.random() > 0.3 ? 'Chủ quan' : 'Khách quan', // Con người vs Bất khả kháng
      sc_natural_disaster: Math.random() > 0.9 ? 'Có' : 'Không', // 10% do bão lũ
      sc_creation_method: Math.random() > 0.4 ? 'SC tạo auto' : 'SC tạo manual (SC tạo tay)',
      sc_creation_time: parseFloat((Math.random() * 15).toFixed(1)), // Phút phản xạ báo cáp
      queue_process: QUEUES[Math.floor(Math.random() * QUEUES.length)],

      // Bottleneck Analytics
      rejection_count: Math.random() > 0.7 ? Math.floor(Math.random() * 4) + 1 : 0, // Số lần bị đá bóng sang luồng khác
      sla_violation_count: Math.random() > 0.8 ? Math.floor(Math.random() * 3) + 1 : 0, // Số lần tái vi phạm
      change_queue_time: Math.floor(Math.random() * 120), // Thời gian đợi luân chuyển Queue (phút)
      ticket_age_days: parseFloat((Math.random() * 30).toFixed(1)), // Số ngày tồn kho (nợ xấu)

      // HT Specific Analytics
      customer_type: CUSTOMER_TYPES[Math.floor(Math.random() * CUSTOMER_TYPES.length)],
      service_type: SERVICE_TYPES[Math.floor(Math.random() * SERVICE_TYPES.length)],
      is_escalated: Math.random() > 0.85 ? 'Có' : 'Không', // Tỷ lệ buộc phải vượt tuyến
    };
  });
};

export const mockSCData = generateMockTickets('SC');
export const mockHTData = generateMockTickets('HT');
export { BRANCHES, LOCATIONS, STAFFS, ISSUE_GROUPS, REASONS, QUEUES, LOCATION_BRANCH_MAP };
