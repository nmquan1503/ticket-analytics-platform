import React, { useMemo } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
  PieChart, Pie, Cell, AreaChart, Area 
} from 'recharts';
import { Target, Activity, Zap, ShieldAlert } from 'lucide-react';

import KPICard from '../KPICard';
import ChartCard from '../ChartCard';

export default function QoSTab({ data }) {
  const qosStats = useMemo(() => {
    let sumSuspend = 0;
    let sumActual = 0;
    let autoCount = 0;
    let disasterCount = 0;

    data.forEach(t => {
      sumSuspend += t.suspend_time || 0;
      sumActual += t.actual_time || 0;
      if (t.sc_creation_method === 'SC tạo auto') autoCount++;
      if (t.sc_natural_disaster === 'Có') disasterCount++;
    });

    return {
      avgSuspend: data.length ? Math.round(sumSuspend / data.length) : 0,
      avgActual: data.length ? Math.round(sumActual / data.length) : 0,
      autoRate: data.length ? ((autoCount / data.length) * 100).toFixed(1) : 0,
      disasterRate: data.length ? ((disasterCount / data.length) * 100).toFixed(1) : 0,
    };
  }, [data]);

  const typeData = useMemo(() => {
    const counts = { 'Chủ quan': 0, 'Khách quan': 0 };
    data.forEach(t => { if (counts[t.sc_type] !== undefined) counts[t.sc_type]++; });
    return [
      { name: 'Chủ quan', value: counts['Chủ quan'], color: '#ef4444' }, // Red for human error
      { name: 'Khách quan', value: counts['Khách quan'], color: '#3b82f6' } // Blue for system/external
    ];
  }, [data]);

  const creationData = useMemo(() => {
    const counts = { 'SC tạo auto': 0, 'SC tạo manual (SC tạo tay)': 0 };
    data.forEach(t => { if (counts[t.sc_creation_method] !== undefined) counts[t.sc_creation_method]++; });
    return [
      { name: 'Hệ thống tự động', value: counts['SC tạo auto'], color: '#10b981' },
      { name: 'Khai báo thủ công', value: counts['SC tạo manual (SC tạo tay)'], color: '#f59e0b' }
    ];
  }, [data]);

  // Comparing time across branches
  const timeComparisonData = useMemo(() => {
    const map = {};
    data.forEach(t => {
      if (!map[t.branch_name]) map[t.branch_name] = { branch: t.branch_name, actual: 0, suspend: 0, count: 0 };
      map[t.branch_name].actual += t.actual_time;
      map[t.branch_name].suspend += t.suspend_time;
      map[t.branch_name].count++;
    });
    return Object.values(map).map(b => ({
      name: b.branch,
      'TG Thao tác (Actual)': Math.round(b.actual / b.count),
      'TG Chết mạng (Suspend)': Math.round(b.suspend / b.count)
    })).sort((a,b) => b['TG Chết mạng (Suspend)'] - a['TG Chết mạng (Suspend)']).slice(0, 7);
  }, [data]);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard 
          title="TG Gián đoạn TT (Suspend)" value={qosStats.avgSuspend} unit="Phút" icon={Target} 
          colorClass={{ bg: 'bg-rose-50', text: 'text-rose-600' }} trend={18}
        />
        <KPICard 
          title="TG Thao tác xử lý (Actual)" value={qosStats.avgActual} unit="Phút" icon={Activity} 
          colorClass={{ bg: 'bg-indigo-50', text: 'text-indigo-600' }} trend={-4}
        />
        <KPICard 
          title="Tỷ lệ SC phát hiện Auto" value={qosStats.autoRate} unit="%" icon={Zap} 
          colorClass={{ bg: 'bg-emerald-50', text: 'text-emerald-600' }} trend={5.2}
        />
        <KPICard 
          title="Do Thiên tai / Thời tiết" value={qosStats.disasterRate} unit="%" icon={ShieldAlert} 
          colorClass={{ bg: 'bg-amber-50', text: 'text-amber-600' }} trend={1}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Tính chất vi phạm (Chủ quan vs Khách quan)">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={typeData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                {typeData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
              <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Phương thức phát hiện lỗi (Creation Method)">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={creationData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                {creationData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
              <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <ChartCard title="Độ vênh Thời gian (Gián đoạn vs Xử lý) Top 7 Chi nhánh">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={timeComparisonData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12 }} />
              <YAxis yAxisId="left" orientation="left" axisLine={false} tickLine={false} tick={{ fontSize: 12 }} />
              <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} cursor={{ fill: '#f3f4f6' }}/>
              <Legend />
              <Bar yAxisId="left" dataKey="TG Chết mạng (Suspend)" fill="#fb7185" radius={[4, 4, 0, 0]} />
              <Bar yAxisId="left" dataKey="TG Thao tác (Actual)" fill="#818cf8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}
