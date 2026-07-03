import { create } from 'zustand';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api/v1';

interface State {
  brandsList: string[];
  overview: any;
  sentiment: any;
  comparison: any;
  aspects: any;
  topics: any[];
  feed: any[];
  feedTotal: number;
  searchResults: any[];
  searchTotal: number;
  loading: boolean;
  error: string | null;
  fetchBrandsList: () => Promise<void>;
  fetchOverview: () => Promise<void>;
  fetchSentiment: (brand?: string) => Promise<void>;
  fetchComparison: (brands: string) => Promise<void>;
  fetchAspects: (brand?: string) => Promise<void>;
  fetchTopics: (brand?: string) => Promise<void>;
  fetchFeed: (brand?: string, sentiment?: string, source?: string, page?: number) => Promise<void>;
  searchFeed: (query: string, brand?: string, sentiment?: string, source?: string, page?: number) => Promise<void>;
}

export const useStore = create<State>((set) => ({
  brandsList: [],
  overview: null,
  sentiment: null,
  comparison: null,
  aspects: null,
  topics: [],
  feed: [],
  feedTotal: 0,
  searchResults: [],
  searchTotal: 0,
  loading: false,
  error: null,

  fetchBrandsList: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/brands`);
      set({ brandsList: response.data.brands || [] });
    } catch (err: any) {
      console.error('Failed to fetch brands list', err);
    }
  },

  fetchOverview: async () => {
    set({ loading: true, error: null });
    try {
      const response = await axios.get(`${API_BASE_URL}/overview`);
      set({ overview: response.data, loading: false });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch overview', loading: false });
    }
  },

  fetchSentiment: async (brand) => {
    set({ loading: true, error: null });
    try {
      const url = brand ? `${API_BASE_URL}/sentiment?brand=${brand}` : `${API_BASE_URL}/sentiment`;
      const response = await axios.get(url);
      set({ sentiment: response.data, loading: false });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch sentiment stats', loading: false });
    }
  },

  fetchComparison: async (brands) => {
    set({ loading: true, error: null });
    try {
      const response = await axios.get(`${API_BASE_URL}/compare?brands=${brands}`);
      set({ comparison: response.data, loading: false });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch brand comparison', loading: false });
    }
  },

  fetchAspects: async (brand) => {
    set({ loading: true, error: null });
    try {
      const url = brand ? `${API_BASE_URL}/aspects?brand=${brand}` : `${API_BASE_URL}/aspects`;
      const response = await axios.get(url);
      set({ aspects: response.data, loading: false });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch aspects metrics', loading: false });
    }
  },

  fetchFeed: async (brand, sentiment, source, page = 1) => {
    set({ loading: true, error: null });
    const limit = 10;
    const skip = (page - 1) * limit;
    
    let url = `${API_BASE_URL}/feed?limit=${limit}&skip=${skip}`;
    if (brand && brand !== 'all') url += `&brand=${brand}`;
    if (sentiment && sentiment !== 'all') url += `&sentiment=${sentiment}`;
    if (source && source !== 'all') url += `&source=${source}`;
    
    try {
      const response = await axios.get(url);
      set({ 
        feed: response.data.items, 
        feedTotal: response.data.total,
        loading: false 
      });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch feed reviews', loading: false });
    }
  },

  fetchTopics: async (brand) => {
    set({ loading: true, error: null });
    try {
      const url = brand ? `${API_BASE_URL}/topics?brand=${brand}` : `${API_BASE_URL}/topics`;
      const response = await axios.get(url);
      set({ topics: response.data, loading: false });
    } catch (err: any) {
      set({ error: err.message || 'Failed to fetch topics', loading: false });
    }
  },

  searchFeed: async (query, brand, sentiment, source, page = 1) => {
    set({ loading: true, error: null });
    const limit = 10;
    const skip = (page - 1) * limit;
    
    let url = `${API_BASE_URL}/search?q=${encodeURIComponent(query)}&limit=${limit}&skip=${skip}`;
    if (brand && brand !== 'all') url += `&brand=${brand}`;
    if (sentiment && sentiment !== 'all') url += `&sentiment=${sentiment}`;
    if (source && source !== 'all') url += `&source=${source}`;
    
    try {
      const response = await axios.get(url);
      set({ 
        searchResults: response.data.items, 
        searchTotal: response.data.total,
        loading: false 
      });
    } catch (err: any) {
      set({ error: err.message || 'Failed to search reviews', loading: false });
    }
  }
}));

