import React, { useMemo } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  ComposedChart, Line, Legend
} from 'recharts';
import { ShieldX, AlertTriangle, GitMerge, TrendingUp, Clock, Calendar } from 'lucide-react';

import KPICard from '../KPICard';
import ChartCard from '../ChartCard';

export default function BottleneckTab({ data }) {
  const bottleneckStats = useMemo(() => {
    let totalRejection = 0;
    let totalViolation = 0;
    let totalWaitTime = 0;
    let totalAge = 0;
    let anyRejectionCount = 0;
    let anyViolationCount = 0;

    data.forEach(t => {
      totalRejection += t.rejection_count || 0;
      totalViolation += t.sla_violation_count || 0;
      totalWaitTime += t.change_queue_time || 0;
      totalAge += t.ticket_age_days || 0;
      if (t.rejection_count > 0) anyRejectionCount++;
      if (t.sla_violation_count > 0) anyViolationCount++;
    });

    return {
      rejectionRate: data.length ? ((anyRejectionCount / data.length) * 100).toFixed(1) : 0,
      violationRate: data.length ? ((anyViolationCount / data.length) * 100).toFixed(1) : 0,
      avgWait: data.length ? Math.round(totalWaitTime / data.length) : 0,
      avgAge: data.length ? (totalAge / data.length).toFixed(1) : 0,
      totalRejection,
      totalViolation,
    };
  }, [data]);

  // Queue Analytics
  const queueData = useMemo(() => {
    const map = {};
    data.forEach(t => {
      const q = t.queue_process;
      if (!map[q]) map[q] = { name: q, tickets: 0, rejections: 0, waitTime: 0, count: 0 };
      map[q].tickets++;
      map[q].rejections += t.rejection_count || 0;
      map[q].waitTime += t.change_queue_time || 0;
      map[q].count++;
    });

    return Object.values(map)
      .map(q => ({ ...q, avgWait: Math.round(q.waitTime / q.count) }))
      .sort((a,b) => b.tickets - a.tickets);
  }, [data]);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Warning Alert */}
      {(bottleneckStats.totalRejection > 0 || bottleneckStats.totalViolation > 0) && (
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 flex items-center gap-4 text-amber-800 shadow-sm">
          <div className="p-2 bg-amber-100 rounded-full shrink-0">
            <ShieldX size={24} className="text-amber-600" />
          </div>
          <div>
            <h3 className="font-bold text-lg text-amber-900">Phân tích Rủi ro Quy trình!</h3>
            <p className="text-sm font-medium">
              Phát hiện <strong>{bottleneckStats.totalRejection} lượt từ chối (đá bóng)</strong> giữa các phòng ban và <strong>{bottleneckStats.totalViolation} lượt chót hạn SLA</strong> trong kỳ báo cáo này.
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
        <KPICard 
          title="Vé bị đá bóng" value={bottleneckStats.rejectionRate} unit="%" icon={GitMerge} 
          colorClass={{ bg: 'bg-orange-50', text: 'text-orange-600' }}
        />
        <KPICard 
          title="Lượt tái VP SLA" value={bottleneckStats.violationRate} unit="%" icon={AlertTriangle} 
          colorClass={{ bg: 'bg-rose-50', text: 'text-rose-600' }}
        />
        <KPICard 
          title="TG Ngâm Ticket TB" value={bottleneckStats.avgWait} unit="Phút" icon={Clock} 
          colorClass={{ bg: 'bg-amber-50', text: 'text-amber-600' }} trend={22}
        />
        <KPICard 
          title="Tuổi thọ tồn kho TB" value={bottleneckStats.avgAge} unit="Ngày" icon={Calendar} 
          colorClass={{ bg: 'bg-indigo-50', text: 'text-indigo-600' }} trend={5}
        />
        <KPICard 
          title="Tổng lượt Từ chối" value={bottleneckStats.totalRejection} icon={TrendingUp} 
          colorClass={{ bg: 'bg-orange-100', text: 'text-orange-700' }}
        />
        <KPICard 
          title="Tổng lượt Vi phạm" value={bottleneckStats.totalViolation} icon={ShieldX} 
          colorClass={{ bg: 'bg-rose-100', text: 'text-rose-700' }}
        />
      </div>

      <div className="grid grid-cols-1 gap-6">
        <div className="bg-gradient-to-br from-slate-900 to-slate-800 p-6 rounded-2xl shadow-lg border border-slate-700">
          <div className="mb-6 flex justify-between items-center">
            <div>
              <h3 className="text-lg font-bold text-white">PROCESSING QUEUES & REJECTION RATES</h3>
              <p className="text-slate-400 text-sm mt-1">Real-time Data: Tắc nghẽn giữa các Đơn vị</p>
            </div>
            <span className="px-3 py-1 bg-rose-500/20 text-rose-400 text-xs font-bold rounded-full border border-rose-500/30">
              Risk Analytics
            </span>
          </div>
          
          <div className="w-full h-[450px]">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={queueData} layout="vertical" margin={{ top: 20, right: 30, left: 60, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#334155" />
                <XAxis type="number" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 13, fontWeight: 600, fill: '#f8fafc' }} />
                
                <Tooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }} 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                
                <Bar dataKey="tickets" name="Tổng vé xử lý" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20} />
                <Bar dataKey="rejections" name="Số lượt Đá Bóng" fill="#f97316" radius={[0, 4, 4, 0]} barSize={20} />
                <Bar dataKey="avgWait" name="TG Ngâm (Phút)" fill="#f59e0b" radius={[0, 4, 4, 0]} barSize={10} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
