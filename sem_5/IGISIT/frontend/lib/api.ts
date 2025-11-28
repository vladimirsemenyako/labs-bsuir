import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Dataset {
  filename: string;
  title: string;
}

export interface DatasetInfo {
  filename: string;
  title: string;
  has_entities: boolean;
  entities: string[];
  entity_type: string;
  indicators: string[];
  categories?: string[];
  category_entities?: Record<string, string[]>;
  year_range: [number, number];
}

export interface TimeSeriesPoint {
  year: number;
  value: number;
}

export interface ForecastPoint {
  year: number;
  forecast: number;
  lower: number;
  upper: number;
}

export interface ForecastResponse {
  historical: TimeSeriesPoint[];
  forecast: ForecastPoint[];
  method: string;
}

export interface WaterFeature {
  name: string;
  lat: number;
  lon: number;
  color: string;
}

export const api = {
  async getDatasets(): Promise<Dataset[]> {
    const response = await axios.get(`${API_BASE_URL}/api/datasets`);
    return response.data.datasets;
  },

  async getDatasetInfo(filename: string): Promise<DatasetInfo> {
    const response = await axios.get(`${API_BASE_URL}/api/dataset/${filename}`);
    return response.data;
  },

  async getForecast(
    filename: string,
    entity?: string,
    indicator?: string,
    category?: string,
    periods: number = 10
  ): Promise<ForecastResponse> {
    const response = await axios.post(`${API_BASE_URL}/api/forecast`, {
      filename,
      entity,
      indicator,
      category,
      periods,
    });
    return response.data;
  },

  async getEntityData(
    filename: string,
    year: number,
    indicator?: string,
    category?: string
  ): Promise<{
    entities: Record<string, number>;
    type: string;
    year: number;
    requested_year?: number;
    categories?: string[];
  }> {
    const params = new URLSearchParams();
    if (indicator) params.append('indicator', indicator);
    if (category) params.append('category', category);
    const query = params.toString();
    const url = query
      ? `${API_BASE_URL}/api/entity-data/${filename}/${year}?${query}`
      : `${API_BASE_URL}/api/entity-data/${filename}/${year}`;
    const response = await axios.get(url);
    return response.data;
  },

  async getWaterFeatures(category: string): Promise<WaterFeature[]> {
    const response = await axios.get(`${API_BASE_URL}/api/water/features`, {
      params: { category },
    });
    return response.data.features;
  },

  async getWaterGeoJSON(category: string): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/api/water/geojson`, {
      params: { category },
    });
    return response.data;
  },

  async getTimeSeries(
    filename: string,
    entity?: string,
    indicator?: string,
    category?: string
  ): Promise<TimeSeriesPoint[]> {
    const params = new URLSearchParams();
    if (entity) params.append('entity', entity);
    if (indicator) params.append('indicator', indicator);
    if (category) params.append('category', category);
    
    const response = await axios.get(`${API_BASE_URL}/api/timeseries/${filename}?${params}`);
    return response.data.data;
  },
};

