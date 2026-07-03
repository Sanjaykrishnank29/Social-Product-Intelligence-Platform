import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';

const API = 'http://localhost:8001/api/v1';

const formatReportType = (type: string) =>
  type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

const capitalize = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

export const ExecutiveIntelligence: React.FC = () => {
  const [insights, setInsights] = useState<any[]>([]);
  const [reports, setReports] = useState<any[]>([]);
  const [filteredReports, setFilteredReports] = useState<any[]>([]);
  const [filterText, setFilterText] = useState('');
  const [loadingInsights, setLoadingInsights] = useState(true);
  const [loadingReports, setLoadingReports] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [exportMsg, setExportMsg] = useState('');

  const fetchInsights = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/insights`);
      if (res.data.status === 'success') setInsights(res.data.insights);
    } catch (e) {
      console.error('Failed to load insights', e);
    } finally {
      setLoadingInsights(false);
    }
  }, []);

  const fetchReports = useCallback(async () => {
    const sampleReport = {
      id: 'sample_pdf',
      report_type: 'Weekly Intelligence',
      summary: 'Executive Summary and Market Insights for Q4 (Sample PDF)',
      generated_at: new Date().toISOString()
    };
    try {
      const res = await axios.get(`${API}/reports`);
      if (res.data.status === 'success') {
        const allReports = [sampleReport, ...res.data.reports];
        setReports(allReports);
        setFilteredReports(allReports);
      }
    } catch (e) {
      console.error('Failed to load reports', e);
      // Fallback to sample if backend is down
      setReports([sampleReport]);
      setFilteredReports([sampleReport]);
    } finally {
      setLoadingReports(false);
    }
  }, []);

  useEffect(() => {
    fetchInsights();
    fetchReports();
  }, [fetchInsights, fetchReports]);

  // Live filter for reports
  useEffect(() => {
    if (!filterText.trim()) {
      setFilteredReports(reports);
    } else {
      const q = filterText.toLowerCase();
      setFilteredReports(
        reports.filter(r =>
          r.report_type.toLowerCase().includes(q) ||
          (r.summary || '').toLowerCase().includes(q)
        )
      );
    }
  }, [filterText, reports]);

  const handleUpdateAll = async () => {
    setRefreshing(true);
    await Promise.all([fetchInsights(), fetchReports()]);
    setRefreshing(false);
  };

  const handleQuickExport = () => {
    if (insights.length === 0) { setExportMsg('No data to export yet.'); return; }
    const rows = [
      ['Brand', 'Top Risk', 'Opportunity', 'Executive Summary', 'Generated At'],
      ...insights.map(i => [
        capitalize(i.brand),
        i.top_risk,
        i.top_opportunity_summary || i.top_opportunity || '',
        i.executive_summary,
        new Date(i.generated_at).toLocaleDateString()
      ])
    ];
    const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'executive_insights.csv';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setExportMsg('Exported!');
    setTimeout(() => setExportMsg(''), 2000);
  };

  const handleDownloadPDF = (reportId: number | string) => {
    if (reportId === 'sample_pdf') {
      window.open(`/Sample_Report.pdf`, '_blank');
    } else {
      window.open(`${API}/reports/download/${reportId}`, '_blank');
    }
  };

  // Derive a short opportunity label (first sentence or first 80 chars)
  const shortOpportunity = (text: string) => {
    if (!text) return 'N/A';
    const sentence = text.split(/[.!?]/)[0];
    return sentence.length > 80 ? sentence.slice(0, 77) + '...' : sentence;
  };

  return (
    <div className="relative min-h-screen pb-24 -mt-8 pt-4">

      <div className="relative z-10 space-y-10">

        {/* Quick Export Row */}
        <div className="flex justify-end">
          <button
            onClick={handleQuickExport}
            className="flex items-center gap-2 px-5 py-2.5 bg-white border border-outline-variant/30 rounded-full font-semibold text-[14px] text-on-surface shadow-sm hover:shadow-md transition-all"
          >
            <span className="material-symbols-outlined text-[20px]">download</span>
            {exportMsg || 'Quick Export'}
          </button>
        </div>

        {/* ── SECTION 1: Key Insights ── */}
        <div>
          <div className="flex items-end justify-between mb-6">
            <div>
              <h2 className="text-[22px] font-semibold text-on-surface tracking-tight">Key Insights</h2>
              <p className="text-[14px] text-on-surface-variant mt-1.5 leading-relaxed">Platform-specific performance and risk analysis</p>
            </div>
            <div className="flex gap-3">
              <span className="px-4 py-1.5 rounded-full bg-[#6cf8bb]/30 text-[#006c49] text-[13px] font-semibold border border-[#6cf8bb]/50">Live Updates</span>
              <span className="px-4 py-1.5 rounded-full bg-white border border-outline-variant/30 text-on-surface-variant text-[13px] font-semibold shadow-sm">Q3 Analysis</span>
            </div>
          </div>

          {loadingInsights ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
              {[0,1,2,3].map(i => (
                <div key={i} className="bg-white p-6 rounded-[16px] shadow-sm border border-white/50 animate-pulse h-72">
                  <div className="h-4 bg-surface-container rounded w-1/2 mb-4"></div>
                  <div className="h-3 bg-surface-container rounded w-full mb-2"></div>
                  <div className="h-3 bg-surface-container rounded w-5/6"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
              {insights.map((insight, idx) => (
                <div key={idx} className="bg-white p-7 rounded-[16px] shadow-[0_10px_15px_-3px_rgba(0,0,0,0.05)] border border-white/50 flex flex-col gap-0">
                  {/* Card Header */}
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="text-[18px] font-semibold text-on-surface capitalize tracking-tight">{capitalize(insight.brand)}</h3>
                      <p className="text-[12px] text-on-surface-variant mt-1">{new Date(insight.generated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</p>
                    </div>
                    <div className="flex gap-0.5 items-end h-6">
                      {[40,70,100,60,80].map((h, i) => (
                        <div key={i} className="w-1.5 bg-[#006c49] rounded-t-sm opacity-70" style={{ height: `${h}%` }}></div>
                      ))}
                    </div>
                  </div>

                  {/* Executive Summary — capped at 4 lines */}
                  <p className="text-[13px] text-on-surface-variant leading-[1.7] mb-5 line-clamp-4">{insight.executive_summary}</p>

                  <div className="space-y-2 mt-auto">
                    <div className="bg-[#ffdad6]/40 border border-[#ffdad6] rounded-[10px] p-3.5">
                      <p className="text-[11px] font-bold text-[#ba1a1a] mb-1 flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-[14px]">error</span> Top Risk
                      </p>
                      <p className="text-[13px] text-[#410002] leading-[1.6]">{insight.top_risk}</p>
                    </div>
                    <div className="bg-[#6cf8bb]/30 border border-[#6cf8bb]/50 rounded-[10px] p-3.5">
                      <p className="text-[11px] font-bold text-[#006c49] mb-1 flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-[14px]">trending_up</span> Opportunity
                      </p>
                      <p className="text-[13px] text-[#002116] leading-[1.6]">{shortOpportunity(insight.top_opportunity_summary || insight.top_opportunity || '')}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ── SECTION 2: Generated Reports ── */}
        <div className="mt-4">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-[22px] font-semibold text-on-surface tracking-tight">Weekly Intelligence Reports</h2>
            <button
              onClick={handleUpdateAll}
              disabled={refreshing}
              className="flex items-center gap-2 text-[13px] font-semibold text-on-surface hover:text-primary transition-colors disabled:opacity-50"
            >
              <span className={`material-symbols-outlined text-[18px] ${refreshing ? 'animate-spin' : ''}`}>sync</span>
              {refreshing ? 'Refreshing...' : 'Update All'}
            </button>
          </div>

          {/* Filter Bar */}
          <div className="flex gap-3 mb-5">
            <div className="flex-grow bg-white border border-outline-variant/30 rounded-[8px] shadow-sm flex items-center px-4 gap-2">
              <span className="material-symbols-outlined text-on-surface-variant text-[18px]">filter_list</span>
              <input
                type="text"
                placeholder="Filter by report name..."
                value={filterText}
                onChange={e => setFilterText(e.target.value)}
                className="w-full bg-transparent border-none py-2.5 text-[14px] focus:ring-0 text-on-surface placeholder:text-on-surface-variant"
              />
              {filterText && (
                <button onClick={() => setFilterText('')} className="text-on-surface-variant hover:text-on-surface">
                  <span className="material-symbols-outlined text-[16px]">close</span>
                </button>
              )}
            </div>
          </div>

          {/* Table Header */}
          <div className="grid grid-cols-12 gap-4 px-5 py-3.5 border-b border-outline-variant/30 text-[11px] font-bold text-on-surface-variant uppercase tracking-widest">
            <div className="col-span-3">Report Type</div>
            <div className="col-span-5">Summary</div>
            <div className="col-span-2">Generated At</div>
            <div className="col-span-2 text-right">Action</div>
          </div>

          {/* Table Rows */}
          {loadingReports ? (
            <div className="space-y-3 mt-4">
              {[0,1].map(i => (
                <div key={i} className="bg-white p-4 rounded-[12px] animate-pulse h-16 border border-white/50"></div>
              ))}
            </div>
          ) : filteredReports.length === 0 ? (
            <div className="text-center py-16 text-on-surface-variant text-[14px]">
              <span className="material-symbols-outlined text-[48px] mb-2 block opacity-30">description</span>
              {filterText ? `No reports matching "${filterText}"` : 'No reports generated yet.'}
            </div>
          ) : (
            <div className="space-y-3 mt-4">
              {filteredReports.map((report, idx) => (
                <div key={idx} className="bg-white px-6 py-5 rounded-[12px] shadow-[0_4px_12px_-2px_rgba(0,0,0,0.04)] border border-white/50 grid grid-cols-12 gap-4 items-center hover:shadow-md transition-shadow">
                  <div className="col-span-3 flex items-center gap-3">
                    <div className="w-9 h-9 bg-surface-container rounded-[8px] flex items-center justify-center shrink-0">
                      <span className="material-symbols-outlined text-[18px] text-on-surface-variant">monitoring</span>
                    </div>
                    <span className="text-[14px] font-semibold text-on-surface leading-snug">{formatReportType(report.report_type)}</span>
                  </div>
                  <div className="col-span-5 text-[14px] text-on-surface-variant leading-[1.6] line-clamp-2 pr-4">{report.summary}</div>
                  <div className="col-span-2 text-[13px] text-on-surface-variant leading-relaxed">
                    {new Date(report.generated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}<br/>
                    <span className="text-[12px] text-on-surface-variant/60">{new Date(report.generated_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                  <div className="col-span-2 flex justify-end">
                    <button
                      onClick={() => handleDownloadPDF(report.id)}
                      className="flex items-center gap-2 px-4 py-2 bg-white border border-outline-variant/30 rounded-full text-[12px] font-semibold text-on-surface hover:bg-surface-container-lowest shadow-sm transition-all"
                    >
                      <span className="material-symbols-outlined text-[15px]">picture_as_pdf</span>
                      Download PDF
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="flex items-center justify-between mt-6 text-[13px] text-on-surface-variant">
            <span>Showing {filteredReports.length} of {reports.length} report{reports.length !== 1 ? 's' : ''}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
