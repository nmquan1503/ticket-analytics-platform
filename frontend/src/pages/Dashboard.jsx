import React, { useState, useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import {
  Calendar, MapPin, Briefcase, Filter, ChevronDown,
  User, Activity, AlertTriangle, LayoutDashboard, Target, GitBranch
} from 'lucide-react';

// Components
import KPICard from '../components/KPICard';
import ChartCard from '../components/ChartCard';
import MultiSelect from '../components/MultiSelect';
import AICopilot from '../components/AICopilot';
import OverviewTab from '../components/tabs/OverviewTab';
import QoSTab from '../components/tabs/QoSTab';
import BottleneckTab from '../components/tabs/BottleneckTab';

// Data
import { mockSCData, mockHTData, STATUSES, LOCATIONS, BRANCHES, PRIORITIES, LOCATION_BRANCH_MAP } from '../data/mockData';

export default function Dashboard() {
  const now = new Date();
  const [viewMode, setViewMode] = useState('SC'); // 'SC' or 'HT'
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'qos', 'bottleneck'
  
  // Real Filter States (Multi-select uses arrays now)
  const [dateRange, setDateRange] = useState('30'); // '7' or '30'
  const [locationFilter, setLocationFilter] = useState([]);
  const [branchFilter, setBranchFilter] = useState([]);
  const [priorityFilter, setPriorityFilter] = useState([]);

  // Logic Chi nhánh khả dụng dựa trên Khu vực
  const availableBranches = useMemo(() => {
    if (locationFilter.length === 0) return BRANCHES;
    return locationFilter.flatMap(loc => LOCATION_BRANCH_MAP[loc] || []);
  }, [locationFilter]);

  // Tự động dọn dẹp Chi nhánh đã chọn nếu không còn khả dụng
  React.useEffect(() => {
    if (branchFilter.length > 0) {
      const validSelected = branchFilter.filter(b => availableBranches.includes(b));
      if (validSelected.length !== branchFilter.length) {
        setBranchFilter(validSelected);
      }
    }
  }, [availableBranches]);
  

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
      } else if (dateRange.startsWith('Q')) {
        const quarter = parseInt(dateRange[1]);
        const year = now.getFullYear();
        const startMonth = (quarter - 1) * 3;
        const endMonth = startMonth + 2;
        const startDate = new Date(year, startMonth, 1);
        const endDate = new Date(year, endMonth + 1, 0);
        if (tDate < startDate || tDate > endDate) return false;
      }
      return true;
    });
  }, [viewMode, locationFilter, branchFilter, priorityFilter, dateRange]);

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

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 p-4 bg-white rounded-2xl shadow-sm border border-gray-100">
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
                <option value="Q1">Quý 1 ({now.getFullYear()})</option>
                <option value="Q2">Quý 2 ({now.getFullYear()})</option>
                <option value="Q3">Quý 3 ({now.getFullYear()})</option>
                <option value="Q4">Quý 4 ({now.getFullYear()})</option>
                <option value="all">Tất cả thời gian</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" size={16} />
            </div>
          </div>

          <div className="flex flex-col gap-1.5 z-40">
            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider ml-1">Khu vực</label>
            <MultiSelect
              options={LOCATIONS}
              selected={locationFilter}
              onChange={setLocationFilter}
              placeholder="Chọn khu vực..."
              icon={MapPin}
            />
          </div>

          <div className="flex flex-col gap-1.5 z-30">
            <label className="text-xs font-bold text-gray-400 uppercase tracking-wider ml-1">Chi nhánh</label>
            <MultiSelect
              options={availableBranches}
              selected={branchFilter}
              onChange={setBranchFilter}
              placeholder={locationFilter.length > 0 ? "Chọn chi nhánh..." : "Chọn khu vực trước..."}
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

        {/* Tab Navigation Menu */}
        <div className="flex items-center gap-2 mt-4 overflow-x-auto pb-2 scrollbar-hide">
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm transition-all whitespace-nowrap ${activeTab === 'overview' ? 'bg-indigo-600 text-white shadow-md' : 'bg-white text-gray-500 hover:bg-gray-100'}`}
          >
            <LayoutDashboard size={18} />
            Tổng quan (Overview)
          </button>
          <button
            onClick={() => setActiveTab('qos')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm transition-all whitespace-nowrap ${activeTab === 'qos' ? 'bg-indigo-600 text-white shadow-md' : 'bg-white text-gray-500 hover:bg-gray-100'}`}
          >
            <Target size={18} />
            Đánh giá Chất lượng (QoS/CX)
          </button>
          <button
            onClick={() => setActiveTab('bottleneck')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm transition-all whitespace-nowrap ${activeTab === 'bottleneck' ? 'bg-indigo-600 text-white shadow-md' : 'bg-white text-gray-500 hover:bg-gray-100'}`}
          >
            <GitBranch size={18} />
            Phân tích Ùn tắc (Bottlenecks)
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto space-y-6">
        {activeTab === 'overview' && <OverviewTab data={data} stats={stats} viewMode={viewMode} />}
        {activeTab === 'qos' && <QoSTab data={data} />}
        {activeTab === 'bottleneck' && <BottleneckTab data={data} />}
      </main>

      <footer className="max-w-7xl mx-auto mt-12 pb-8 flex justify-between items-center text-sm text-gray-400 border-t border-gray-100 pt-6">
        <div className="flex items-center gap-2">
          <Activity size={16} />
          <span>Hệ thống giám sát vận hành Real-time</span>
        </div>
        <p>© 2025 SCC HT System • Vietnam Telecom Performance Dashboard</p>
      </footer>

      {/* Tích hợp trực tiếp Trợ lý AI & SQL Analyzer */}
      <AICopilot />
    </div>
  );
}
