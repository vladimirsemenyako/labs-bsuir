'use client';

import { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip, GeoJSON } from 'react-leaflet';
import { WaterFeature } from '@/lib/api';
import L from 'leaflet';

if (typeof window !== 'undefined') {
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  });
}

interface MapComponentProps {
  features: WaterFeature[];
  entityData: Record<string, number>;
  title: string;
  category: string;
  geojson: any;
}

export default function MapComponent({ features, entityData, title, category, geojson }: MapComponentProps) {
  useEffect(() => {
    require('leaflet/dist/leaflet.css');
  }, []);

  const values = Object.values(entityData || {}).filter(
    (value) => typeof value === 'number' && !Number.isNaN(value)
  );
  const minVal = values.length ? Math.min(...values) : 0;
  const maxVal = values.length ? Math.max(...values) : 1;
  const range = maxVal - minVal || 1;

  const getFeatureColor = (name: string) => {
    const item = features.find((f) => f.name === name);
    return item?.color || '#808080';
  };

  const getFeatureValue = (name: string) => {
    return entityData?.[name];
  };

  const geoJSONStyle = (feature: any) => {
    const name = feature.properties.name;
    const value = getFeatureValue(name);
    const color = getFeatureColor(name);
    
    if (value === undefined) {
      return {
        color: '#cccccc',
        weight: 1.5,
        opacity: 0.3,
        fillOpacity: category === 'Озера' ? 0.2 : 0,
      };
    }

    const normalized = (value - minVal) / range;
    const weight = category === 'Озера' ? 1 : 2 + normalized * 4;
    const fillOpacity = category === 'Озера' ? 0.3 + normalized * 0.5 : 0;

    return {
      color,
      weight,
      opacity: 0.85,
      fillColor: color,
      fillOpacity,
    };
  };

  const onEachFeature = (feature: any, layer: any) => {
    const name = feature.properties.name;
    const value = getFeatureValue(name);
    
    if (value !== undefined) {
      layer.bindPopup(`
        <div style="font-size: 14px;">
          <strong>${name}</strong><br/>
          ${title}: ${value.toFixed(3)}
        </div>
      `);
      
      layer.bindTooltip(`${name}: ${value.toFixed(2)}`, {
        permanent: false,
        direction: 'top'
      });
    }
  };

  return (
    <MapContainer
      center={[53.5, 28.0]}
      zoom={7}
      scrollWheelZoom={true}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {geojson && (
        <GeoJSON
          data={geojson}
          style={geoJSONStyle}
          onEachFeature={onEachFeature}
        />
      )}

      {features.map((feature) => {
        const value = entityData?.[feature.name];
        const hasValue = typeof value === 'number' && !Number.isNaN(value);
        const markerColor = hasValue ? feature.color : '#94a3b8';

        return (
          <CircleMarker
            key={feature.name}
            center={[feature.lat, feature.lon]}
            radius={category === 'Озера' ? 7 : 8}
            pathOptions={{
              color: markerColor,
              fillColor: markerColor,
              fillOpacity: hasValue ? 0.85 : 0.35,
              weight: 2,
            }}
          >
            <Popup>
              <div className="text-sm">
                <strong>{feature.name}</strong>
                <br />
                {hasValue ? (
                  <>
                    {title}: {value?.toFixed(3)}
                  </>
                ) : (
                  'Данные отсутствуют'
                )}
              </div>
            </Popup>
            {!hasValue && (
              <Tooltip direction="top" opacity={0.7}>
                <span>{feature.name}: нет данных</span>
              </Tooltip>
            )}
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}

