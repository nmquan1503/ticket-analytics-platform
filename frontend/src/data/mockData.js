const BRANCHES = ['Hà Nội 1', 'Hà Nội 10', 'Khánh Hòa 2', 'Đà Nẵng', 'Hồ Chí Minh 5', 'Cần Thơ', 'Hải Phòng', 'Hà Giang'];
const LOCATIONS = ['01. Hà Nội', '06. Khánh Hòa', '04. Đà Nẵng', '12. Hồ Chí Minh', '15. Tây Nam Bộ', '02. Đông Bắc Bộ'];
const STAFFS = ['Nguyễn Minh Quân', 'Lê Văn Mạnh', 'Trần Thị Thảo', 'Phạm Hoàng Nam', 'Đỗ Trung Kiên', 'Vũ Hải Yến'];
const ISSUE_GROUPS = ['Hệ thống Access', 'Core IP', 'Truyền dẫn', 'Nguồn điện', 'Hệ thống OLT'];
const REASONS = ['Đứt cáp quang', 'Nhiễu tín hiệu', 'Mất điện lưới', 'Lỗi phần cứng', 'Cảnh báo tự động', 'Quá tải thiết bị'];

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
    createdDate.setDate(createdDate.getDate() - Math.floor(Math.random() * 45)); // Generate up to 45 days ago
    
    return {
      ticket_id: i + 1,
      code: `${mode}${25102500000 + i}`,
      status: statusObj.name,
      branch_name: BRANCHES[Math.floor(Math.random() * BRANCHES.length)],
      location: LOCATIONS[Math.floor(Math.random() * LOCATIONS.length)],
      created_date: createdDate.toISOString().split('T')[0],
      cus_qty: Math.floor(Math.random() * 500),
      actual_time: Math.floor(Math.random() * 180), // minutes
      staff_name: STAFFS[Math.floor(Math.random() * STAFFS.length)],
      sla_status: Math.random() > 0.2 ? 'Đúng hạn' : 'Quá hạn',
      type: mode, // SC or HT
      
      // New Analytics Fields based on schema analysis
      priority: PRIORITIES[Math.floor(Math.random() * PRIORITIES.length)],
      sos_ticket_flag: Math.random() > 0.85 ? 'Có' : 'Không', // 15% SOS rate
      reason: REASONS[Math.floor(Math.random() * REASONS.length)],
      issue_group: ISSUE_GROUPS[Math.floor(Math.random() * ISSUE_GROUPS.length)],
    };
  });
};

export const mockSCData = generateMockTickets('SC');
export const mockHTData = generateMockTickets('HT');
export { BRANCHES, LOCATIONS, STAFFS, ISSUE_GROUPS, REASONS };
