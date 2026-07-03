import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API = 'http://localhost:8001/api/v1';

export const Alerts: React.FC = () => {
  const [emails, setEmails] = useState<string[]>(['ceo@company.com']);
  const [inputValue, setInputValue] = useState('');
  const [sending, setSending] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{type: 'success'|'error', text: string} | null>(null);

  const [recentAlerts, setRecentAlerts] = useState<any[]>([]);

  useEffect(() => {
    // Fetch recent alerts to display history
    axios.get(`${API}/alerts`).then(res => {
      if (res.data.status === 'success') {
        setRecentAlerts(res.data.alerts);
      }
    }).catch(console.error);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addEmail();
    }
  };

  const addEmail = () => {
    const val = inputValue.trim();
    if (val && val.includes('@') && !emails.includes(val)) {
      setEmails([...emails, val]);
      setInputValue('');
    }
  };

  const removeEmail = (emailToRemove: string) => {
    setEmails(emails.filter(e => e !== emailToRemove));
  };

  const sendAlerts = async () => {
    if (emails.length === 0) {
      setStatusMsg({ type: 'error', text: 'Please add at least one recipient email address.' });
      return;
    }
    
    setSending(true);
    setStatusMsg(null);
    try {
      const res = await axios.post(`${API}/alerts/send`, { emails });
      if (res.data.status === 'success') {
        setStatusMsg({ type: 'success', text: res.data.message });
      } else {
        setStatusMsg({ type: 'error', text: res.data.message });
      }
    } catch (e: any) {
      setStatusMsg({ type: 'error', text: e.response?.data?.message || e.message || 'Failed to send emails' });
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      <div>
        <h1 className="text-[26px] font-bold text-on-surface tracking-tight">Alerts & Notifications</h1>
        <p className="text-[14px] text-on-surface-variant mt-1.5 leading-relaxed">
          Manage your monitored intelligence rules and email notification recipients.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Monitored Rules Section */}
        <div className="space-y-4">
          <h2 className="text-[18px] font-semibold text-on-surface">Active Alert Rules</h2>
          <div className="space-y-3">
            {[
              { title: 'Sentiment Drop', desc: 'Triggers when net sentiment drops below 50% over a 24h period.', severity: 'High', color: 'text-[#ba1a1a]', bg: 'bg-[#ffdad6]/30' },
              { title: 'Topic Surge', desc: 'Triggers when a negative topic volume increases by >300%.', severity: 'High', color: 'text-[#ba1a1a]', bg: 'bg-[#ffdad6]/30' },
              { title: 'Competitor Mention', desc: 'Triggers when users strongly compare the brand to a rival.', severity: 'Medium', color: 'text-amber-600', bg: 'bg-amber-100/30' }
            ].map((rule, idx) => (
              <div key={idx} className="bg-white border border-outline-variant/30 rounded-[12px] p-4 shadow-sm flex gap-4 items-start">
                <div className={`w-10 h-10 rounded-[10px] flex items-center justify-center shrink-0 ${rule.bg}`}>
                  <span className={`material-symbols-outlined text-[20px] ${rule.color}`}>notifications_active</span>
                </div>
                <div>
                  <h3 className="text-[14px] font-bold text-on-surface flex items-center gap-2">
                    {rule.title}
                    <span className={`text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wide font-bold border border-current ${rule.color}`}>
                      {rule.severity}
                    </span>
                  </h3>
                  <p className="text-[13px] text-on-surface-variant mt-1 leading-snug">{rule.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Email Management & Action */}
        <div className="space-y-4">
          <h2 className="text-[18px] font-semibold text-on-surface">Email Recipients</h2>
          <div className="bg-white border border-outline-variant/30 rounded-[12px] p-6 shadow-sm space-y-6">
            <div>
              <label className="block text-[13px] font-semibold text-on-surface-variant mb-2">Recipient Email Addresses</label>
              
              <div className="min-h-[100px] border border-outline-variant/50 rounded-[8px] p-2 flex flex-wrap gap-2 items-start bg-surface-container-lowest focus-within:border-primary focus-within:ring-1 focus-within:ring-primary transition-all cursor-text" onClick={() => document.getElementById('email-input')?.focus()}>
                {emails.map((email) => (
                  <div key={email} className="flex items-center gap-1 bg-primary/10 text-primary px-3 py-1.5 rounded-full text-[13px] font-medium border border-primary/20">
                    {email}
                    <button onClick={() => removeEmail(email)} className="hover:text-[#ba1a1a] transition-colors ml-1 flex items-center">
                      <span className="material-symbols-outlined text-[14px] block">close</span>
                    </button>
                  </div>
                ))}
                <input
                  id="email-input"
                  type="email"
                  className="flex-1 min-w-[150px] bg-transparent border-none text-[13px] text-on-surface py-1.5 px-2 focus:ring-0 outline-none"
                  placeholder="Type email and press Enter..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  onBlur={addEmail}
                />
              </div>
              <p className="text-[11px] text-on-surface-variant mt-2">Add email addresses to receive instant or daily alert summaries.</p>
            </div>

            <button
              onClick={sendAlerts}
              disabled={sending || emails.length === 0}
              className="w-full flex items-center justify-center gap-2 bg-primary text-on-primary py-3 rounded-full text-[14px] font-bold shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className={`material-symbols-outlined text-[18px] ${sending ? 'animate-spin' : ''}`}>
                {sending ? 'sync' : 'send'}
              </span>
              {sending ? 'Sending Emails...' : 'Send Alert Mail Now'}
            </button>

            {statusMsg && (
              <div className={`p-4 rounded-[8px] text-[13px] font-medium flex items-center gap-2 ${statusMsg.type === 'error' ? 'bg-[#ffdad6]/40 text-[#ba1a1a] border border-[#ffdad6]' : 'bg-[#6cf8bb]/30 text-[#006c49] border border-[#6cf8bb]/50'}`}>
                <span className="material-symbols-outlined text-[18px]">
                  {statusMsg.type === 'error' ? 'error' : 'check_circle'}
                </span>
                {statusMsg.text}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Alert History */}
      <div className="mt-8 pt-8 border-t border-outline-variant/20">
        <h2 className="text-[18px] font-semibold text-on-surface mb-4">Recent Alert History</h2>
        <div className="bg-white border border-outline-variant/30 rounded-[12px] shadow-sm overflow-hidden">
          {recentAlerts.length === 0 ? (
            <div className="p-8 text-center text-on-surface-variant text-[14px]">No recent alerts found.</div>
          ) : (
            <table className="w-full text-left">
              <thead className="bg-surface-container/20 text-[11px] font-bold text-on-surface-variant uppercase tracking-widest border-b border-outline-variant/20">
                <tr>
                  <th className="py-3 px-6">Timestamp</th>
                  <th className="py-3 px-6">Brand</th>
                  <th className="py-3 px-6">Severity</th>
                  <th className="py-3 px-6">Alert Details</th>
                </tr>
              </thead>
              <tbody className="text-[13px] text-on-surface divide-y divide-outline-variant/10">
                {recentAlerts.slice(0, 10).map((a) => (
                  <tr key={a.id} className="hover:bg-surface-container/20 transition-colors">
                    <td className="py-4 px-6 text-on-surface-variant whitespace-nowrap">
                      {a.timestamp ? new Date(a.timestamp).toLocaleString() : 'N/A'}
                    </td>
                    <td className="py-4 px-6 font-semibold uppercase">{a.brand}</td>
                    <td className="py-4 px-6">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${a.severity.toLowerCase() === 'high' ? 'bg-[#ffdad6]/40 text-[#ba1a1a]' : 'bg-amber-100/50 text-amber-700'}`}>
                        {a.severity}
                      </span>
                    </td>
                    <td className="py-4 px-6 leading-snug">
                      <strong className="block mb-0.5">{a.alert_type.replace(/_/g, ' ').toUpperCase()}</strong>
                      <span className="text-on-surface-variant">{a.message}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};
