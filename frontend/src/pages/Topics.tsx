import React, { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export const Topics: React.FC = () => {
  const { topics, loading, error, fetchTopics } = useStore();
  const [expandedTopic, setExpandedTopic] = useState<string | null>(null);

  useEffect(() => {
    fetchTopics();
  }, [fetchTopics]);

  if (loading && topics.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-on-surface-variant font-body-md text-[16px]">
        <span className="material-symbols-outlined animate-spin text-[32px] text-primary mb-4">progress_activity</span>
        <p>Analyzing semantic complaint themes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-error-container/20 text-error p-6 rounded-[16px] neumorphic-card border border-error/30 text-center font-body-md text-[16px]">
        <p>Error loading themes: {error}</p>
      </div>
    );
  }

  const chartData = topics.map(t => {
    const row: any = { name: t.name };
    Object.keys(t).forEach((k) => {
      if (k !== 'name' && k !== 'samples') {
        const capKey = k.charAt(0).toUpperCase() + k.slice(1);
        row[capKey] = t[k];
      }
    });
    return row;
  });

  const toggleExpand = (topicName: string) => {
    if (expandedTopic === topicName) {
      setExpandedTopic(null);
    } else {
      setExpandedTopic(topicName);
    }
  };

  const activeBrands = topics.length > 0 
    ? Object.keys(topics[0]).filter(k => k !== 'name' && k !== 'samples')
    : [];

  return (
    <div className="space-y-12">
      {/* Chart Section */}
      <div className="bg-surface-container-lowest p-container-padding rounded-[16px] neumorphic-card border border-white/50">
        <h2 className="font-headline-md text-[24px] text-on-surface mb-6 flex items-center gap-2 font-semibold">
          <span className="material-symbols-outlined text-primary">bar_chart</span>
          Topic Volume Comparison
        </h2>
        <div className="w-full h-[400px]">
          <ResponsiveContainer>
            <BarChart
              layout="vertical"
              data={chartData}
              margin={{ top: 20, right: 30, left: 10, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-surface-container-highest)" />
              <XAxis type="number" stroke="var(--color-on-surface-variant)" />
              <YAxis dataKey="name" type="category" stroke="var(--color-on-surface-variant)" width={180} style={{ fontSize: '14px', fontFamily: 'Outfit' }} />
              <Tooltip
                contentStyle={{ backgroundColor: 'var(--color-surface-container-lowest)', borderColor: 'var(--color-outline-variant)', color: 'var(--color-on-surface)', borderRadius: '8px' }}
              />
              <Legend />
              {activeBrands.map((brandKey) => {
                const capitalizedBrand = brandKey.charAt(0).toUpperCase() + brandKey.slice(1);
                const brandColors: any = {
                  amazon: '#ff9900',
                  flipkart: '#2874f0',
                  meesho: '#e71d73',
                  myntra: '#ff3f6c'
                };
                const color = brandColors[brandKey.toLowerCase()] || 'var(--color-primary)';
                return (
                  <Bar 
                    key={brandKey} 
                    dataKey={capitalizedBrand} 
                    fill={color}
                    radius={[0, 4, 4, 0]} 
                  />
                );
              })}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Topics Grid */}
      <section>
        <h2 className="font-headline-md text-[24px] text-on-surface mb-6 flex items-center gap-2 font-semibold">
          <span className="material-symbols-outlined text-primary">grid_view</span>
          Discovered Themes Detail
        </h2>
        <div className="grid grid-cols-1 gap-6">
          {topics.map((topic, index) => {
            const isExpanded = expandedTopic === topic.name;
            const brandKeys = Object.keys(topic).filter(k => k !== 'name' && k !== 'samples');
            const totalCount = brandKeys.reduce((sum, k) => sum + (topic[k] || 0), 0);
            return (
              <div key={index} className="bg-surface-container-lowest p-6 rounded-[16px] neumorphic-card border border-white/50 flex flex-col gap-4 transition-all duration-300">
                <div className="flex justify-between items-center flex-wrap gap-4">
                  <div>
                    <h3 className="font-title-lg text-[20px] font-semibold text-on-surface tracking-tight">{topic.name}</h3>
                    <span className="font-label-sm text-[12px] text-on-surface-variant">
                      Total Clustered Mentions: <strong className="text-on-surface">{totalCount}</strong>
                    </span>
                  </div>
                  <div className="flex gap-3 items-center flex-wrap">
                    {brandKeys.map((brandKey) => {
                      const val = topic[brandKey];
                      const capBrand = brandKey.charAt(0).toUpperCase() + brandKey.slice(1);
                      return (
                        <span key={brandKey} className="px-3 py-1 bg-surface-container text-on-surface-variant rounded-full font-label-sm text-[12px] font-semibold uppercase tracking-wider border border-white/40">
                          {capBrand}: {val}
                        </span>
                      );
                    })}
                    <button
                      onClick={() => toggleExpand(topic.name)}
                      className="neumorphic-button flex items-center gap-1 bg-surface text-on-surface px-4 py-2 rounded-lg font-label-md text-[14px] border border-white/40 hover:bg-surface-container-high transition-colors"
                    >
                      {isExpanded ? (
                        <><span className="material-symbols-outlined text-[18px]">expand_less</span> Hide Samples</>
                      ) : (
                        <><span className="material-symbols-outlined text-[18px]">expand_more</span> View Samples</>
                      )}
                    </button>
                  </div>
                </div>

                {isExpanded && (
                  <div className="mt-2 pt-4 border-t border-outline-variant/20 flex flex-col gap-3 animate-in fade-in slide-in-from-top-4 duration-300">
                    <h4 className="font-label-md text-[14px] font-semibold text-on-surface-variant flex items-center gap-1">
                      <span className="material-symbols-outlined text-[18px]">notes</span> Sample Reviews:
                    </h4>
                    {topic.samples.length === 0 ? (
                      <p className="text-on-surface-variant italic font-body-md text-[14px]">No samples available.</p>
                    ) : (
                      topic.samples.map((sample: any, sIdx: number) => {
                        let sentimentClass = "bg-surface text-on-surface-variant";
                        if (sample.sentiment === 'positive') sentimentClass = "bg-secondary-container text-on-secondary-container";
                        if (sample.sentiment === 'neutral') sentimentClass = "bg-tertiary-fixed text-on-tertiary-fixed-variant";
                        if (sample.sentiment === 'negative') sentimentClass = "bg-error-container text-on-error-container";

                        return (
                          <div
                            key={sIdx}
                            className="bg-surface-container-low border border-white/20 rounded-xl p-4 font-body-md text-[14px] leading-relaxed"
                          >
                            <div className="flex justify-between items-center mb-2">
                              <span className="px-2 py-0.5 bg-surface-container text-on-surface-variant rounded font-label-sm text-[10px] font-bold uppercase tracking-wider border border-white/40">
                                {sample.brand}
                              </span>
                              <span className={`px-2 py-0.5 rounded font-label-sm text-[10px] font-bold uppercase tracking-wider border border-white/40 ${sentimentClass}`}>
                                {sample.sentiment}
                              </span>
                            </div>
                            <p className="text-on-surface italic">"{sample.text}"</p>
                          </div>
                        )
                      })
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
};
