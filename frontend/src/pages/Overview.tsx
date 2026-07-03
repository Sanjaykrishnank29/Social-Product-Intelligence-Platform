import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useStore } from '../store/useStore';

export const Overview: React.FC = () => {
  const [details, setDetails] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { feed, fetchFeed } = useStore();

  useEffect(() => {
    const fetchAmazonDetails = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get(`http://localhost:8001/api/v1/brands/amazon`);
        setDetails(response.data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch Amazon details');
      } finally {
        setLoading(false);
      }
    };

    fetchAmazonDetails();
    fetchFeed('amazon', 'all', 'all', 1);
  }, [fetchFeed]);

  if (loading && !details) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-on-surface-variant font-body-md text-[16px]">
        <span className="material-symbols-outlined animate-spin text-[32px] text-primary mb-4">progress_activity</span>
        <p>Loading Amazon intelligence...</p>
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

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display-xl text-[48px] font-extrabold text-on-surface capitalize tracking-tight flex items-center gap-4">
            <span className="material-symbols-outlined text-[40px] text-primary">dashboard</span>
            Amazon Intelligence Overview
          </h1>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-card-gap">
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50 flex flex-col justify-center items-center text-center">
          <span className="material-symbols-outlined text-primary mb-2 text-[28px]">stars</span>
          <h2 className="font-display-lg text-[36px] font-bold text-on-surface leading-none">{details.score}<span className="text-[16px] text-on-surface-variant font-normal">/100</span></h2>
          <p className="text-on-surface-variant font-label-md uppercase tracking-wider mt-1">Overall Score</p>
        </div>
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50 flex flex-col justify-center items-center text-center">
          <span className="material-symbols-outlined text-secondary mb-2 text-[28px]">forum</span>
          <h2 className="font-display-lg text-[36px] font-bold text-on-surface leading-none">{details.mentions.toLocaleString()}</h2>
          <p className="text-on-surface-variant font-label-md uppercase tracking-wider mt-1">Total Mentions</p>
        </div>
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50 flex flex-col justify-center items-center text-center">
          <span className="material-symbols-outlined text-tertiary mb-2 text-[28px]">star_rate</span>
          <h2 className="font-display-lg text-[36px] font-bold text-on-surface leading-none">{details.rating}<span className="text-[16px] text-on-surface-variant font-normal">/5</span></h2>
          <p className="text-on-surface-variant font-label-md uppercase tracking-wider mt-1">Average Rating</p>
        </div>
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50 flex flex-col justify-center items-center text-center">
          <span className="material-symbols-outlined text-secondary mb-2 text-[28px]">trending_up</span>
          <h2 className="font-display-lg text-[36px] font-bold text-secondary leading-none">↑ 8%</h2>
          <p className="text-on-surface-variant font-label-md uppercase tracking-wider mt-1">Weekly Trend</p>
        </div>
      </div>

      {/* Executive Summary Card */}
      <div className="bg-primary-container/20 p-6 rounded-[16px] neumorphic-card border border-primary/30">
        <h3 className="font-headline-sm flex items-center gap-2 text-primary mb-3">
          <span className="material-symbols-outlined">analytics</span> Executive Summary
        </h3>
        <p className="text-on-surface font-body-lg text-[18px] leading-relaxed">
          {details.executive_summary}
        </p>
      </div>

      {/* Insights Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-card-gap">
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-error/50">
          <h3 className="font-headline-sm flex items-center gap-2 text-error mb-4">
            <span className="material-symbols-outlined">warning</span> Top Risk
          </h3>
          <p className="text-on-surface font-body-md leading-relaxed">{details.top_risk}</p>
        </div>
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-secondary/50">
          <h3 className="font-headline-sm flex items-center gap-2 text-secondary mb-4">
            <span className="material-symbols-outlined">lightbulb</span> Top Opportunity
          </h3>
          <p className="text-on-surface font-body-md leading-relaxed">{details.top_opportunity}</p>
        </div>
      </div>

      {/* Bottom Row: Alerts and Reviews */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-card-gap">
        {/* Active Alerts */}
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50">
          <h3 className="font-headline-sm flex items-center gap-2 text-on-surface mb-4">
            <span className="material-symbols-outlined text-error">notifications_active</span> Active Alerts
          </h3>
          <div className="space-y-4">
            {details.recent_alerts && details.recent_alerts.length > 0 ? (
              details.recent_alerts.map((alert: any) => (
                <div key={alert.id} className="p-4 bg-surface-container-low rounded-xl border border-white/20">
                  <div className="flex items-center justify-between mb-2">
                    <span className={`px-2 py-1 text-[10px] uppercase font-bold tracking-wider rounded-md ${
                      alert.severity === 'high' ? 'bg-error/20 text-error' : 
                      alert.severity === 'medium' ? 'bg-primary/20 text-primary' : 
                      'bg-surface-container-high text-on-surface-variant'
                    }`}>
                      {alert.severity}
                    </span>
                    <span className="text-[12px] text-on-surface-variant">{alert.timestamp ? new Date(alert.timestamp).toLocaleDateString() : ''}</span>
                  </div>
                  <p className="text-[14px] text-on-surface">{alert.message}</p>
                </div>
              ))
            ) : (
              <p className="text-on-surface-variant text-[14px]">No active alerts for Amazon.</p>
            )}
          </div>
        </div>

        {/* Recent Reviews */}
        <div className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50">
          <h3 className="font-headline-sm flex items-center gap-2 text-on-surface mb-4">
            <span className="material-symbols-outlined text-secondary">forum</span> Recent Reviews
          </h3>
          <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
            {feed && feed.length > 0 ? (
              feed.slice(0, 5).map((review: any) => (
                <div key={review.id} className="p-4 bg-surface-container-low rounded-xl border border-white/20">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[12px] text-on-surface-variant font-label-sm px-2 py-1 bg-surface rounded-full border border-outline-variant/30">{review.source || 'Review'}</span>
                    <span className="text-[12px] text-on-surface-variant">{new Date(review.post_date).toLocaleDateString()}</span>
                  </div>
                  <p className="text-[14px] text-on-surface italic leading-relaxed">"{review.cleaned_text}"</p>
                  <div className="mt-3 flex gap-2">
                    <span className={`px-2 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider ${
                      review.sentiment_label === 'positive' ? 'bg-secondary/20 text-secondary' :
                      review.sentiment_label === 'negative' ? 'bg-error/20 text-error' :
                      'bg-outline-variant/20 text-on-surface-variant'
                    }`}>
                      {review.sentiment_label || 'Unscored'}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-on-surface-variant text-[14px]">No recent reviews found.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
