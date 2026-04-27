// Simple node test for mock data logic
const BRANCHES = ['Hà Nội 1', 'Hà Nội 10', 'Khánh Hòa 2', 'Đà Nẵng', 'Hồ Chí Minh 5', 'Cần Thơ', 'Hải Phòng'];
const REGIONS = ['Miền Bắc', 'Miền Trung', 'Miền Nam'];
const STAFFS = ['Nguyễn Minh Quân', 'Lê Văn Mạnh', 'Trần Thị Thảo', 'Phạm Hoàng Nam', 'Đỗ Trung Kiên', 'Vũ Hải Yến'];

const STATUSES = [
  { name: 'New', color: '#6366f1' },
  { name: 'Inprogress', color: '#f59e0b' },
  { name: 'Resolved', color: '#10b981' },
  { name: 'Closed', color: '#64748b' }
];

const generateMockTickets = (mode) => {
  return Array.from({ length: 100 }).map((_, i) => {
    const statusObj = STATUSES[Math.floor(Math.random() * STATUSES.length)];
    const createdDate = new Date();
    createdDate.setDate(createdDate.getDate() - Math.floor(Math.random() * 30));
    
    return {
      ticket_id: i + 1,
      code: `${mode}${25102500000 + i}`,
      status: statusObj.name,
      branch_name: BRANCHES[Math.floor(Math.random() * BRANCHES.length)],
      region: REGIONS[Math.floor(Math.random() * REGIONS.length)],
      created_date: createdDate.toISOString().split('T')[0],
      cus_qty: Math.floor(Math.random() * 500),
      actual_time: Math.floor(Math.random() * 180),
      staff_name: STAFFS[Math.floor(Math.random() * STAFFS.length)],
      sla_status: Math.random() > 0.2 ? 'Đúng hạn' : 'Quá hạn',
      type: mode
    };
  });
};

const data = generateMockTickets('SC');
console.log('--- TEST DATA GENERATION (SC) ---');
console.log('Total Tickets:', data.length);
console.log('First 3 tickets preview:');
console.table(data.slice(0, 3).map(t => ({ 
  ID: t.code, 
  Status: t.status, 
  Region: t.region, 
  Branch: t.branch_name, 
  Cus: t.cus_qty, 
  Time: t.actual_time 
})));

const impactedCustomers = data.reduce((acc, curr) => acc + curr.cus_qty, 0);
const slaCorrect = data.filter(t => t.sla_status === 'Đúng hạn').length;
const slaRate = (slaCorrect / data.length * 100).toFixed(1);
const avgTime = Math.round(data.reduce((acc, curr) => acc + curr.actual_time, 0) / data.length);

console.log('\n--- KPI CALCULATIONS ---');
console.log('Total Impacted Customers:', impactedCustomers);
console.log('SLA Compliance Rate:', slaRate + '%');
console.log('Avg Processing Time:', avgTime + ' mins');

const statusDist = {};
data.forEach(t => statusDist[t.status] = (statusDist[t.status] || 0) + 1);
console.log('\n--- STATUS DISTRIBUTION ---');
console.table(statusDist);
