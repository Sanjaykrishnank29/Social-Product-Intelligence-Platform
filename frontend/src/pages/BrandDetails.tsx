import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useStore } from '../store/useStore';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Mock Data provided by User for charts
const sentimentTrendData = [
  { week: 'Week 1', positive: 48, negative: 32 },
  { week: 'Week 2', positive: 51, negative: 30 },
  { week: 'Week 3', positive: 53, negative: 28 },
  { week: 'Week 4', positive: 56, negative: 25 },
  { week: 'Week 5', positive: 58, negative: 23 },
  { week: 'Week 6', positive: 61, negative: 20 },
];

const aspectData = [
  { aspect: 'Delivery', score: 92 },
  { aspect: 'Product Quality', score: 88 },
  { aspect: 'Returns', score: 84 },
  { aspect: 'Pricing', score: 75 },
  { aspect: 'Customer Support', score: 61 },
];

const topicData = [
  { topic: 'Refund Delays', mentions: 148 },
  { topic: 'Customer Support', mentions: 121 },
  { topic: 'Damaged Products', mentions: 96 },
  { topic: 'Late Delivery', mentions: 82 },
  { topic: 'App Performance', mentions: 54 },
];

export const BrandDetails: React.FC = () => {
  const brand = 'amazon';
  const [details, setDetails] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [searchQuery, setSearchQuery] = useState('');

  const { searchResults, searchFeed } = useStore();

  useEffect(() => {
    const fetchDetails = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get(`http://localhost:8001/api/v1/brands/${brand}`);
        setDetails(response.data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch brand details');
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
    searchFeed('', brand, 'all', 'all', 1);
  }, [brand, searchFeed]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    searchFeed(searchQuery, brand, 'all', 'all', 1);
  };

  if (loading && !details) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-on-surface-variant font-body-md text-[16px]">
        <span className="material-symbols-outlined animate-spin text-[32px] text-primary mb-4">progress_activity</span>
        <p>Loading Amazon Intelligence Dashboard...</p>
      </div>
    );
  }

  if (error || !details) {
    return (
      <div className="bg-error-container/20 text-error p-6 rounded-[16px] neumorphic-card border border-error/30 text-center font-body-md text-[16px]">
        <p>Error loading dashboard: {error}</p>
      </div>
    );
  }

  // Calculate Net Sentiment
  const posCount = details.sentiment?.positive || 0;
  const negCount = details.sentiment?.negative || 0;
  const totalSent = posCount + negCount + (details.sentiment?.neutral || 0);
  const netSentiment = totalSent > 0 ? Math.round(((posCount - negCount) / totalSent) * 100) : 0;
  const netSentimentDisplay = netSentiment > 0 ? `+${netSentiment}%` : `${netSentiment}%`;

  return (
    <div className="space-y-12 pb-12">
      {/* Header Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display-xl text-[48px] font-extrabold text-on-surface capitalize tracking-tight flex items-center gap-4">
            <span className="material-symbols-outlined text-[40px] text-primary">storefront</span>
            Amazon Intelligence
          </h1>
          <p className="text-on-surface-variant font-body-lg text-[18px] mt-2">
            Amazon Health Dashboard
          </p>
        </div>
      </div>

      {/* Section 1: KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-card-gap">
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50 flex flex-col justify-center items-center text-center">
          <span className="material-symbols-outlined text-primary mb-2 text-[28px]">stars</span>
          <h2 className="font-display-lg text-[32px] font-bold text-on-surface leading-none">{details.score}<span className="text-[14px] text-on-surface-variant font-normal">/100</span></h2>
          <p className="text-on-surface-variant font-label-sm uppercase tracking-wider mt-1">Overall Score</p>
        </div>
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50 flex flex-col justify-center items-center text-center">
          <span className="material-symbols-outlined text-secondary mb-2 text-[28px]">forum</span>
          <h2 className="font-display-lg text-[32px] font-bold text-on-surface leading-none">{details.mentions.toLocaleString()}</h2>
          <p className="text-on-surface-variant font-label-sm uppercase tracking-wider mt-1">Mentions</p>
        </div>
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50 flex flex-col justify-center items-center text-center">
          <span className="material-symbols-outlined text-tertiary mb-2 text-[28px]">star_rate</span>
          <h2 className="font-display-lg text-[32px] font-bold text-on-surface leading-none">{details.rating}<span className="text-[14px] text-on-surface-variant font-normal">/5</span></h2>
          <p className="text-on-surface-variant font-label-sm uppercase tracking-wider mt-1">Rating</p>
        </div>
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50 flex flex-col justify-center items-center text-center">
          <span className="material-symbols-outlined text-secondary mb-2 text-[28px]">thumbs_up_down</span>
          <h2 className="font-display-lg text-[32px] font-bold text-on-surface leading-none">{netSentimentDisplay}</h2>
          <p className="text-on-surface-variant font-label-sm uppercase tracking-wider mt-1">Net Sentiment</p>
        </div>
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50 flex flex-col justify-center items-center text-center">
          <span className="material-symbols-outlined text-secondary mb-2 text-[28px]">trending_up</span>
          <h2 className="font-display-lg text-[32px] font-bold text-secondary leading-none">Improving</h2>
          <p className="text-on-surface-variant font-label-sm uppercase tracking-wider mt-1">Weekly Trend</p>
        </div>
      </div>

      {/* Section 2: Executive Summary */}
      <div className="bg-primary-container/20 p-6 rounded-[16px] neumorphic-card border border-primary/30">
        <h3 className="font-headline-sm flex items-center gap-2 text-primary mb-3">
          <span className="material-symbols-outlined">analytics</span> Executive Summary
        </h3>
        <p className="text-on-surface font-body-lg text-[18px] leading-relaxed">
          {details.executive_summary}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Section 3: Sentiment Trend */}
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50">
          <h3 className="font-headline-sm flex items-center gap-2 text-on-surface mb-6">
            <span className="material-symbols-outlined text-primary">show_chart</span> Sentiment Trend
          </h3>
          <p className="text-sm text-on-surface-variant mb-6 italic">Weekly sentiment distribution over the last six weeks.</p>
          <div className="w-full h-[300px]">
            <ResponsiveContainer>
              <LineChart data={sentimentTrendData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-surface-container-highest)" vertical={false} />
                <XAxis dataKey="week" stroke="var(--color-on-surface-variant)" tick={{fill: 'var(--color-on-surface-variant)', fontSize: 12}} />
                <YAxis stroke="var(--color-on-surface-variant)" tick={{fill: 'var(--color-on-surface-variant)', fontSize: 12}} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--color-surface-container-lowest)', borderColor: 'var(--color-outline-variant)', borderRadius: '8px' }} />
                <Legend />
                <Line type="monotone" dataKey="positive" stroke="var(--color-secondary)" strokeWidth={3} dot={{r: 4, fill: 'var(--color-secondary)'}} activeDot={{r: 6}} name="Positive" />
                <Line type="monotone" dataKey="negative" stroke="var(--color-error)" strokeWidth={3} dot={{r: 4, fill: 'var(--color-error)'}} activeDot={{r: 6}} name="Negative" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Section 4: Aspect Analysis */}
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50">
          <h3 className="font-headline-sm flex items-center gap-2 text-on-surface mb-6">
            <span className="material-symbols-outlined text-tertiary">assessment</span> Aspect Satisfaction
          </h3>
          <p className="text-sm text-on-surface-variant mb-6 italic">Positive sentiment score by customer experience aspect.</p>
          <div className="w-full h-[300px]">
            <ResponsiveContainer>
              <BarChart layout="vertical" data={aspectData} margin={{ top: 5, right: 30, left: 30, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-surface-container-highest)" horizontal={false} />
                <XAxis type="number" stroke="var(--color-on-surface-variant)" tick={{fill: 'var(--color-on-surface-variant)'}} domain={[0, 100]} />
                <YAxis dataKey="aspect" type="category" stroke="var(--color-on-surface-variant)" tick={{fill: 'var(--color-on-surface)', fontWeight: 600, fontSize: 12}} width={120} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--color-surface-container-lowest)', borderColor: 'var(--color-outline-variant)', borderRadius: '8px' }} cursor={{fill: 'var(--color-surface-container-low)'}} />
                <Bar dataKey="score" fill="var(--color-tertiary)" radius={[0, 4, 4, 0]} barSize={24} name="Satisfaction Score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Section 5: Topic Intelligence */}
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50">
          <h3 className="font-headline-sm flex items-center gap-2 text-on-surface mb-6">
            <span className="material-symbols-outlined text-error">report_problem</span> Top Complaint Topics
          </h3>
          <p className="text-sm text-on-surface-variant mb-6 italic">Most frequently mentioned negative topics in Amazon reviews.</p>
          <div className="w-full h-[300px]">
            <ResponsiveContainer>
              <BarChart layout="vertical" data={topicData} margin={{ top: 5, right: 30, left: 30, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-surface-container-highest)" horizontal={false} />
                <XAxis type="number" stroke="var(--color-on-surface-variant)" tick={{fill: 'var(--color-on-surface-variant)'}} />
                <YAxis dataKey="topic" type="category" stroke="var(--color-on-surface-variant)" tick={{fill: 'var(--color-on-surface)', fontWeight: 600, fontSize: 12}} width={130} />
                <Tooltip contentStyle={{ backgroundColor: 'var(--color-surface-container-lowest)', borderColor: 'var(--color-outline-variant)', borderRadius: '8px' }} cursor={{fill: 'var(--color-surface-container-low)'}} />
                <Bar dataKey="mentions" fill="var(--color-error)" radius={[0, 4, 4, 0]} barSize={24} name="Mentions" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Section 6: Alerts & Risks */}
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50 flex flex-col">
          <h3 className="font-headline-sm flex items-center gap-2 text-on-surface mb-6">
            <span className="material-symbols-outlined text-primary">notifications_active</span> Alerts & Risks
          </h3>
          <div className="flex-grow space-y-4">
            {details.recent_alerts && details.recent_alerts.length > 0 ? (
              details.recent_alerts.map((alert: any) => {
                const isHigh = alert.severity === 'high';
                const isMedium = alert.severity === 'medium';
                return (
                  <div key={alert.id} className={`p-4 rounded-xl border flex gap-3 items-start ${
                    isHigh ? 'bg-error-container/10 border-error/30' : 
                    isMedium ? 'bg-primary-container/10 border-primary/30' : 
                    'bg-secondary-container/10 border-secondary/30'
                  }`}>
                    <div className={`mt-0.5 ${
                      isHigh ? 'text-error' : isMedium ? 'text-primary' : 'text-secondary'
                    }`}>
                      <span className="material-symbols-outlined text-[20px]">
                        {isHigh ? 'error' : isMedium ? 'warning' : 'info'}
                      </span>
                    </div>
                    <div>
                      <p className="text-[15px] text-on-surface font-medium leading-tight mb-1">{alert.message}</p>
                      <span className="text-[12px] text-on-surface-variant opacity-80">{alert.timestamp ? new Date(alert.timestamp).toLocaleDateString() : 'Recent'}</span>
                    </div>
                  </div>
                )
              })
            ) : (
              <p className="text-on-surface-variant text-[14px]">No active alerts for Amazon.</p>
            )}
          </div>
        </div>
      </div>

      {/* Section 7: Recent Reviews */}
      <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50">
        <h3 className="font-headline-sm flex items-center gap-2 text-on-surface mb-6">
          <span className="material-symbols-outlined text-secondary">forum</span> Recent Reviews
        </h3>
        
        <form onSubmit={handleSearch} className="relative w-full max-w-2xl mb-6">
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search Amazon reviews..."
            className="w-full bg-surface-container-low border border-outline-variant/30 rounded-full py-3 px-12 focus:ring-2 focus:ring-primary/20 text-[16px] text-on-surface placeholder:text-on-surface-variant transition-all shadow-sm"
          />
          <span className="material-symbols-outlined absolute left-4 top-3.5 text-on-surface-variant">search</span>
          <button type="submit" className="absolute right-2 top-2 bg-primary hover:bg-primary/90 text-on-primary px-4 py-1.5 rounded-full font-label-md transition-colors">
            Search
          </button>
        </form>

        <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
          {searchResults && searchResults.length > 0 ? (
            searchResults.map((review: any) => (
              <div key={review.id} className="p-4 bg-surface-container-low rounded-xl border border-white/20">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className="text-[12px] text-on-surface-variant font-label-sm px-2 py-1 bg-surface rounded-full border border-outline-variant/30">{review.source || 'Review'}</span>
                    <span className="text-[12px] text-on-surface-variant">{review.post_date ? new Date(review.post_date).toLocaleString() : ''}</span>
                  </div>
                </div>
                <p className="text-[14px] text-on-surface leading-relaxed" dangerouslySetInnerHTML={{ __html: `"${review.highlight || review.cleaned_text}"` }}></p>
                <div className="mt-3 flex gap-2">
                  <span className={`px-2 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider ${
                    review.sentiment_label === 'positive' ? 'bg-secondary-container/30 text-secondary' :
                    review.sentiment_label === 'negative' ? 'bg-error-container/30 text-error' :
                    'bg-outline-variant/20 text-on-surface-variant'
                  }`}>
                    {review.sentiment_label || 'Unscored'}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <p className="text-on-surface-variant text-[14px]">No reviews found for Amazon.</p>
          )}
        </div>
      </div>
    </div>
  );
};
