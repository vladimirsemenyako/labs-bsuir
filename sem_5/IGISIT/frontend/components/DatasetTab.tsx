import { useState, useEffect, useMemo } from 'react';
import useSWR from 'swr';
import { api, Dataset, DatasetInfo, WaterFeature } from '@/lib/api';
import WaterMap from './WaterMap';
import TimeSeriesChart from './TimeSeriesChart';
import YearSlider from './YearSlider';

interface DatasetTabProps {
  dataset: Dataset;
}

const CATEGORY_ORDER = ['Реки', 'Подземные воды'];
const SECTION_TABS = [
  { id: 'map', label: 'Карта' },
  { id: 'forecast', label: 'Прогноз' },
  { id: 'table', label: 'Таблица' },
] as const;
const MAP_DATASET_FILENAME = 'C11-2005-2024.csv';

export default function DatasetTab({ dataset }: DatasetTabProps) {
  const { data: info } = useSWR<DatasetInfo>(`/api/dataset/${dataset.filename}`, () =>
    api.getDatasetInfo(dataset.filename)
  );

  const [selectedYear, setSelectedYear] = useState<number>(2024);
  const [forecastYears, setForecastYears] = useState<number>(12);
  const [selectedEntity, setSelectedEntity] = useState<string>('');
  const [selectedIndicator, setSelectedIndicator] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [activeSection, setActiveSection] = useState<'map' | 'forecast' | 'table'>('map');

  const isMapDataset = dataset.filename === MAP_DATASET_FILENAME;
  const filteredCategories = info?.categories?.filter((category) => category !== 'Озера') ?? [];
  const categoriesKey = filteredCategories.join('|');

  const sortedCategories = useMemo(() => {
    if (!filteredCategories.length) {
      return [];
    }
    return [...filteredCategories].sort((a, b) => {
      const ai = CATEGORY_ORDER.indexOf(a);
      const bi = CATEGORY_ORDER.indexOf(b);
      return (ai === -1 ? CATEGORY_ORDER.length : ai) - (bi === -1 ? CATEGORY_ORDER.length : bi);
    });
  }, [categoriesKey]);

  useEffect(() => {
    if (!info?.year_range) {
      return;
    }
    const [minYear, maxYear] = info.year_range;
    if (selectedYear < minYear || selectedYear > maxYear) {
      setSelectedYear(maxYear);
    }
  }, [info?.year_range?.[0], info?.year_range?.[1]]);

  useEffect(() => {
    if (!sortedCategories.length) {
      return;
    }
    if (!selectedCategory || !sortedCategories.includes(selectedCategory)) {
      setSelectedCategory(sortedCategories[0]);
    }
  }, [sortedCategories, selectedCategory]);

  useEffect(() => {
    setSelectedEntity('');
  }, [selectedCategory]);

  useEffect(() => {
    const defaultSection: 'map' | 'forecast' | 'table' = isMapDataset ? 'map' : 'forecast';
    setActiveSection(defaultSection);
    setSelectedIndicator('');
    setSelectedEntity('');
    setSelectedCategory('');
  }, [dataset.filename, isMapDataset]);

  const indicatorKey = selectedIndicator || 'auto';
  const entityKey = selectedEntity || 'all';
  const categoryKey = selectedCategory || 'all';
  const hasCategories = sortedCategories.length > 0;
  const effectiveCategory = hasCategories
    ? selectedCategory
    : info?.entity_type === 'river'
    ? 'Реки'
    : '';
  const requestCategory = hasCategories ? selectedCategory || undefined : undefined;

  const fetchWaterFeatures = (_: string, category: string) => api.getWaterFeatures(category);
  const fetchWaterGeoJSON = (_: string, category: string) => api.getWaterGeoJSON(category);

  const { data: waterFeatures } = useSWR<WaterFeature[]>(
    isMapDataset && effectiveCategory ? ['/water/features', effectiveCategory] : null,
    fetchWaterFeatures
  );

  const { data: waterGeoJSON } = useSWR(
    isMapDataset && effectiveCategory ? ['/water/geojson', effectiveCategory] : null,
    fetchWaterGeoJSON
  );

  const { data: entityData } = useSWR(
    isMapDataset && info && effectiveCategory
      ? `/api/entity-data/${dataset.filename}/${selectedYear}/${indicatorKey}/${categoryKey}`
      : null,
    () =>
      api.getEntityData(
        dataset.filename,
        selectedYear,
        selectedIndicator || undefined,
        requestCategory
      )
  );

  const { data: forecastData } = useSWR(
    info
      ? `/api/forecast/${dataset.filename}/${entityKey}/${indicatorKey}/${categoryKey}/${forecastYears}`
      : null,
    () =>
      api.getForecast(
        dataset.filename,
        selectedEntity || undefined,
        selectedIndicator || undefined,
        requestCategory,
        forecastYears
      )
  );

  if (!info) {
    return (
      <div className="flex items-center justify-center h-80 bg-white/5 border border-white/10 rounded-3xl backdrop-blur-xl">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-cyan-400 border-t-transparent"></div>
      </div>
    );
  }

  const availableEntities = hasCategories
    ? info.category_entities?.[selectedCategory] ?? []
    : info.entities ?? [];
  const totalEntities = availableEntities.length || info.entities?.length || 0;
  const hasEntityValues = !!entityData && Object.keys(entityData.entities || {}).length > 0;
  const canRenderMap = isMapDataset && !!effectiveCategory && waterFeatures && waterGeoJSON;
  const indicatorLabel =
    selectedIndicator && selectedIndicator.length > 50
      ? `${selectedIndicator.substring(0, 50)}...`
      : selectedIndicator;
  const chartTitle = [
    dataset.title,
    selectedCategory && hasCategories ? selectedCategory : '',
    selectedEntity,
    indicatorLabel,
  ]
    .filter(Boolean)
    .join(' | ');
  const resolvedDataYear = isMapDataset ? entityData?.year ?? null : null;
  const requestedDataYear = isMapDataset ? entityData?.requested_year ?? selectedYear : null;
  const mapYearMismatch =
    resolvedDataYear !== null &&
    requestedDataYear !== null &&
    resolvedDataYear !== requestedDataYear;
  const visibleSections = isMapDataset ? SECTION_TABS : SECTION_TABS.filter((tab) => tab.id !== 'map');

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap gap-3">
        {visibleSections.map((section) => {
          const isActive = activeSection === section.id;
          return (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`px-4 py-2 rounded-2xl text-sm font-semibold transition-all duration-300 ${
                isActive
                  ? 'bg-cyan-400/90 text-slate-900 shadow-lg shadow-cyan-500/30'
                  : 'bg-white/10 border border-white/20 text-slate-200 hover:bg-white/20'
              }`}
            >
              {section.label}
            </button>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {isMapDataset && activeSection === 'map' && (
            <div className="bg-white/10 border border-white/20 rounded-3xl p-6 backdrop-blur-2xl shadow-2xl transition-all">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-semibold text-white">
                  Карта - {effectiveCategory || 'Реки'}
                </h3>
                {!hasEntityValues && (
                  <span className="text-sm text-white/60">Нет данных для визуализации</span>
                )}
              </div>
              {mapYearMismatch && (
                <p className="text-xs text-amber-200 mb-3">
                  Нет данных за {requestedDataYear}. Показаны значения {resolvedDataYear}.
                </p>
              )}
              {canRenderMap && waterFeatures && waterGeoJSON && entityData ? (
                <WaterMap
                  category={effectiveCategory}
                  features={waterFeatures}
                  entityData={entityData.entities || {}}
                  geojson={waterGeoJSON}
                  title={dataset.title}
                />
              ) : (
                <div className="h-[420px] flex items-center justify-center text-white/70 border border-dashed border-white/30 rounded-2xl">
                  Выберите другую категорию или показатель.
                </div>
              )}
            </div>
          )}

          {activeSection === 'forecast' && (
            <div className="bg-white/10 border border-white/15 rounded-3xl p-6 backdrop-blur-2xl shadow-2xl min-h-[420px]">
              {forecastData ? (
                <TimeSeriesChart
                  historical={forecastData.historical}
                  forecast={forecastData.forecast}
                  title={chartTitle}
                  selectedYear={selectedYear}
                />
              ) : (
                <div className="flex items-center justify-center h-72 text-white/70">
                  Недостаточно данных для построения прогноза
                </div>
              )}
            </div>
          )}
          {activeSection === 'table' && (
            <div className="bg-white/10 border border-white/15 rounded-3xl p-6 backdrop-blur-2xl shadow-2xl">
              {forecastData ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-4">Исторические значения</h3>
                    <div className="max-h-96 overflow-y-auto rounded-2xl border border-white/10">
                      <table className="min-w-full text-sm text-white/90 divide-y divide-white/10">
                        <thead className="bg-white/10 uppercase text-xs tracking-wider">
                          <tr>
                            <th className="px-4 py-2 text-left">Год</th>
                            <th className="px-4 py-2 text-right">Показатель</th>
                          </tr>
                        </thead>
                        <tbody>
                          {forecastData.historical.map((point) => (
                            <tr key={point.year} className="border-b border-white/5">
                              <td className="px-4 py-2">{point.year}</td>
                              <td className="px-4 py-2 text-right">{point.value.toFixed(2)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-4">Прогноз</h3>
                    <div className="max-h-96 overflow-y-auto rounded-2xl border border-white/10">
                      <table className="min-w-full text-sm text-white/90 divide-y divide-white/10">
                        <thead className="bg-white/10 uppercase text-xs tracking-wider">
                          <tr>
                            <th className="px-4 py-2 text-left">Год</th>
                            <th className="px-4 py-2 text-right">Прогноз</th>
                          </tr>
                        </thead>
                        <tbody>
                          {forecastData.forecast
                            .filter(
                              (point) =>
                                point.year >
                                forecastData.historical[forecastData.historical.length - 1]?.year
                            )
                            .map((point) => (
                              <tr key={point.year} className="border-b border-white/5">
                                <td className="px-4 py-2">{point.year}</td>
                                <td className="px-4 py-2 text-right">
                                  {point.forecast.toFixed(2)}{' '}
                                  <span className="text-xs text-white/60">
                                    ({point.lower.toFixed(1)} - {point.upper.toFixed(1)})
                                  </span>
                                </td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-72 text-white/70">
                  Недостаточно данных для отображения таблицы
                </div>
              )}
            </div>
          )}
        </div>
        <div className="lg:col-span-1">
          <div className="bg-white/5 border border-white/15 rounded-3xl p-6 backdrop-blur-2xl shadow-2xl sticky top-8 space-y-6">
            <YearSlider
              min={info.year_range[0]}
              max={info.year_range[1]}
              value={selectedYear}
              onChange={setSelectedYear}
            />

            {hasCategories && (
              <div>
                <label className="block text-xs uppercase tracking-widest text-white/60 mb-2">
                  Тип объекта
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-4 py-3 rounded-2xl bg-white/10 text-white border border-white/10 focus:outline-none focus:ring-2 focus:ring-cyan-400"
                >
                  {sortedCategories.map((category) => (
                    <option key={category} value={category} className="text-slate-900">
                      {category}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div>
              <label className="block text-xs uppercase tracking-widest text-white/60 mb-2">
                Горизонт прогноза (лет)
              </label>
              <input
                type="number"
                min={1}
                max={30}
                value={forecastYears}
                onChange={(e) => setForecastYears(parseInt(e.target.value) || 12)}
                className="w-full px-4 py-3 rounded-2xl bg-white/10 text-white border border-white/10 focus:outline-none focus:ring-2 focus:ring-cyan-400"
              />
            </div>

            {info.has_entities && (
              <div>
                <label className="block text-xs uppercase tracking-widest text-white/60 mb-2">
                  Объект
                </label>
                <select
                  value={selectedEntity}
                  onChange={(e) => setSelectedEntity(e.target.value)}
                  className="w-full px-4 py-3 rounded-2xl bg-white/10 text-white border border-white/10 focus:outline-none focus:ring-2 focus:ring-cyan-400"
                >
                  <option value="">Все</option>
                  {availableEntities.map((entity) => (
                    <option key={entity} value={entity} className="text-slate-900">
                      {entity}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-white/60 mt-1">Найдено объектов: {totalEntities}</p>
              </div>
            )}

            {info.indicators && info.indicators.length > 0 && (
              <div>
                <label className="block text-xs uppercase tracking-widest text-white/60 mb-2">
                  Показатель
                </label>
                <select
                  value={selectedIndicator}
                  onChange={(e) => setSelectedIndicator(e.target.value)}
                  className="w-full px-4 py-3 rounded-2xl bg-white/10 text-white border border-white/10 focus:outline-none focus:ring-2 focus:ring-cyan-400"
                >
                  <option value="" className="text-slate-900">
                    Автоматически
                  </option>
                  {info.indicators.map((indicator) => (
                    <option key={indicator} value={indicator} className="text-slate-900">
                      {indicator.length > 50 ? `${indicator.substring(0, 50)}...` : indicator}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-white/60 mt-1">
                  Найдено показателей: {info.indicators.length}
                </p>
              </div>
            )}

            <div className="border-t border-white/10 pt-4 space-y-2 text-sm text-white/70">
              <div className="flex justify-between">
                <span>Период данных</span>
                <span className="text-white font-semibold">
                  {info.year_range[0]} - {info.year_range[1]}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Тип данных</span>
                <span className="text-white font-semibold">{info.entity_type}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
