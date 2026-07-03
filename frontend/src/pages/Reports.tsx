import React, { useEffect, useState, useCallback, useRef } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts';

const API = 'http://localhost:8001/api/v1';
const BRAND = 'amazon';

const ASPECT_LABELS: Record<string, string> = {
  delivery_packaging: 'Delivery & Packaging',
  product_quality: 'Product Quality',
  price_value: 'Price & Value',
  returns_refunds: 'Returns & Refunds',
  app_ux: 'App UX',
};

const SENTIMENT_COLORS: Record<string, string> = {
  positive: '#006c49',
  neutral: '#4a5568',
  negative: '#ba1a1a',
};

const PIE_COLORS = ['#6cf8bb', '#718096', '#ffdad6'];

const formatReportType = (t: string) =>
  t.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

// ─── Generate standalone HTML for the print window ───────────────────────────
function buildPrintHTML(data: any, reportMeta: any) {
  const { brand, aspectScores, topTopics, sentPie, feed, insight } = data;
  const sentTotal = sentPie.reduce((a: number, b: any) => a + b.value, 0);
  const positivePct = sentTotal > 0 ? Math.round((sentPie[0].value / sentTotal) * 100) : 0;
  const neutralPct  = sentTotal > 0 ? Math.round((sentPie[1].value / sentTotal) * 100) : 0;
  const negativePct = sentTotal > 0 ? Math.round((sentPie[2].value / sentTotal) * 100) : 0;
  const reportDate = reportMeta
    ? new Date(reportMeta.generated_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
    : new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });

  const recs = [
    'Prioritize fixing the AI search feature UX — it is the #1 complaint driver',
    'Improve delivery reliability tracking notifications to reduce anxiety-related reviews',
    'Streamline the returns & refunds process with clearer status updates',
    'Invest in customer support response time and resolution quality',
    'Leverage strong product quality perception in marketing campaigns',
  ];

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width"/>
<title>Amazon Intelligence Report – ${reportDate}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Outfit',sans-serif;background:#fff;color:#1a1c1e;font-size:13px;line-height:1.6;padding:32px 40px}
  h1{font-size:22px;font-weight:800;color:#131b2e;letter-spacing:-.5px}
  .sub{font-size:12px;color:#6b7280;margin-top:4px}
  hr{border:none;border-top:1px solid #e5e7eb;margin:20px 0}
  .sec{margin-bottom:28px;page-break-inside:avoid}
  .sec-title{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#6b7280;border-bottom:1px solid #e5e7eb;padding-bottom:6px;margin-bottom:14px}
  .kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
  .kpi{background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;padding:14px}
  .kpi-val{font-size:24px;font-weight:800;color:#131b2e;margin-bottom:2px}
  .kpi-lbl{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#9ca3af}
  .sum-box{background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;padding:14px;font-size:13px;line-height:1.8}
  .sent-row{margin-bottom:10px}
  .sent-lbl{display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px}
  .bar-bg{height:8px;background:#f3f4f6;border-radius:99px;overflow:hidden}
  .bar-fill{height:100%;border-radius:99px}
  .asp-row{display:flex;align-items:center;gap:10px;margin-bottom:7px}
  .asp-lbl{width:155px;font-size:12px;color:#374151;flex-shrink:0}
  .asp-bg{flex:1;height:9px;background:#f3f4f6;border-radius:99px;overflow:hidden}
  .asp-fill{height:100%;border-radius:99px}
  .asp-pct{width:36px;text-align:right;font-size:12px;font-weight:600;color:#374151}
  table{width:100%;border-collapse:collapse;font-size:12px}
  th{text-align:left;padding:7px 10px;background:#f9fafb;border-bottom:2px solid #e5e7eb;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.06em;font-size:9px}
  td{padding:7px 10px;border-bottom:1px solid #f3f4f6;color:#374151}
  tr:last-child td{border-bottom:none}
  .r-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
  .r-box{padding:14px;border-radius:10px}
  .r-box.risk{background:rgba(255,218,214,.3);border:1px solid #ffdad6}
  .r-box.opp{background:rgba(108,248,187,.2);border:1px solid rgba(108,248,187,.5)}
  .r-ttl{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}
  .r-ttl.risk{color:#ba1a1a}.r-ttl.opp{color:#006c49}
  .r-txt{font-size:13px;line-height:1.6}
  .r-txt.risk{color:#410002}.r-txt.opp{color:#002116}
  .rev{background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:10px;margin-bottom:7px}
  .rev-meta{display:flex;justify-content:space-between;margin-bottom:5px}
  .rev-src{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#9ca3af}
  .badge{font-size:9px;font-weight:700;padding:2px 7px;border-radius:99px}
  .badge.positive{background:rgba(108,248,187,.3);color:#006c49}
  .badge.negative{background:rgba(255,218,214,.4);color:#ba1a1a}
  .badge.neutral{background:#f3f4f6;color:#6b7280}
  .rev-txt{font-size:12px;line-height:1.5;color:#374151}
  .rev-dt{font-size:10px;color:#9ca3af;margin-top:5px}
  .rec-item{display:flex;gap:10px;margin-bottom:9px;align-items:flex-start}
  .rec-num{width:20px;height:20px;background:rgba(108,248,187,.3);border:1px solid rgba(108,248,187,.5);border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:11px;color:#006c49;font-weight:700}
  .footer{text-align:center;font-size:10px;color:#9ca3af;margin-top:28px;padding-top:14px;border-top:1px solid #e5e7eb}
  .header-row{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:20px}
  .brand-badge{display:inline-block;background:rgba(108,248,187,.3);color:#006c49;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;padding:2px 9px;border-radius:99px;border:1px solid rgba(108,248,187,.5);margin-top:5px}
  @media print{body{padding:20px 28px}.sec{page-break-inside:avoid}*{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}}
</style>
</head>
<body>
<div class="header-row">
  <div>
    <h1>Amazon Intelligence Report</h1>
    <p class="sub">${formatReportType(reportMeta?.report_type || 'weekly_intelligence')} &nbsp;·&nbsp; ${reportDate}</p>
    <span class="brand-badge">Amazon</span>
  </div>
  <div style="text-align:right;color:#9ca3af;font-size:10px">Generated by SocialIntel AI<br/>Social Intelligence Platform</div>
</div>
<hr/>

<div class="sec">
  <div class="sec-title">1. KPI Scorecard</div>
  <div class="kpi-grid">
    <div class="kpi"><div class="kpi-val" style="color:#006c49">${brand.score}<span style="font-size:13px;color:#9ca3af">/100</span></div><div class="kpi-lbl">Overall Score</div></div>
    <div class="kpi"><div class="kpi-val">${(brand.mentions || 0).toLocaleString()}</div><div class="kpi-lbl">Total Mentions</div></div>
    <div class="kpi"><div class="kpi-val" style="color:#d97706">${brand.rating}<span style="font-size:13px;color:#9ca3af">/5</span></div><div class="kpi-lbl">Avg Rating</div></div>
    <div class="kpi"><div class="kpi-val" style="color:${(brand.sentiment?.positive - brand.sentiment?.negative) >= 0 ? '#006c49' : '#ba1a1a'}">${(brand.sentiment?.positive - brand.sentiment?.negative) >= 0 ? '+' : ''}${brand.sentiment?.positive - brand.sentiment?.negative}</div><div class="kpi-lbl">Net Sentiment</div></div>
  </div>
</div>

${insight?.executive_summary ? `<div class="sec"><div class="sec-title">2. Executive Summary</div><div class="sum-box">${insight.executive_summary}</div></div>` : ''}

<div class="sec">
  <div class="sec-title">3. Sentiment Distribution</div>
  <div class="sent-row"><div class="sent-lbl"><span style="font-weight:600">Positive</span><span style="color:#6b7280">${positivePct}% (${sentPie[0].value.toLocaleString()})</span></div><div class="bar-bg"><div class="bar-fill" style="width:${positivePct}%;background:#6cf8bb"></div></div></div>
  <div class="sent-row"><div class="sent-lbl"><span style="font-weight:600">Neutral</span><span style="color:#6b7280">${neutralPct}% (${sentPie[1].value.toLocaleString()})</span></div><div class="bar-bg"><div class="bar-fill" style="width:${neutralPct}%;background:#718096"></div></div></div>
  <div class="sent-row"><div class="sent-lbl"><span style="font-weight:600">Negative</span><span style="color:#6b7280">${negativePct}% (${sentPie[2].value.toLocaleString()})</span></div><div class="bar-bg"><div class="bar-fill" style="width:${negativePct}%;background:#ffdad6"></div></div></div>
</div>

<div class="sec">
  <div class="sec-title">4. Aspect Satisfaction Analysis</div>
  ${aspectScores.map((a: any) => `<div class="asp-row"><div class="asp-lbl">${a.label}</div><div class="asp-bg"><div class="asp-fill" style="width:${a.score}%;background:${a.fill}"></div></div><div class="asp-pct">${a.score}%</div></div>`).join('')}
</div>

<div class="sec">
  <div class="sec-title">5. Top Complaint Themes</div>
  <table><thead><tr><th>Theme</th><th>Mentions</th></tr></thead><tbody>${topTopics.map((t: any) => `<tr><td>${t.name}</td><td><strong>${t.count}</strong></td></tr>`).join('')}</tbody></table>
</div>

${insight ? `<div class="sec"><div class="sec-title">6. Risks &amp; Opportunities</div><div class="r-grid"><div class="r-box risk"><div class="r-ttl risk">⚠ Top Risk</div><div class="r-txt risk">${insight.top_risk}</div></div><div class="r-box opp"><div class="r-ttl opp">↑ Opportunity</div><div class="r-txt opp">${insight.top_opportunity_summary || insight.top_opportunity || ''}</div></div></div></div>` : ''}

<div class="sec">
  <div class="sec-title">7. Recent Reviews Sample</div>
  ${feed.slice(0, 5).map((r: any) => `<div class="rev"><div class="rev-meta"><span class="rev-src">${r.source}</span><span class="badge ${r.sentiment_label}">${(r.sentiment_label || '').toUpperCase()}</span></div><div class="rev-txt">${r.cleaned_text}</div><div class="rev-dt">${r.post_date ? new Date(r.post_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '—'}</div></div>`).join('')}
</div>

<div class="sec">
  <div class="sec-title">8. Recommended Actions</div>
  ${recs.map((rec, i) => `<div class="rec-item"><div class="rec-num">${i + 1}</div><div>${rec}</div></div>`).join('')}
</div>

<div class="footer">Generated by SocialIntel AI Platform &nbsp;·&nbsp; ${new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</div>
<script>window.onload=function(){window.print()}</script>
</body>
</html>`;
}

// ─── Drawer: Full Amazon Report ─────────────────────────────────────────────
const AmazonReportDrawer: React.FC<{
  onClose: () => void;
  reportMeta: any;
}> = ({ onClose, reportMeta }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const drawerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [brandRes, aspectRes, topicRes, feedRes, insightRes] = await Promise.all([
          axios.get(`${API}/brands/${BRAND}`),
          axios.get(`${API}/aspects?brand=${BRAND}`),
          axios.get(`${API}/topics?brand=${BRAND}`),
          axios.get(`${API}/feed?brand=${BRAND}&limit=6`),
          axios.get(`${API}/insights?brand=${BRAND}`),
        ]);

        const brand = brandRes.data;
        const aspects = aspectRes.data;
        const topics = topicRes.data;
        const feed = feedRes.data.items || [];
        const insight = insightRes.data.insights?.[0];

        const aspectScores = Object.entries(ASPECT_LABELS).map(([key, label]) => {
          const d = aspects[key]?.[BRAND] || { positive: 0, neutral: 0, negative: 0 };
          const total = d.positive + d.neutral + d.negative;
          const score = total > 0 ? Math.round((d.positive / total) * 100) : 0;
          return { label, score, fill: score >= 50 ? '#006c49' : '#ba1a1a' };
        });

        const topTopics = (topics || []).slice(0, 6).map((t: any) => ({
          name: t.name,
          count: t[BRAND] || 0,
        }));

        const sentPie = [
          { name: 'Positive', value: brand.sentiment?.positive || 0 },
          { name: 'Neutral',  value: brand.sentiment?.neutral  || 0 },
          { name: 'Negative', value: brand.sentiment?.negative || 0 },
        ];

        setData({ brand, aspectScores, topTopics, sentPie, feed, insight });
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const exportAsPDF = () => {
    if (!data) return;
    const html = buildPrintHTML(data, reportMeta);
    const win = window.open('', '_blank');
    if (win) {
      win.document.write(html);
      win.document.close();
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40" onClick={onClose} />

      {/* Drawer */}
      <div
        ref={drawerRef}
        className="fixed right-0 top-0 bottom-0 w-[780px] z-50 bg-white shadow-2xl overflow-y-auto flex flex-col"
        style={{ animation: 'slideInRight 0.3s cubic-bezier(0.34,1.56,0.64,1)' }}
      >
        {/* Header */}
        <div className="sticky top-0 z-10 bg-white border-b border-outline-variant/20 px-8 py-5 flex items-center justify-between">
          <div>
            <h2 className="text-[20px] font-bold text-on-surface tracking-tight">Amazon Intelligence Report</h2>
            {reportMeta && (
              <p className="text-[13px] text-on-surface-variant mt-0.5">
                {formatReportType(reportMeta.report_type)} &nbsp;·&nbsp;{' '}
                {new Date(reportMeta.generated_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
              </p>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={exportAsPDF}
              disabled={loading || !data}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-on-primary rounded-full text-[13px] font-semibold shadow-sm hover:shadow-md disabled:opacity-40 transition-all"
            >
              <span className="material-symbols-outlined text-[16px]">picture_as_pdf</span>
              Export as PDF
            </button>
            <button onClick={onClose} className="w-9 h-9 flex items-center justify-center rounded-full hover:bg-surface-container transition-colors">
              <span className="material-symbols-outlined text-[20px] text-on-surface-variant">close</span>
            </button>
          </div>
        </div>

        {/* Body */}
        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-3">
              <div className="w-10 h-10 border-4 border-primary/30 border-t-primary rounded-full animate-spin mx-auto"></div>
              <p className="text-[14px] text-on-surface-variant">Loading report data...</p>
            </div>
          </div>
        ) : data ? (
          <div className="flex-1 px-8 py-6 space-y-10">

            {/* 1. KPI */}
            <section>
              <h3 className="section-title">1. KPI Scorecard</h3>
              <div className="grid grid-cols-4 gap-4 mt-4">
                {[
                  { label: 'Overall Score', value: `${data.brand.score}/100`, icon: 'grade', color: 'text-[#006c49]' },
                  { label: 'Total Mentions', value: data.brand.mentions?.toLocaleString(), icon: 'forum', color: 'text-primary' },
                  { label: 'Avg Rating', value: `${data.brand.rating}/5`, icon: 'star', color: 'text-amber-500' },
                  { label: 'Net Sentiment', value: `${((data.brand.sentiment?.positive || 0) - (data.brand.sentiment?.negative || 0)) >= 0 ? '+' : ''}${(data.brand.sentiment?.positive || 0) - (data.brand.sentiment?.negative || 0)}`, icon: 'sentiment_satisfied', color: 'text-blue-500' },
                ].map((kpi, i) => (
                  <div key={i} className="bg-surface-container/40 rounded-[12px] p-4 border border-outline-variant/20">
                    <span className={`material-symbols-outlined text-[22px] ${kpi.color}`}>{kpi.icon}</span>
                    <p className="text-[22px] font-bold text-on-surface mt-2">{kpi.value}</p>
                    <p className="text-[11px] text-on-surface-variant uppercase tracking-wider mt-1">{kpi.label}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* 2. Executive Summary */}
            {data.insight?.executive_summary && (
              <section>
                <h3 className="section-title">2. Executive Summary</h3>
                <div className="mt-4 bg-surface-container/40 border border-outline-variant/20 rounded-[12px] p-5">
                  <p className="text-[14px] text-on-surface leading-[1.8]">{data.insight.executive_summary}</p>
                </div>
              </section>
            )}

            {/* 3. Sentiment */}
            <section>
              <h3 className="section-title">3. Sentiment Distribution</h3>
              <div className="mt-4 grid grid-cols-2 gap-6 items-center">
                <div className="h-[200px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={data.sentPie} cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={3} dataKey="value">
                        {data.sentPie.map((_: any, i: number) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                      </Pie>
                      <Tooltip formatter={(v: any) => v.toLocaleString()} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-3">
                  {data.sentPie.map((s: any, i: number) => {
                    const total = data.sentPie.reduce((a: number, b: any) => a + b.value, 0);
                    const pct = total > 0 ? Math.round((s.value / total) * 100) : 0;
                    return (
                      <div key={i}>
                        <div className="flex justify-between text-[13px] mb-1">
                          <span className="font-medium">{s.name}</span>
                          <span className="text-on-surface-variant">{pct}% ({s.value.toLocaleString()})</span>
                        </div>
                        <div className="h-2 bg-surface-container rounded-full overflow-hidden">
                          <div className="h-full rounded-full" style={{ width: `${pct}%`, backgroundColor: PIE_COLORS[i] }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </section>

            {/* 4. Aspects */}
            <section>
              <h3 className="section-title">4. Aspect Satisfaction Analysis</h3>
              <div className="mt-4 h-[220px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.aspectScores} layout="vertical" margin={{ left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
                    <XAxis type="number" domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fontSize: 11 }} />
                    <YAxis dataKey="label" type="category" width={145} tick={{ fontSize: 12 }} />
                    <Tooltip formatter={(v: any) => `${v}%`} />
                    <Bar dataKey="score" radius={[0, 6, 6, 0]}>
                      {data.aspectScores.map((e: any, i: number) => <Cell key={i} fill={e.fill} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>

            {/* 5. Topics */}
            <section>
              <h3 className="section-title">5. Top Complaint Themes</h3>
              <div className="mt-4 h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.topTopics} margin={{ left: -10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={50} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#dae2fd" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>

            {/* 6. Risks */}
            {data.insight && (
              <section>
                <h3 className="section-title">6. Risks &amp; Opportunities</h3>
                <div className="mt-4 grid grid-cols-2 gap-4">
                  <div className="bg-[#ffdad6]/40 border border-[#ffdad6] rounded-[12px] p-5">
                    <p className="text-[11px] font-bold text-[#ba1a1a] mb-2 flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[14px]">error</span> Top Risk
                    </p>
                    <p className="text-[14px] text-[#410002] leading-[1.6]">{data.insight.top_risk}</p>
                  </div>
                  <div className="bg-[#6cf8bb]/30 border border-[#6cf8bb]/50 rounded-[12px] p-5">
                    <p className="text-[11px] font-bold text-[#006c49] mb-2 flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[14px]">trending_up</span> Opportunity
                    </p>
                    <p className="text-[14px] text-[#002116] leading-[1.6]">{data.insight.top_opportunity_summary || data.insight.top_opportunity}</p>
                  </div>
                </div>
              </section>
            )}

            {/* 7. Reviews */}
            <section>
              <h3 className="section-title">7. Recent Reviews Sample</h3>
              <div className="mt-4 space-y-3">
                {data.feed.map((r: any, i: number) => (
                  <div key={i} className="bg-surface-container/30 border border-outline-variant/20 rounded-[10px] p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wide">{r.source}</span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full" style={{ background: r.sentiment_label === 'positive' ? '#6cf8bb40' : r.sentiment_label === 'negative' ? '#ffdad640' : '#71809620', color: SENTIMENT_COLORS[r.sentiment_label] || '#4a5568' }}>
                        {r.sentiment_label?.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-[13px] text-on-surface leading-[1.6] line-clamp-3">{r.cleaned_text}</p>
                    <p className="text-[11px] text-on-surface-variant mt-2">
                      {r.post_date ? new Date(r.post_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '—'}
                    </p>
                  </div>
                ))}
                {data.feed.length === 0 && <p className="text-[13px] text-on-surface-variant text-center py-6">No recent reviews available.</p>}
              </div>
            </section>

            {/* 8. Recommendations */}
            <section>
              <h3 className="section-title">8. Recommended Actions</h3>
              <div className="mt-4 space-y-2">
                {['Prioritize fixing the AI search feature UX — it is the #1 complaint driver', 'Improve delivery reliability tracking notifications to reduce anxiety-related reviews', 'Streamline the returns & refunds process with clearer status updates', 'Invest in customer support response time and resolution quality', 'Leverage strong product quality perception in marketing campaigns'].map((rec, i) => (
                  <div key={i} className="flex items-start gap-3 text-[13px] text-on-surface leading-[1.6]">
                    <div className="w-5 h-5 rounded-full bg-[#6cf8bb]/30 border border-[#6cf8bb]/50 flex items-center justify-center shrink-0 mt-0.5">
                      <span className="material-symbols-outlined text-[12px] text-[#006c49]">check</span>
                    </div>
                    {rec}
                  </div>
                ))}
              </div>
            </section>

            <div className="border-t border-outline-variant/20 pt-6 text-center text-[12px] text-on-surface-variant">
              Generated by SocialIntel AI Platform &nbsp;·&nbsp; {new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-on-surface-variant text-[14px]">Failed to load report data.</div>
        )}
      </div>

      <style>{`
        @keyframes slideInRight { from{transform:translateX(100%);opacity:0} to{transform:translateX(0);opacity:1} }
        .section-title{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--color-on-surface-variant,#45464d);border-bottom:1px solid rgba(0,0,0,.06);padding-bottom:8px}
      `}</style>
    </>
  );
};

// ─── Reports Page ─────────────────────────────────────────────────────────
export const Reports: React.FC = () => {
  const [reports, setReports] = useState<any[]>([]);
  const [filteredReports, setFilteredReports] = useState<any[]>([]);
  const [filterText, setFilterText] = useState('');
  const [loading, setLoading] = useState(true);
  const [openReport, setOpenReport] = useState<any | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchReports = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/reports`);
      if (res.data.status === 'success') {
        setReports(res.data.reports);
        setFilteredReports(res.data.reports);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchReports(); }, [fetchReports]);

  useEffect(() => {
    if (!filterText.trim()) { setFilteredReports(reports); return; }
    const q = filterText.toLowerCase();
    setFilteredReports(reports.filter(r => r.report_type.toLowerCase().includes(q) || (r.summary || '').toLowerCase().includes(q)));
  }, [filterText, reports]);

  const handleRefresh = async () => { setRefreshing(true); await fetchReports(); setRefreshing(false); };

  return (
    <div className="relative min-h-screen pb-24 -mt-8 pt-4">
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-[26px] font-bold text-on-surface tracking-tight">Reports</h1>
            <p className="text-[14px] text-on-surface-variant mt-1.5">Generated intelligence reports with full HTML summaries and PDF export</p>
          </div>
          <button onClick={handleRefresh} disabled={refreshing} className="flex items-center gap-2 px-5 py-2.5 bg-white border border-outline-variant/30 rounded-full text-[13px] font-semibold text-on-surface shadow-sm hover:shadow-md disabled:opacity-50 transition-all">
            <span className={`material-symbols-outlined text-[18px] ${refreshing ? 'animate-spin' : ''}`}>sync</span>
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-3 bg-white border border-outline-variant/30 rounded-[10px] shadow-sm px-4">
          <span className="material-symbols-outlined text-[18px] text-on-surface-variant">search</span>
          <input type="text" placeholder="Filter reports by name or summary..." value={filterText} onChange={e => setFilterText(e.target.value)} className="w-full bg-transparent border-none py-3 text-[14px] text-on-surface placeholder:text-on-surface-variant focus:ring-0" />
          {filterText && <button onClick={() => setFilterText('')} className="text-on-surface-variant hover:text-on-surface"><span className="material-symbols-outlined text-[16px]">close</span></button>}
        </div>

        {/* Table */}
        <div className="bg-white rounded-[16px] shadow-[0_10px_15px_-3px_rgba(0,0,0,0.05)] border border-white/50 overflow-hidden">
          <div className="grid grid-cols-12 gap-4 px-6 py-4 border-b border-outline-variant/20 text-[11px] font-bold text-on-surface-variant uppercase tracking-widest bg-surface-container/20">
            <div className="col-span-3">Report Type</div>
            <div className="col-span-4">Summary</div>
            <div className="col-span-2">Generated At</div>
            <div className="col-span-3 text-right">Actions</div>
          </div>

          {loading ? (
            <div>{[0,1,2].map(i => <div key={i} className="px-6 py-5 border-b border-outline-variant/10 animate-pulse"><div className="grid grid-cols-12 gap-4"><div className="col-span-3 h-5 bg-surface-container rounded"></div><div className="col-span-4 h-4 bg-surface-container rounded"></div><div className="col-span-2 h-4 bg-surface-container rounded"></div><div className="col-span-3 h-8 bg-surface-container rounded-full ml-auto w-32"></div></div></div>)}</div>
          ) : filteredReports.length === 0 ? (
            <div className="text-center py-20 text-on-surface-variant">
              <span className="material-symbols-outlined text-[56px] mb-3 block opacity-20">description</span>
              <p className="text-[15px] font-medium">{filterText ? `No reports matching "${filterText}"` : 'No reports generated yet.'}</p>
              <p className="text-[13px] mt-1 opacity-70">Run the pipeline to generate intelligence reports.</p>
            </div>
          ) : (
            filteredReports.map((report, idx) => (
              <div key={idx} className="grid grid-cols-12 gap-4 px-6 py-5 border-b border-outline-variant/10 items-center hover:bg-surface-container/20 transition-colors last:border-b-0">
                <div className="col-span-3 flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#dae2fd]/50 rounded-[10px] flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-[20px] text-primary">monitoring</span>
                  </div>
                  <div>
                    <p className="text-[14px] font-semibold text-on-surface leading-snug">{formatReportType(report.report_type)}</p>
                    <span className="inline-block px-2 py-0.5 mt-1 bg-[#6cf8bb]/30 text-[#006c49] text-[10px] font-bold uppercase rounded-[4px]">Amazon</span>
                  </div>
                </div>
                <div className="col-span-4 text-[13px] text-on-surface-variant leading-[1.6] line-clamp-2 pr-4">{report.summary || '—'}</div>
                <div className="col-span-2">
                  <p className="text-[13px] text-on-surface font-medium">{new Date(report.generated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</p>
                  <p className="text-[12px] text-on-surface-variant/70">{new Date(report.generated_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</p>
                </div>
                <div className="col-span-3 flex items-center justify-end gap-2">
                  <button onClick={() => setOpenReport(report)} className="flex items-center gap-2 px-4 py-2 bg-primary text-on-primary rounded-full text-[12px] font-semibold shadow-sm hover:shadow-md transition-all">
                    <span className="material-symbols-outlined text-[15px]">open_in_full</span>
                    View Report
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {!loading && <p className="text-[13px] text-on-surface-variant">Showing {filteredReports.length} of {reports.length} report{reports.length !== 1 ? 's' : ''}</p>}
      </div>

      {openReport && <AmazonReportDrawer reportMeta={openReport} onClose={() => setOpenReport(null)} />}
    </div>
  );
};
