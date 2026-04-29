const buildQueryString = (filters, extraParams = {}) => {
  const params = new URLSearchParams();
  if (filters) {
    if (filters.dateRange && filters.dateRange !== 'all') params.append('date_range', filters.dateRange);
    if (filters.locations && filters.locations.length > 0) filters.locations.forEach(l => params.append('locations', l));
    if (filters.branches && filters.branches.length > 0) filters.branches.forEach(b => params.append('branches', b));
    if (filters.priorities && filters.priorities.length > 0) filters.priorities.forEach(p => params.append('priorities', p));
  }
  Object.keys(extraParams).forEach(k => params.append(k, extraParams[k]));
  const str = params.toString();
  return str ? `?${str}` : '';
};

// -------------------------------------------------------------
// API CHO SC (SỰ CỐ)
// -------------------------------------------------------------
export const scApi = {
  getKpi: async (filters) => {
    const res = await fetch(`/sc_analytics/kpi${buildQueryString(filters)}`);
    return res.json();
  },
  getTrend: async (filters) => {
    const res = await fetch(`/sc_analytics/trend${buildQueryString(filters)}`);
    return res.json();
  },
  getProcessingTimeDist: async (filters) => {
    const res = await fetch(`/sc_analytics/processing_time_distribution${buildQueryString(filters)}`);
    return res.json();
  },
  getParetoIssueGroups: async (filters) => {
    const res = await fetch(`/sc_analytics/pareto_issue_groups${buildQueryString(filters)}`);
    return res.json();
  },
  getTopBranches: async (filters, limit = 5) => {
    const res = await fetch(`/sc_analytics/top_branches_ranked${buildQueryString(filters, { limit })}`);
    return res.json();
  }
};

// -------------------------------------------------------------
// API CHO HT (HỖ TRỢ KỸ THUẬT)
// -------------------------------------------------------------
export const htApi = {
  getKpi: async (filters) => {
    const res = await fetch(`/ht_analytics/kpi${buildQueryString(filters)}`);
    return res.json();
  },
  getTrend: async (filters) => {
    const res = await fetch(`/ht_analytics/trend${buildQueryString(filters)}`);
    return res.json();
  },
  getStepDist: async (filters) => {
    const res = await fetch(`/ht_analytics/step_distribution${buildQueryString(filters)}`);
    return res.json();
  },
  getDeadlineDist: async (filters) => {
    const res = await fetch(`/ht_analytics/deadline_distribution${buildQueryString(filters)}`);
    return res.json();
  },
  getTopQueues: async (filters, limit = 5) => {
    const res = await fetch(`/ht_analytics/top_processing_queues${buildQueryString(filters, { limit })}`);
    return res.json();
  },
  getSlaPivot: async (filters) => {
    const res = await fetch(`/ht_analytics/sla_by_service_pivot${buildQueryString(filters)}`);
    return res.json();
  }
};

// -------------------------------------------------------------
// API CHO CHATBOT & AI
// -------------------------------------------------------------
export const chatApi = {
  sendMessage: async (text) => {
    // API hiện tại không nhận params nên gửi body rỗng
    const res = await fetch(`/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });
    if (!res.ok) throw new Error("Lỗi kết nối Chat API");
    return res.json();
  },
  getDownloadUrl: (fileId) => {
    return `/chat/download/${fileId}`;
  },
  fetchCsvData: async (fileId) => {
    const res = await fetch(`/chat/download/${fileId}`);
    if (!res.ok) throw new Error("Lỗi lấy dữ liệu CSV");
    return res.text();
  }
};
