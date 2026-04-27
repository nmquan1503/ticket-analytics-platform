import React, { useState, useMemo } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
  PieChart, Pie, Cell, AreaChart, Area 
} from 'recharts';
import { 
  Ticket, Users, Clock, Zap, Filter, Calendar, MapPin, 
  Briefcase, ChevronDown, User, Activity, AlertTriangle, Flame
} from 'lucide-react';

// Components
import KPICard from '../components/KPICard';
import ChartCard from '../components/ChartCard';
import MultiSelect from '../components/MultiSelect';

// Data
import { mockSCData, mockHTData, STATUSES, LOCATIONS, BRANCHES, PRIORITIES } from '../data/mockData';

export default function Dashboard() {
  const [viewMode, setViewMode] = useState('SC'); // 'SC' or 'HT'
  
  // Real Filter States (Multi-select uses arrays now)
  const [dateRange, setDateRange] = useState('30'); // '7' or '30'
  const [locationFilter, setLocationFilter] = useState([]);
  const [branchFilter, setBranchFilter] = useState([]);
  const [priorityFilter, setPriorityFilter] = useState([]);
  
  // Filtered Data Logic
  const data = useMemo(() => {
    const rawData = viewMode === 'SC' ? mockSCData : mockHTData;
    
    return rawData.filter(t => {
      // 1. Location Filter (Array includes)
      if (locationFilter.length > 0 && !locationFilter.includes(t.location)) return false;
      
      // 2. Branch Filter (Array includes)
      if (branchFilter.length > 0 && !branchFilter.includes(t.branch_name)) return false;
      
      // 3. Priority Filter (Array includes)
      if (priorityFilter.length > 0 && !priorityFilter.includes(t.priority)) return false;
      
      // 3. Date Range Filter
      const tDate = new Date(t.created_date);
      const now = new Date();
      if (dateRange === '7') {
        const past = new Date();
        past.setDate(now.getDate() - 7);
        if (tDate < past) return false;
      } else if (dateRange === '30') {
        const past = new Date();
        past.setDate(now.getDate() - 30);
        if (tDate < past) return false;
      }
      return true;
    });
  }, [viewMode, locationFilter, branchFilter, dateRange]);

  // KPI Calculations
  const stats = useMemo(() => {
    const total = data.length;
    const impactedCustomers = data.reduce((acc, curr) => acc + curr.cus_qty, 0);
    const slaCorrect = data.filter(t => t.sla_status === 'Đúng hạn').length;
    const slaRate = total > 0 ? ((slaCorrect / total) * 100).toFixed(1) : 0;
    const avgTime = total > 0 ? Math.round(data.reduce((acc, curr) => acc + curr.actual_time, 0) / total) : 0;
    const sosCount = data.filter(t => t.sos_ticket_flag === 'Có').length;
    const criticalCount = data.filter(t => t.priority >= 5).length;

    return { total, impactedCustomers, slaRate, avgTime, sosCount, criticalCount };
  }, [data]);

  // Chart Data calculations... (Same as before but using the separate data)
  const statusData = useMemo(() => {
    return STATUSES.map(s => ({
      name: s.name,
      value: data.filter(t => t.status === s.name).length,
      color: s.color
    }));
  }, [data]);

  const trendData = useMemo(() => {
    const dateMap = {};
    data.forEach(t => {
      dateMap[t.created_date] = (dateMap[t.created_date] || 0) + 1;
    });
    return Object.entries(dateMap)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => new Date(a.date) - new Date(b.date));
  }, [data]);

  const branchData = useMemo(() => {
    const branchMap = {};
    data.forEach(t => {
      branchMap[t.branch_name] = (branchMap[t.branch_name] || 0) + 1;
    });
    return Object.entries(branchMap)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5);
  }, [data]);

  const staffData = useMemo(() => {
    const staffMap = {};
    data.forEach(t => {
      staffMap[t.staff_name] = (staffMap[t.staff_name] || 0) + 1;
    });
    return Object.entries(staffMap)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5);
  }, [data]);

  // Top Reasons
  const topReasons = useMemo(() => {
    const counts = {};
    data.forEach(t => counts[t.reason] = (counts[t.reason] || 0) + 1);
    return Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,5).map(i => ({ name: i[0], value: i[1] }));
  }, [data]);
  
  // Issue Group Distribution
  const groupData = useMemo(() => {
    const counts = {};
    data.forEach(t => counts[t.issue_group] = (counts[t.issue_group] || 0) + 1);
    const COLORS = ['#ef4444', '#f97316', '#f59e0b', '#10b981', '#3b82f6'];
    return Object.entries(counts).sort((a,b)=>b[1]-a[1]).map((i, idx) => ({ name: i[0], value: i[1], color: COLORS[idx % COLORS.length] }));
  }, [data]);

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8 font-sans text-slate-900">
      <header className="max-w-7xl mx-auto mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">Dashboard Quản lý Ticket</h1>
            <p className="text-gray-500 mt-1">Phân tích dữ liệu vận hành hệ thống {viewMode}</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center bg-white p-1 rounded-xl shadow-sm border border-gray-100">
              <button 
                onClick={() => setViewMode('SC')}
                className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${viewMode === 'SC' ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-600 hover:bg-gray-50'}`}
              >
                Sự Cố (SC)
              </button>
              <button 
                onClick={() => setViewMode('HT')}
                className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${viewMode === 'HT' ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-600 hover:bg-gray-50'}`}
              >
                Hỗ Trợ (HT)
              </button>
            </div>
            <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 border-2 border-white shadow-sm ring-2 ring-indigo-50">
              <User size={20} />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-white rounded-2xl shadow-sm border border-gray-100">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider ml-1">Thời gian</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
              <select 
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="pl-10 pr-4 py-2.5 w-full bg-gray-50 border-none rounded-xl text-sm font-medium appearance-none select-none cursor-pointer hover:bg-gray-100 transition-colors"
                style={{ WebkitAppearance: 'none', MozAppearance: 'none' }}
              >
                <option value="30">30 ngày gần nhất</option>
                <option value="7">7 ngày gần nhất</option>
                <option value="all">Tất cả thời gian</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" size={16} />
            </div>
          </div>

          <div className="flex flex-col gap-1.5 x-40">
            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider ml-1">Thời gian</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
              <select 
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="pl-10 pr-4 py-2.5 w-full bg-gray-50 border-none rounded-xl text-sm font-medium appearance-none select-none cursor-pointer hover:bg-gray-100 transition-colors"
                style={{ WebkitAppearance: 'none', MozAppearance: 'none' }}
              >
                <option value="30">30 ngày gần nhất</option>
                <option value="7">7 ngày gần nhất</option>
                <option value="all">Tất cả thời gian</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" size={16} />
            </div>
          </div>

          <div className="flex flex-col gap-1.5 z-40">
            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider ml-1">Khu vực (dim_locations)</label>
            <MultiSelect
              options={LOCATIONS}
              selected={locationFilter}
              onChange={setLocationFilter}
              placeholder="Chọn khu vực..."
              icon={MapPin}
            />
          </div>

          <div className="flex flex-col gap-1.5 z-30">
            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider ml-1">Chi nhánh (dim_branches)</label>
            <MultiSelect
              options={BRANCHES}
              selected={branchFilter}
              onChange={setBranchFilter}
              placeholder="Chọn chi nhánh..."
              icon={Briefcase}
            />
          </div>
          
          <div className="flex flex-col gap-1.5 z-20">
            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider ml-1">Mức ưu tiên</label>
            <MultiSelect
              options={PRIORITIES}
              selected={priorityFilter}
              onChange={setPriorityFilter}
              placeholder="Chọn mức độ..."
              icon={AlertTriangle}
            />
          </div>

          <div className="flex items-end">
            <button 
              onClick={() => {
                setDateRange('30');
                setLocationFilter([]);
                setBranchFilter([]);
                setPriorityFilter([]);
              }}
              className="w-full py-2.5 bg-gray-900 text-white rounded-xl text-sm font-bold flex items-center justify-center gap-2 hover:bg-gray-800 transition-colors shadow-sm active:scale-95"
            >
              <Filter size={18} />
              Xóa bộ lọc
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto space-y-6">
        {/* SOS Alerts Banner */}
        {(stats.sosCount > 0 || stats.criticalCount > 0) && (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-4 mb-6 flex items-center justify-between text-red-600 animate-pulse-slow shadow-sm">
            <div className="flex items-center gap-4">
              <div className="p-2 bg-red-100 rounded-full">
                <AlertTriangle size={24} className="text-red-500" />
              </div>
              <div>
                <h3 className="font-bold text-lg">Cảnh báo Điểm nóng!</h3>
                <p className="text-sm font-medium text-gray-700">
                  Hiện có <strong className="text-red-600">{stats.sosCount} vé SOS</strong> và <strong className="text-red-600">{stats.criticalCount} vé Vượt mức khẩn cấp (P5-P6)</strong> đang treo trên hệ thống.
                </p>
              </div>
            </div>
            <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-sm font-bold shadow-md transition-transform scale-100 active:scale-95 whitespace-nowrap hidden sm:block">
              Xử lý ngay
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard 
            title="Tổng số Ticket" 
            value={stats.total} 
            icon={Ticket} 
            colorClass={{ bg: 'bg-emerald-50', text: 'text-emerald-600' }}
            trend={12}
          />
          <KPICard 
            title="Khách hàng ảnh hưởng" 
            value={stats.impactedCustomers.toLocaleString()} 
            icon={Users} 
            colorClass={{ bg: 'bg-rose-50', text: 'text-rose-600' }}
            trend={-5}
          />
          <KPICard 
            title="Tỷ lệ Đúng hạn SLA" 
            value={stats.slaRate} 
            unit="%"
            icon={Clock} 
            colorClass={{ bg: 'bg-indigo-50', text: 'text-indigo-600' }}
            trend={2.4}
          />
          <KPICard 
            title="Thời gian xử lý TB" 
            value={stats.avgTime} 
            unit="Phút"
            icon={Zap} 
            colorClass={{ bg: 'bg-amber-50', text: 'text-amber-600' }}
            trend={-8}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <ChartCard title="Phân bổ Trạng thái Xử lý">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={statusData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={8} dataKey="value">
                  {statusData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                <Legend verticalAlign="bottom" height={36}/>
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Xu hướng Ticket phát sinh (30 ngày)" className="lg:col-span-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} tickFormatter={(val) => val.split('-').slice(2).join('/')} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} />
                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                <Area type="monotone" dataKey="count" name="Số lượng" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#colorCount)" />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartCard title="Top 5 Chi nhánh phát sinh nhiều nhất">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={branchData} margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} vertical={false} />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 13, fontWeight: 500 }} width={100} />
                <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}/>
                <Bar dataKey="value" fill="#6366f1" radius={[0, 8, 8, 0]} barSize={24} name="Số ticket" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Top 5 Nhân sự xử lý tích cực nhất">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={staffData} margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} vertical={false} />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 13, fontWeight: 500 }} width={120} />
                <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}/>
                <Bar dataKey="value" fill="#10b981" radius={[0, 8, 8, 0]} barSize={24} name="Đã xử lý" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* RCA Row - Deep Analytics based on scc_ht_schema */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-12">
          <ChartCard title="Top 5 Nguyên nhân gốc rễ (Root Causes)">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={topReasons} margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} vertical={false} />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 13, fontWeight: 500, fill: '#ef4444' }} width={120} />
                <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}/>
                <Bar dataKey="value" fill="#ef4444" radius={[0, 8, 8, 0]} barSize={24} name="Số lượng lõi" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Phân bổ Lỗ hổng theo Nhóm thiết bị (Issue Groups)">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={groupData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={2} dataKey="value">
                  {groupData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                <Legend verticalAlign="bottom" height={36}/>
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      </main>

      <footer className="max-w-7xl mx-auto mt-12 pb-8 flex justify-between items-center text-sm text-gray-400 border-t border-gray-100 pt-6">
        <div className="flex items-center gap-2">
          <Activity size={16} />
          <span>Hệ thống giám sát vận hành Real-time</span>
        </div>
        <p>© 2025 SCC HT System • Vietnam Telecom Performance Dashboard</p>
      </footer>
    </div>
  );
}
