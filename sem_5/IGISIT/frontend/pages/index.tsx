import { useState } from 'react';
import Head from 'next/head';
import useSWR from 'swr';
import { api } from '@/lib/api';
import DatasetTab from '@/components/DatasetTab';

export default function Home() {
  const { data: datasets, error } = useSWR('/api/datasets', () => api.getDatasets());
  const [activeTab, setActiveTab] = useState(0);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-red-200">
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-bold">Ошибка подключения к API</h2>
          <p className="text-slate-300">
            Убедитесь, что backend сервер запущен на <span className="text-cyan-300">http://localhost:8000</span>
          </p>
        </div>
      </div>
    );
  }

  if (!datasets) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-cyan-400 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Водные ресурсы Беларуси - Аналитика</title>
        <meta name="description" content="Интерактивная витрина данных и прогнозов по водным ресурсам Беларуси" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-[#020617] via-[#0b1120] to-[#020617] text-slate-100">
        <div className="max-w-7xl mx-auto px-4 py-10 space-y-10">
          <header className="bg-white/10 border border-white/20 rounded-3xl p-8 shadow-2xl backdrop-blur-xl">
            <div className="flex flex-col gap-4">
              <div>
                <p className="uppercase text-xs tracking-[0.4em] text-cyan-200/80">Беларусь · Водные ресурсы</p>
                <h1 className="text-4xl lg:text-5xl font-bold mt-3 text-white">
                  Живая аналитика и прогноз водных систем
                </h1>
              </div>
              <p className="text-slate-200 text-lg max-w-4xl">
                Интерактивный атлас показывает состояние рек, озёр и подземных вод, позволяет фильтровать показатели,
                подсвечивать регионы на карте и строить полиномиальные прогнозы будущих трендов.
              </p>
            </div>
          </header>

          <section className="bg-white/5 border border-white/15 rounded-3xl shadow-2xl backdrop-blur-2xl">
            <nav className="flex flex-wrap gap-3 p-4">
              {datasets.map((dataset, index) => {
                const isActive = activeTab === index;
                return (
                  <button
                    key={dataset.filename}
                    onClick={() => setActiveTab(index)}
                    className={`px-5 py-3 rounded-2xl text-sm font-semibold transition-all duration-300
                      ${isActive
                        ? 'bg-cyan-400/80 text-slate-900 shadow-lg shadow-cyan-500/50'
                        : 'bg-white/10 text-slate-200 hover:bg-white/20'
                      }`}
                  >
                    {dataset.title}
                  </button>
                );
              })}
            </nav>
          </section>

          <section className="space-y-6">
            {datasets[activeTab] && <DatasetTab dataset={datasets[activeTab]} />}
          </section>

          <footer className="mt-16 bg-white/5 border border-white/10 rounded-3xl p-6 text-center backdrop-blur-xl shadow-2xl">
            <p className="text-sm text-slate-200 mb-1">
              <span className="font-semibold text-cyan-200">Источник данных:</span> Министерство природных ресурсов и охраны
              окружающей среды Республики Беларусь
            </p>
            <p className="text-xs text-slate-400">
              Прогнозирование выполняется с использованием моделей Prophet и полиномиальной регрессии.
            </p>
          </footer>
        </div>
      </main>
    </>
  );
}

