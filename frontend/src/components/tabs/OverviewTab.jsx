import React, { useMemo } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
  PieChart, Pie, Cell, AreaChart, Area 
} from 'recharts';
import { Ticket, Users, Clock, Zap, AlertTriangle, ArrowUpCircle } from 'lucide-react';

import KPICard from '../KPICard';
import ChartCard from '../ChartCard';
import { STATUSES } from '../../data/mockData';

export default function OverviewTab({ data, stats, viewMode }) {
  // Status Distribution Data
  const statusData = useMemo(() => {
    return STATUSES.map(s => ({
      name: s.name,
      value: data.filter(t => t.status === s.name).length,
      color: s.color
    }));
  }, [data]);

  // Trend Data (Area Chart)
  const trendData = useMemo(() => {
    const dateMap = {};
    data.forEach(t => {
      dateMap[t.created_date] = (dateMap[t.created_date] || 0) + 1;
    });
    return Object.entries(dateMap)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => new Date(a.date) - new Date(b.date));
  }, [data]);

  // Top 5 Branches
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

  // Top 5 Staff
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

  // HT Specific: Escalation Rate
  const escalationData = useMemo(() => {
    const counts = { 'Có': 0, 'Không': 0 };
    data.forEach(t => { if (counts[t.is_escalated] !== undefined) counts[t.is_escalated]++; });
    return [
      { name: 'Phải Leo thang', value: counts['Có'], color: '#f43f5e' },
      { name: 'Xử lý tại chỗ', value: counts['Không'], color: '#10b981' }
    ];
  }, [data]);

  // HT Specific: Customer Types
  const customerTypeData = useMemo(() => {
    const counts = {};
    data.forEach(t => { if (t.customer_type) counts[t.customer_type] = (counts[t.customer_type] || 0) + 1; });
    return Object.entries(counts).map(([name, value]) => ({ name, value })).sort((a,b)=>b.value - a.value);
  }, [data]);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* SOS Alerts Banner */}
      {(stats.sosCount > 0 || stats.criticalCount > 0) && (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-4 flex items-center justify-between text-red-600 animate-pulse-slow shadow-sm">
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

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard 
          title="Tổng số Ticket" value={stats.total} icon={Ticket} 
          colorClass={{ bg: 'bg-emerald-50', text: 'text-emerald-600' }} trend={12}
        />
        <KPICard 
          title="Khách hàng ảnh hưởng" value={stats.impactedCustomers.toLocaleString()} icon={Users} 
          colorClass={{ bg: 'bg-rose-50', text: 'text-rose-600' }} trend={-5}
        />
        <KPICard 
          title="Tỷ lệ Đúng hạn SLA" value={stats.slaRate} unit="%" icon={Clock} 
          colorClass={{ bg: 'bg-indigo-50', text: 'text-indigo-600' }} trend={2.4}
        />
        <KPICard 
          title="Thời gian xử lý TB" value={stats.avgTime} unit="Phút" icon={Zap} 
          colorClass={{ bg: 'bg-amber-50', text: 'text-amber-600' }} trend={-8}
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

        <ChartCard title="Xu hướng Ticket phát sinh (Timeline)" className="lg:col-span-2">
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

      {/* RCA Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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

      {viewMode === 'HT' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-slide-up">
          <ChartCard title="Tỷ lệ Vượt cấp xử lý (Escalation Rate)">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={escalationData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {escalationData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                <Legend verticalAlign="bottom" height={36}/>
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Phân khúc Khách hàng hỗ trợ">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={customerTypeData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis 
                  dataKey="name" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fontSize: 10, fill: '#64748b' }} 
                  interval={0}
                  angle={-30}
                  textAnchor="end"
                  height={60}
                />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12 }} />
                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Số lượng" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      )}
    </div>
  );
}
