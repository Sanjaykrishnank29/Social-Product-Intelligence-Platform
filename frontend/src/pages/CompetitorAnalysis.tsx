import React, { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';

export const CompetitorAnalysis: React.FC = () => {
  const { comparison, aspects, loading, error, fetchComparison, fetchAspects, brandsList, fetchBrandsList } = useStore();
  const [selectedBrands, setSelectedBrands] = useState<string[]>(['amazon', 'flipkart']);

  useEffect(() => {
    fetchBrandsList();
    fetchAspects();
  }, [fetchBrandsList, fetchAspects]);

  useEffect(() => {
    if (selectedBrands.length > 0) {
      fetchComparison(selectedBrands.join(','));
    }
  }, [selectedBrands, fetchComparison]);

  const toggleBrand = (brand: string) => {
    if (brand === 'amazon') return; // Amazon is the fixed primary benchmark
    setSelectedBrands(prev => 
      prev.includes(brand) 
        ? prev.filter(b => b !== brand)
        : [...prev, brand].slice(0, 4) // Limit to max 4 brands
    );
  };

  const getMetricDisplayValue = (val: any) => {
    if (typeof val === 'number') {
      if (val < 1) {
        return `${(val * 100).toFixed(1)}%`;
      }
      return val.toLocaleString();
    }
    return val;
  };

  if (loading && !comparison) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-on-surface-variant font-body-md text-[16px]">
        <span className="material-symbols-outlined animate-spin text-[32px] text-primary mb-4">progress_activity</span>
        <p>Loading competitor analysis...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-error-container/20 text-error p-6 rounded-[16px] neumorphic-card border border-error/30 text-center font-body-md text-[16px]">
        <p>Error loading comparison: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-12">
      <div className="bg-surface-container-lowest p-container-padding rounded-[16px] neumorphic-card border border-white/50">
        <h2 className="font-headline-md text-[24px] text-on-surface mb-6 flex items-center gap-2 font-semibold">
          <span className="material-symbols-outlined text-primary">filter_list</span>
          Select Brands to Compare (Max 4)
        </h2>
        <div className="flex flex-wrap gap-3">
          {brandsList.map(brand => {
            const isAmazon = brand === 'amazon';
            return (
              <button
                key={brand}
                onClick={() => toggleBrand(brand)}
                className={`px-4 py-2 rounded-full font-label-md transition-colors flex items-center gap-2 ${
                  isAmazon 
                    ? 'bg-primary/20 text-primary border border-primary/50 cursor-not-allowed' 
                    : selectedBrands.includes(brand) 
                      ? 'bg-surface-container-highest text-on-surface border border-outline-variant' 
                      : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container-high border border-transparent'
                }`}
                title={isAmazon ? "Amazon is the primary baseline" : `Compare against ${brand}`}
              >
                {isAmazon && <span className="material-symbols-outlined text-[16px]">verified</span>}
                {brand.charAt(0).toUpperCase() + brand.slice(1)}
              </button>
            );
          })}
        </div>
      </div>

      {/* Comparison Metrics */}
      {comparison?.metrics && comparison.metrics.length > 0 && (
        <div className="bg-surface-container-lowest p-container-padding rounded-[16px] neumorphic-card border border-white/50">
          <h2 className="font-headline-md text-[24px] text-on-surface mb-6 flex items-center gap-2 font-semibold">
            <span className="material-symbols-outlined text-primary">bar_chart</span>
            Brand In-Depth Comparison
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead className="bg-surface-container-low text-[14px] text-on-surface-variant uppercase tracking-wider font-label-md">
                <tr>
                  <th className="p-4 border-b border-outline-variant/30 font-semibold">Comparison Metric</th>
                  {Object.keys(comparison.metrics[0])
                    .filter(k => k !== 'name' && k !== 'unit')
                    .map((brandKey) => (
                      <th key={brandKey} className="p-4 border-b border-outline-variant/30 font-semibold capitalize text-on-surface">
                        {brandKey}
                      </th>
                    ))}
                  <th className="p-4 border-b border-outline-variant/30 font-semibold text-right">Unit</th>
                </tr>
              </thead>
              <tbody className="text-[16px] text-on-surface font-body-md">
                {comparison.metrics.map((metric: any, index: number) => {
                  const brandKeys = Object.keys(metric).filter(k => k !== 'name' && k !== 'unit');
                  return (
                    <tr key={index} className="border-b border-outline-variant/20 last:border-0 hover:bg-surface-container-low/50 transition-colors">
                      <td className="p-4 font-semibold text-on-surface-variant">{metric.name}</td>
                      {brandKeys.map((brandKey) => (
                        <td key={brandKey} className="p-4 font-bold text-on-surface">
                          {getMetricDisplayValue(metric[brandKey])}
                        </td>
                      ))}
                      <td className="p-4 text-right text-[12px] text-on-surface-variant font-label-sm">{metric.unit}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Aspect-Based Sentiment Analysis (ABSA) */}
      {aspects && Object.keys(aspects).length > 0 && (
        <div className="bg-surface-container-lowest p-container-padding rounded-[16px] neumorphic-card border border-white/50">
          <h2 className="font-headline-md text-[24px] text-on-surface mb-6 flex items-center gap-2 font-semibold">
            <span className="material-symbols-outlined text-primary">pie_chart</span>
            Aspect Sentiment Comparison (ABSA)
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead className="bg-surface-container-low text-[14px] text-on-surface-variant uppercase tracking-wider font-label-md">
                <tr>
                  <th className="p-4 border-b border-outline-variant/30 font-semibold">Aspect Category</th>
                  {selectedBrands.map((brandKey) => (
                    <th key={brandKey} className="p-4 border-b border-outline-variant/30 font-semibold capitalize text-on-surface">
                      {brandKey} Sentiment
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="text-[16px] text-on-surface font-body-md">
                {Object.keys(aspects).map((key: string) => {
                  const aspectName = key.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
                  return (
                    <tr key={key} className="border-b border-outline-variant/20 last:border-0 hover:bg-surface-container-low/50 transition-colors">
                      <td className="p-4 font-semibold text-on-surface-variant">{aspectName}</td>
                      {selectedBrands.map((brandKey) => {
                        const brandData = aspects[key]?.[brandKey];
                        const sumVal = brandData ? brandData.summary : 'N/A';
                        let badgeClass = "bg-surface text-on-surface-variant border-outline-variant/30";
                        if (sumVal === 'positive') badgeClass = "bg-secondary-container/20 text-secondary border-secondary/30";
                        if (sumVal === 'negative') badgeClass = "bg-error-container/20 text-error border-error/30";
                        
                        return (
                          <td key={brandKey} className="p-4">
                            <span className={`px-3 py-1 rounded-full text-[12px] font-label-sm font-semibold border uppercase tracking-wider ${badgeClass}`}>
                              {sumVal}
                            </span>
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
