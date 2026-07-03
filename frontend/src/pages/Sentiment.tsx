import React, { useEffect } from 'react';
import { useStore } from '../store/useStore';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts';

export const Sentiment: React.FC = () => {
  const { sentiment, loading, error, fetchSentiment } = useStore();

  useEffect(() => {
    fetchSentiment();
  }, [fetchSentiment]);

  if (loading && !sentiment) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-on-surface-variant font-body-md text-[16px]">
        <span className="material-symbols-outlined animate-spin text-[32px] text-primary mb-4">progress_activity</span>
        <p>Loading sentiment stats...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-error-container/20 text-error p-6 rounded-[16px] neumorphic-card border border-error/30 text-center font-body-md text-[16px]">
        <p>Error loading sentiment stats: {error}</p>
      </div>
    );
  }

  // Parse sentiment data dynamically for BarChart
  const getBarChartData = () => {
    if (!sentiment) return [];
    
    return ['Positive', 'Neutral', 'Negative'].map((label) => {
      const key = label.toLowerCase();
      const row: any = { name: label };
      Object.keys(sentiment).forEach((brandKey) => {
        const capitalizedBrand = brandKey.charAt(0).toUpperCase() + brandKey.slice(1);
        row[capitalizedBrand] = sentiment[brandKey]?.[key] || 0;
      });
      return row;
    });
  };

  const getPieChartData = (brandKey: string) => {
    if (!sentiment || !sentiment[brandKey]) return [];
    const brandData = sentiment[brandKey];
    
    return [
      { name: 'Positive', value: brandData.positive || 0, color: 'var(--color-secondary)' },
      { name: 'Neutral', value: brandData.neutral || 0, color: 'var(--color-outline)' },
      { name: 'Negative', value: brandData.negative || 0, color: 'var(--color-error)' }
    ].filter(item => item.value > 0);
  };

  const barData = getBarChartData();
  const activeBrands = sentiment ? Object.keys(sentiment) : [];

  return (
    <div className="space-y-12">
      {/* Comparative Bar Chart */}
      <div className="bg-surface-container-lowest p-container-padding rounded-[16px] neumorphic-card border border-white/50">
        <h2 className="font-headline-md text-[24px] text-on-surface mb-6 flex items-center gap-2 font-semibold">
          <span className="material-symbols-outlined text-primary">analytics</span>
          Brand Sentiment Comparison
        </h2>
        <div className="w-full h-[350px]">
          <ResponsiveContainer>
            <BarChart
              data={barData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-surface-container-highest)" />
              <XAxis dataKey="name" stroke="var(--color-on-surface-variant)" />
              <YAxis stroke="var(--color-on-surface-variant)" />
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--color-surface-container-lowest)', borderColor: 'var(--color-outline-variant)', color: 'var(--color-on-surface)', borderRadius: '8px' }}
              />
              <Legend />
              {activeBrands.map((brandKey) => {
                const capitalizedBrand = brandKey.charAt(0).toUpperCase() + brandKey.slice(1);
                // Assigning colors based on standard dashboard colors
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
                    radius={[8, 8, 0, 0]} 
                  />
                );
              })}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Pie Charts Side by Side */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-card-gap">
        {activeBrands.map((brandKey) => {
          const brandName = brandKey.charAt(0).toUpperCase() + brandKey.slice(1);
          const pieData = getPieChartData(brandKey);
          return (
            <div key={brandKey} className="bg-surface-container-lowest p-gutter rounded-[16px] neumorphic-card border border-white/50 flex flex-col items-center">
              <h2 className="font-title-lg text-[20px] text-on-surface mb-4 font-semibold w-full text-center">
                {brandName}
              </h2>
              <div className="w-full h-[260px]">
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                    >
                      {pieData.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)' }}/>
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
