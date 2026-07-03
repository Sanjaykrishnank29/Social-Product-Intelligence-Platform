import React, { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';

export const RawFeed: React.FC = () => {
  const { feed, feedTotal, loading, error, fetchFeed } = useStore();
  
  const [brand, setBrand] = useState('all');
  const [sentiment, setSentiment] = useState('all');
  const [source, setSource] = useState('all');
  const [page, setPage] = useState(1);
  const limit = 10;

  useEffect(() => {
    fetchFeed(brand, sentiment, source, page);
  }, [fetchFeed, brand, sentiment, source, page]);

  const handleBrandChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setBrand(e.target.value);
    setPage(1); // Reset to page 1
  };

  const handleSourceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSource(e.target.value);
    setPage(1); // Reset to page 1
  };

  const handleSentimentChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSentiment(e.target.value);
    setPage(1); // Reset to page 1
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const totalPages = Math.ceil(feedTotal / limit);

  return (
    <div className="space-y-8">
      {/* Filters Bar */}
      <div className="flex flex-wrap gap-4 items-center bg-surface-container-lowest p-4 rounded-[16px] neumorphic-card border border-white/50">
        <div className="flex items-center gap-2 text-on-surface-variant font-label-md">
          <span className="material-symbols-outlined text-[20px]">filter_list</span>
          <span>Filters:</span>
        </div>
        
        <select 
          className="bg-surface-container border border-outline-variant/30 text-on-surface text-[14px] rounded-full px-4 py-2 focus:ring-2 focus:ring-primary/20 focus:outline-none transition-all cursor-pointer font-body-md" 
          value={brand} 
          onChange={handleBrandChange}
        >
          <option value="all">All Brands</option>
          <option value="amazon">Amazon</option>
          <option value="flipkart">Flipkart</option>
          <option value="meesho">Meesho</option>
          <option value="myntra">Myntra</option>
        </select>

        <select 
          className="bg-surface-container border border-outline-variant/30 text-on-surface text-[14px] rounded-full px-4 py-2 focus:ring-2 focus:ring-primary/20 focus:outline-none transition-all cursor-pointer font-body-md" 
          value={source} 
          onChange={handleSourceChange}
        >
          <option value="all">All Sources</option>
          <option value="playstore">Play Store</option>
          <option value="reddit">Reddit</option>
          <option value="google_news">Google News</option>
          <option value="trustpilot">Trustpilot</option>
          <option value="google_store">Google Store</option>
        </select>

        <select 
          className="bg-surface-container border border-outline-variant/30 text-on-surface text-[14px] rounded-full px-4 py-2 focus:ring-2 focus:ring-primary/20 focus:outline-none transition-all cursor-pointer font-body-md" 
          value={sentiment} 
          onChange={handleSentimentChange}
        >
          <option value="all">All Sentiments</option>
          <option value="positive">Positive</option>
          <option value="neutral">Neutral</option>
          <option value="negative">Negative</option>
        </select>
      </div>

      {/* Error/Loading */}
      {error && (
        <div className="bg-error-container/20 text-error p-6 rounded-[16px] neumorphic-card border border-error/30 text-center font-body-md text-[16px]">
          <p>Failed to load reviews feed: {error}</p>
        </div>
      )}

      {loading && feed.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-on-surface-variant font-body-md text-[16px]">
          <span className="material-symbols-outlined animate-spin text-[32px] text-primary mb-4">progress_activity</span>
          <p>Loading reviews feed...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Reviews List */}
          <div className="bg-surface-container-lowest p-container-padding rounded-[16px] neumorphic-card border border-white/50">
            <h3 className="font-headline-md text-[24px] text-on-surface mb-6 font-semibold flex items-center gap-2">
              <span className="material-symbols-outlined text-primary">forum</span> Latest Reviews Feed
            </h3>
            <div className="space-y-4 max-h-[800px] overflow-y-auto pr-4 custom-scrollbar">
              {feed.length === 0 ? (
                <div className="text-center p-12 text-on-surface-variant italic font-body-md text-[16px]">
                  No reviews found matching the filters.
                </div>
              ) : (
                feed.map((review) => {
                  let sentimentClass = "bg-surface text-on-surface-variant";
                  if (review.sentiment_label === 'positive') sentimentClass = "bg-secondary-container text-on-secondary-container";
                  if (review.sentiment_label === 'neutral') sentimentClass = "bg-tertiary-fixed text-on-tertiary-fixed-variant";
                  if (review.sentiment_label === 'negative') sentimentClass = "bg-error-container text-on-error-container";

                  return (
                    <div key={review.id} className="p-gutter bg-surface-container-low rounded-xl border border-white/20 hover:border-primary/20 transition-all">
                      <div className="flex justify-between items-start mb-3 flex-wrap gap-2">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary-fixed flex items-center justify-center text-primary font-bold text-[16px] border border-white">
                            {review.author ? review.author[0].toUpperCase() : '?'}
                          </div>
                          <div>
                            <p className="font-label-md text-[14px] font-semibold text-on-surface">{review.author || 'Anonymous'}</p>
                            <p className="font-label-sm text-[12px] text-on-surface-variant flex items-center gap-1">
                              <span className="material-symbols-outlined text-[14px]">schedule</span>
                              {formatDate(review.post_date)} • {review.source}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-3 py-1 rounded-full font-label-sm text-[12px] font-bold uppercase tracking-wider border border-white/40 ${sentimentClass}`}>
                            {review.sentiment_label}
                          </span>
                          <span className="px-3 py-1 bg-surface-container text-on-surface-variant rounded-full font-label-sm text-[12px] font-semibold uppercase tracking-wider border border-white/40">
                            {review.brand}
                          </span>
                        </div>
                      </div>
                      <p className="font-body-md text-[16px] text-on-surface-variant italic leading-relaxed">"{review.cleaned_text}"</p>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-4 bg-surface-container-lowest p-4 rounded-[16px] neumorphic-card border border-white/50">
              <button 
                className={`neumorphic-button px-6 py-2 rounded-full font-label-md text-[14px] flex items-center gap-2 ${page === 1 || loading ? 'opacity-50 cursor-not-allowed bg-surface text-on-surface-variant' : 'bg-surface text-on-surface hover:bg-surface-container-high'}`}
                onClick={() => setPage(prev => Math.max(prev - 1, 1))}
                disabled={page === 1 || loading}
              >
                <span className="material-symbols-outlined text-[18px]">chevron_left</span> Previous
              </button>
              <span className="font-label-md text-[14px] text-on-surface-variant font-medium">
                Page {page} of {totalPages} <span className="opacity-60 ml-1">({feedTotal} total)</span>
              </span>
              <button 
                className={`neumorphic-button px-6 py-2 rounded-full font-label-md text-[14px] flex items-center gap-2 ${page === totalPages || loading ? 'opacity-50 cursor-not-allowed bg-surface text-on-surface-variant' : 'bg-surface text-on-surface hover:bg-surface-container-high'}`}
                onClick={() => setPage(prev => Math.min(prev + 1, totalPages))}
                disabled={page === totalPages || loading}
              >
                Next <span className="material-symbols-outlined text-[18px]">chevron_right</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
