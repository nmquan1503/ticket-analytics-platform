import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, ComposedChart, Line
} from 'recharts';
import { AlertTriangle, Activity, MapPin, Zap } from 'lucide-react';
import { scApi } from '../../services/api';

export default function SCOverviewTab({ filters }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    kpi: {},
    trend: [],
    processingDist: null,
    pareto: [],
    topBranches: []
  });

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      setLoading(true);
      try {
        const [kpi, trend, dist, pareto, branches] = await Promise.all([
          scApi.getKpi(filters),
          scApi.getTrend(filters),
          scApi.getProcessingTimeDist(filters),
          scApi.getParetoIssueGroups(filters),
          scApi.getTopBranches(filters, 5)
        ]);
        if (isMounted) {
          setData({ kpi, trend, processingDist: dist, pareto, topBranches: branches });
        }
      } catch (err) {
        console.error("Failed to fetch SC data", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    fetchData();
    return () => { isMounted = false; };
  }, [filters]);

  if (loading) return <div className="p-12 text-center text-slate-500 font-medium animate-pulse uppercase tracking-widest text-sm">Đang tải trung tâm điều hành...</div>;

  const { kpi, trend, processingDist, pareto, topBranches } = data;

  return (
    <div className="bg-slate-950 text-slate-100 -m-6 p-6 md:p-8 rounded-[1.4rem] space-y-6 shadow-[inset_0_0_80px_rgba(0,0,0,0.5)] border border-slate-800 relative overflow-hidden animate-fade-in">
      {/* Grid Background Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGcgc3Ryb2tlPSIjMzMzMzMzIiBzdHJva2Utd2lkdGg9IjEiIGZpbGw9Im5vbmUiPjxwYXRoIGQ9Ik00MCAwaC00MHY0MCIvPjwvZz48L3N2Zz4=')] opacity-[0.03] pointer-events-none"></div>

      {/* Tựa đề Tab (thay thế cho việc dùng chung ở Dashboard) */}
      <div className="relative z-10 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide">SC Command Center</h2>
          <p className="text-xs text-slate-400 font-mono mt-1">NOC-LEVEL INCIDENT MONITORING</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
          <span className="text-xs text-emerald-400 font-mono font-bold">SYSTEM ONLINE</span>
        </div>
      </div>

      {/* SOS Banner */}
      {(kpi.critical_count > 0 || kpi.disaster_related > 0) && (
        <div className="relative bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center justify-between shadow-[0_0_20px_rgba(239,68,68,0.15)] z-10 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-red-500/20 rounded-full animate-pulse">
              <AlertTriangle size={24} className="text-red-500" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-red-400 tracking-wider uppercase">Critical Incidents Detected</h3>
              <p className="text-sm font-medium text-slate-300">
                Ghi nhận <strong className="text-red-400">{kpi.critical_count} sự cố cấp cao</strong> và <strong className="text-amber-400">{kpi.disaster_related} sự cố do thiên tai</strong> cần xử lý ngay.
              </p>
            </div>
          </div>
          <div className="text-right hidden sm:block">
            <div className="text-[10px] uppercase text-red-500/70 font-bold tracking-widest">Severity Level</div>
            <div className="text-red-500 font-black text-xl animate-pulse">DEFCON 3</div>
          </div>
        </div>
      )}

      {/* Bento Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 relative z-10">
        
        {/* Main Trend Chart with Overlay KPIs */}
        <div className="lg:col-span-8 bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group shadow-lg">
          <div className="absolute top-0 right-0 w-64 h-64 bg-rose-500/5 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>
          
          <div className="flex flex-col sm:flex-row justify-between items-start mb-6 relative z-10">
            <div>
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2 mb-4 sm:mb-0">
                <Activity size={16} className="text-rose-400" /> Cường độ Sự cố
              </h3>
            </div>
            
            {/* Overlay KPIs */}
            <div className="flex gap-6">
              <div className="text-right">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">Tổng Số Lượng</div>
                <div className="text-4xl font-black text-white">{kpi.total_tickets}</div>
              </div>
              <div className="text-right border-l border-slate-700 pl-6">
                <div className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-1">KH Ảnh Hưởng</div>
                <div className="text-4xl font-black text-rose-500">{kpi.impacted_cust?.toLocaleString()}</div>
              </div>
            </div>
          </div>

          <div className="h-[280px] w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend}>
                <defs>
                  <linearGradient id="scGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" />
                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} tickFormatter={(val) => val.split('-').slice(2).join('/')} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#f8fafc' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Area type="monotone" dataKey="cnt" name="Sự cố" stroke="#ef4444" strokeWidth={3} fillOpacity={1} fill="url(#scGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Failing Branches Leaderboard */}
        <div className="lg:col-span-4 bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col shadow-lg">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2">
            <MapPin size={16} className="text-indigo-400" /> Điểm nóng (Hotspot)
          </h3>
          <div className="flex-1 flex flex-col gap-5 justify-center">
            {topBranches.map((branch, idx) => (
              <div key={idx} className="flex flex-col gap-2 group">
                <div className="flex justify-between items-center text-sm">
                  <div className="flex items-center gap-3">
                    <span className={`flex items-center justify-center w-6 h-6 rounded bg-slate-800 text-xs font-bold font-mono transition-colors ${idx === 0 ? 'text-rose-400 border border-rose-500/30 bg-rose-500/10' : 'text-slate-400'}`}>
                      0{idx + 1}
                    </span>
                    <span className="font-semibold text-slate-200 group-hover:text-white transition-colors">{branch.name}</span>
                  </div>
                  <span className="font-bold text-white">{branch.cnt} <span className="text-[10px] text-slate-500 font-normal">TICKETS</span></span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all duration-1000 ${idx === 0 ? 'bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.8)]' : 'bg-indigo-500'}`} 
                    style={{ width: `${(branch.cnt / (topBranches[0]?.cnt || 1)) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Pareto Chart */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-lg">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2">
            <Zap size={16} className="text-amber-400" /> Phân loại Nguyên nhân (Pareto)
          </h3>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={pareto} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#94a3b8' }} interval={0} angle={-20} textAnchor="end" height={50} />
                <YAxis yAxisId="left" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} width={40} />
                <YAxis yAxisId="right" orientation="right" axisLine={false} tickLine={false} tickFormatter={(val) => `${val}%`} tick={{ fontSize: 10, fill: '#64748b' }} width={40}/>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }} />
                <Bar yAxisId="left" dataKey="cnt" fill="#3b82f6" name="Số lượng" radius={[4,4,0,0]} barSize={25} />
                <Line yAxisId="right" type="monotone" dataKey="cumulative_pct" stroke="#f59e0b" strokeWidth={2} name="Tích lũy (%)" dot={{ r: 3, fill: '#f59e0b', strokeWidth: 0 }} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Processing Time Stats */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between shadow-lg">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-6">
            Hiệu suất Khắc phục
          </h3>
          <div className="grid grid-cols-2 gap-4 mb-8">
            <div className="bg-slate-800/40 p-4 rounded-xl border border-slate-800/50 flex flex-col justify-center items-center text-center">
              <div className="text-[10px] text-slate-400 uppercase font-bold mb-2">Tỉ lệ Đúng hạn</div>
              <div className="text-3xl font-black text-emerald-400">{kpi.on_time_rate}%</div>
            </div>
            <div className="bg-slate-800/40 p-4 rounded-xl border border-slate-800/50 flex flex-col justify-center items-center text-center">
              <div className="text-[10px] text-slate-400 uppercase font-bold mb-2">Thời gian TB</div>
              <div className="text-3xl font-black text-indigo-400 flex items-baseline gap-1">
                {kpi.avg_actual_time} <span className="text-sm text-slate-500 font-medium">phút</span>
              </div>
            </div>
          </div>
          
          <div>
            <div className="text-[10px] text-slate-500 uppercase font-bold mb-2 text-center">Phân bổ thời gian (Phút)</div>
            <div className="h-[100px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={processingDist?.histogram || []} margin={{ top: 0, right: 0, left: -25, bottom: 0 }}>
                  <XAxis dataKey="high" tickFormatter={(val) => `<${val}`} axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                  <Tooltip cursor={{ fill: '#1e293b' }} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }} />
                  <Bar dataKey="freq" fill="#8b5cf6" radius={[2, 2, 0, 0]} name="Số lượng" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
