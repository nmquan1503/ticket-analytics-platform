import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, AreaChart, Area
} from 'recharts';
import { CheckCircle2, XCircle, Clock3, AlertOctagon, TrendingUp, Users, BarChart2 } from 'lucide-react';
import { htApi } from '../../services/api';

// ── Circular Gauge SVG component ─────────────────────────────────────────────
function CircularGauge({ value, max = 100, color = '#3b82f6', size = 80, label, sublabel }) {
  const radius = (size - 12) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(value / max, 1);
  const dashOffset = circumference * (1 - pct);

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="#e5e7eb" strokeWidth={10} />
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={color} strokeWidth={10}
          strokeDasharray={circumference} strokeDashoffset={dashOffset}
          strokeLinecap="round" style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
      </svg>
      <div className="text-center -mt-1">
        <div className="text-xl font-black text-gray-900">{label}</div>
        {sublabel && <div className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider">{sublabel}</div>}
      </div>
    </div>
  );
}

// ── In-cell mini bar ─────────────────────────────────────────────────────────
function MiniBar({ value, max, color }) {
  const pct = max > 0 ? Math.min((value / max) * 100, 100) : 0;
  return (
    <div className="flex items-center gap-2 w-full">
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="text-xs font-bold text-gray-700 w-8 text-right">{value}</span>
    </div>
  );
}

export default function HTOverviewTab({ filters }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({ kpi: {}, trend: [], stepDist: [], deadlineDist: [], topQueues: [], slaPivot: [] });

  useEffect(() => {
    let isMounted = true;
    const load = async () => {
      setLoading(true);
      try {
        const [kpi, trend, stepDist, deadlineDist, topQueues, slaPivot] = await Promise.all([
          htApi.getKpi(filters), htApi.getTrend(filters), htApi.getStepDist(filters),
          htApi.getDeadlineDist(filters), htApi.getTopQueues(filters, 5), htApi.getSlaPivot(filters)
        ]);
        if (isMounted) setData({ kpi, trend, stepDist, deadlineDist, topQueues, slaPivot });
      } catch (err) { console.error(err); }
      finally { if (isMounted) setLoading(false); }
    };
    load();
    return () => { isMounted = false; };
  }, [filters]);

  if (loading) return (
    <div className="flex flex-col items-center justify-center py-24 gap-3">
      <div className="flex gap-2">
        {[0, 1, 2].map(i => (
          <div key={i} className="w-3 h-3 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: `${i * 150}ms` }} />
        ))}
      </div>
      <p className="text-sm text-gray-400 font-medium">Đang tải dữ liệu Hỗ trợ Kỹ thuật...</p>
    </div>
  );

  const { kpi, trend, stepDist, deadlineDist, topQueues, slaPivot } = data;
  const totalDeadline = deadlineDist.reduce((s, r) => s + (r.value || 0), 0);
  const onTimeEntry = deadlineDist.find(d => d.name === 'Đúng hạn');
  const overdueEntry = deadlineDist.find(d => d.name === 'Quá hạn');
  const maxQueue = Math.max(...topQueues.map(q => q.cnt), 1);
  const maxPivot = Math.max(...slaPivot.map(s => (s.on_time || 0) + (s.overdue || 0)), 1);

  // Build funnel-like data from stepDist
  const totalStep = stepDist.reduce((s, r) => s + (r.value || 0), 0);

  return (
    <div className="space-y-6 animate-fade-in">

      {/* SOS Banner */}
      {kpi.sos_tickets > 0 && (
        <div className="bg-amber-50 border-l-4 border-amber-400 rounded-xl p-4 flex items-center gap-4 shadow-sm">
          <AlertOctagon className="text-amber-500 flex-shrink-0" size={24} />
          <div>
            <p className="font-bold text-amber-800">Cảnh báo {kpi.sos_tickets} Ticket SOS</p>
            <p className="text-sm text-amber-700">Khách hàng phàn nàn nhiều lần – cần xử lý ưu tiên ngay.</p>
          </div>
        </div>
      )}

      {/* ── SECTION 1: KPI Gauges Row ──────────────────────────────────────── */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
        <div className="flex items-center gap-2 mb-6">
          <TrendingUp size={18} className="text-blue-500" />
          <h3 className="font-bold text-gray-800">Hiệu suất Tổng quan</h3>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 items-center">
          <div className="flex flex-col items-center gap-2">
            <div className="text-4xl font-black text-gray-900">{kpi.total_tickets}</div>
            <div className="flex items-center gap-1 text-xs text-gray-500 font-semibold uppercase tracking-wider">
              <BarChart2 size={12} /> Tổng Ticket
            </div>
          </div>
          <CircularGauge
            value={kpi.on_time_rate} max={100} color="#10b981" size={90}
            label={`${kpi.on_time_rate}%`} sublabel="Đúng hạn SLA"
          />
          <CircularGauge
            value={kpi.sla_violations} max={kpi.total_tickets || 1} color="#f59e0b" size={90}
            label={kpi.sla_violations} sublabel="Vi phạm SLA"
          />
          <CircularGauge
            value={kpi.total_rejections} max={kpi.total_tickets || 1} color="#ef4444" size={90}
            label={kpi.total_rejections} sublabel="Lần Reject"
          />
        </div>
      </div>

      {/* ── SECTION 2: Ticket Funnel + Trend ───────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">

        {/* Ticket Pipeline Funnel (dạng Progress Bars xếp dọc) */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex flex-col">
          <div className="flex items-center gap-2 mb-6">
            <Users size={18} className="text-purple-500" />
            <h3 className="font-bold text-gray-800">Phễu Xử lý Ticket</h3>
          </div>
          <div className="flex-1 flex flex-col justify-around gap-4">
            {stepDist.map((step, idx) => {
              const pct = totalStep > 0 ? Math.round((step.value / totalStep) * 100) : 0;
              const stepColors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'];
              const color = stepColors[idx % stepColors.length];
              return (
                <div key={idx} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-gray-700 truncate max-w-[75%]">{step.step_name}</span>
                    <span className="text-xs font-bold text-gray-500">{pct}%</span>
                  </div>
                  <div className="relative h-8 bg-gray-50 rounded-lg overflow-hidden border border-gray-100">
                    <div
                      className="absolute left-0 top-0 h-full rounded-lg flex items-center pl-3 transition-all duration-1000"
                      style={{ width: `${Math.max(pct, 8)}%`, backgroundColor: color + '22', borderRight: `3px solid ${color}` }}
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-bold text-gray-600">{step.value}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Trend Chart */}
        <div className="lg:col-span-3 bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <TrendingUp size={18} className="text-blue-500" />
              <h3 className="font-bold text-gray-800">Xu hướng Ticket HT</h3>
            </div>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 size={14} className="text-emerald-500" />
                <span className="text-gray-500 font-medium">{onTimeEntry?.value} Đúng hạn</span>
              </div>
              <div className="flex items-center gap-1.5">
                <XCircle size={14} className="text-rose-500" />
                <span className="text-gray-500 font-medium">{overdueEntry?.value} Quá hạn</span>
              </div>
            </div>
          </div>
          <div className="h-[230px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend}>
                <defs>
                  <linearGradient id="htGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="ticket_date" axisLine={false} tickLine={false}
                  tick={{ fontSize: 11, fill: '#94a3b8' }}
                  tickFormatter={val => val.split('-').slice(2).join('/')} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }} />
                <Area type="monotone" dataKey="cnt" name="Ticket HT" stroke="#3b82f6" strokeWidth={2.5} fillOpacity={1} fill="url(#htGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* ── SECTION 3: Queue Table + SLA by Service ─────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Queue Data Table with In-cell Bars */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 flex items-center gap-2">
            <Clock3 size={18} className="text-indigo-500" />
            <h3 className="font-bold text-gray-800">Workload theo Queue</h3>
          </div>
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 text-[11px] text-gray-400 uppercase tracking-wider">
                <th className="px-6 py-3 text-left font-semibold">Queue</th>
                <th className="px-6 py-3 text-left font-semibold">Tải xử lý</th>
                <th className="px-6 py-3 text-right font-semibold">Tickets</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {topQueues.map((q, idx) => (
                <tr key={idx} className="hover:bg-blue-50/30 transition-colors group">
                  <td className="px-6 py-3.5">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-blue-400 group-hover:bg-blue-500 transition-colors" />
                      <span className="text-sm font-semibold text-gray-800">{q.queue_name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-3.5 w-48">
                    <MiniBar value={q.cnt} max={maxQueue} color="#3b82f6" />
                  </td>
                  <td className="px-6 py-3.5 text-right">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-50 text-blue-700">
                      {q.cnt}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* SLA by Service Grouped Bar */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center gap-2 mb-6">
            <CheckCircle2 size={18} className="text-emerald-500" />
            <h3 className="font-bold text-gray-800">SLA theo Loại Dịch vụ</h3>
          </div>
          <div className="space-y-4">
            {slaPivot.map((svc, idx) => {
              const total = (svc.on_time || 0) + (svc.overdue || 0);
              const onTimePct = total > 0 ? Math.round((svc.on_time / total) * 100) : 0;
              return (
                <div key={idx} className="space-y-1.5">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-gray-700 truncate max-w-[70%]">{svc.service_type}</span>
                    <span className={`text-xs font-bold ${onTimePct >= 90 ? 'text-emerald-600' : onTimePct >= 75 ? 'text-amber-600' : 'text-rose-600'}`}>
                      {onTimePct}% đúng hạn
                    </span>
                  </div>
                  <div className="flex h-5 w-full rounded-lg overflow-hidden gap-0.5 bg-gray-50">
                    <div
                      className="h-full bg-emerald-400 flex items-center justify-end pr-1.5 transition-all duration-700 rounded-l-lg"
                      style={{ width: `${(svc.on_time / maxPivot) * 100}%` }}
                    >
                      {svc.on_time > 5 && <span className="text-[9px] text-white font-bold">{svc.on_time}</span>}
                    </div>
                    <div
                      className="h-full bg-rose-400 flex items-center justify-start pl-1.5 transition-all duration-700 rounded-r-lg"
                      style={{ width: `${(svc.overdue / maxPivot) * 100}%` }}
                    >
                      {svc.overdue > 2 && <span className="text-[9px] text-white font-bold">{svc.overdue}</span>}
                    </div>
                  </div>
                </div>
              );
            })}
            <div className="flex gap-4 pt-2 text-[11px] text-gray-400 font-semibold">
              <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-emerald-400 inline-block"></span>Đúng hạn</div>
              <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-rose-400 inline-block"></span>Quá hạn</div>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
