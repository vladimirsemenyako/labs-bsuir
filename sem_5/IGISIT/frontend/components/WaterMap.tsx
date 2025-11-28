'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { WaterFeature } from '@/lib/api';

const MapComponent = dynamic(() => import('./MapComponent'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[500px] rounded-3xl bg-white/10 border border-white/10 animate-pulse" />
  ),
});

interface WaterMapProps {
  features: WaterFeature[];
  entityData: Record<string, number>;
  title: string;
  category: string;
  geojson: any;
}

export default function WaterMap({ features, entityData, title, category, geojson }: WaterMapProps) {
  return (
    <div className="w-full h-[500px]">
      <MapComponent
        features={features}
        entityData={entityData}
        title={title}
        category={category}
        geojson={geojson}
      />
    </div>
  );
}

