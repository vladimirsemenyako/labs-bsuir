import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  ComposedChart,
  ReferenceLine,
} from 'recharts';
import { TimeSeriesPoint, ForecastPoint } from '@/lib/api';

interface TimeSeriesChartProps {
  historical: TimeSeriesPoint[];
  forecast: ForecastPoint[];
  title: string;
  selectedYear?: number;
}

export default function TimeSeriesChart({ historical, forecast, title, selectedYear }: TimeSeriesChartProps) {
  const lastHistoricalYear = historical[historical.length - 1]?.year || 2024;
  const futureData = forecast.filter((f) => f.year > lastHistoricalYear);

  const historicalData = historical.map((h) => ({
    year: h.year,
    Данные: h.value,
  }));

  const forecastData = futureData.map((f) => ({
    year: f.year,
    Прогноз: f.forecast,
    Нижняя_граница: f.lower,
    Верхняя_граница: f.upper,
  }));

  const combinedData = [...historicalData, ...forecastData];

  const renderDot = (color: string) => (props: any) => {
    const { cx, cy, payload } = props;
    if (!payload) return null;
    const isSelected = selectedYear && payload.year === selectedYear;
    const radius = isSelected ? 7 : 4;

    return (
      <circle
        cx={cx}
        cy={cy}
        r={radius}
        fill={color}
        stroke="#fff"
        strokeWidth={isSelected ? 2 : 1}
      />
    );
  };

  const CustomTick = (props: any) => {
    const { x, y, payload } = props;
    const isSelected = selectedYear && payload.value === selectedYear;
    return (
      <text
        x={x}
        y={y + 10}
        fill={isSelected ? '#fdf4ff' : '#cbd5f5'}
        fontSize={12}
        fontWeight={isSelected ? 700 : 500}
        textAnchor="middle"
      >
        {payload.value}
      </text>
    );
  };

  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold mb-4 text-white">{title}</h3>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={combinedData}>
          <defs>
            <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#a855f7" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#0f172a" stopOpacity="0" />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
          <XAxis dataKey="year" tick={<CustomTick />} axisLine={{ stroke: '#475569' }} tickLine={false} />
          <YAxis
            tick={{ fill: '#cbd5f5', fontSize: 12 }}
            axisLine={{ stroke: '#475569' }}
            tickLine={false}
            width={60}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(15,23,42,0.9)',
              border: '1px solid rgba(248,250,252,0.2)',
              borderRadius: '1rem',
              color: '#f8fafc',
            }}
            itemStyle={{ color: '#f8fafc' }}
            labelStyle={{ color: '#a5b4fc', fontWeight: 600 }}
          />
          <Legend wrapperStyle={{ color: '#e2e8f0' }} />

          {selectedYear && (
            <ReferenceLine
              x={selectedYear}
              stroke="#f472b6"
              strokeWidth={2}
              strokeDasharray="4 4"
              label={{
                value: `${selectedYear}`,
                position: 'top',
                fill: '#f472b6',
                style: { fontWeight: 700 },
              }}
            />
          )}
          <ReferenceLine
            x={lastHistoricalYear}
            stroke="#38bdf8"
            strokeDasharray="2 6"
            label={{
              value: 'Факт/прогноз',
              position: 'top',
              fill: '#38bdf8',
              style: { fontSize: 10, fontWeight: 600 },
            }}
          />

          <Area
            type="monotone"
            dataKey="Верхняя_граница"
            stroke="none"
            fill="url(#confidenceGradient)"
            fillOpacity={1}
            activeDot={false}
          />
          <Area
            type="monotone"
            dataKey="Нижняя_граница"
            stroke="none"
            fill="#0f172a"
            fillOpacity={0}
            activeDot={false}
          />

          <Line
            type="monotone"
            dataKey="Данные"
            stroke="#38bdf8"
            strokeWidth={3}
            dot={renderDot('#38bdf8')}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey="Прогноз"
            stroke="#c084fc"
            strokeWidth={3}
            strokeDasharray="6 4"
            dot={renderDot('#c084fc')}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

