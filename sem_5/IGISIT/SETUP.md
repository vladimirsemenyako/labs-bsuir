# Установка и запуск

## Backend (FastAPI)

```bash
cd backend
pip3 install -r requirements.txt
python3 -m uvicorn main:app --reload
```

Backend будет доступен на http://localhost:8000

## Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Frontend будет доступен на http://localhost:3000

## Быстрый запуск

```bash
chmod +x start.sh
./start.sh
```

## Структура проекта

```
├── backend/          # FastAPI сервер
│   ├── main.py      # Основной API
│   └── requirements.txt
├── frontend/        # Next.js приложение
│   ├── components/  # React компоненты
│   ├── pages/       # Страницы
│   ├── lib/         # API клиент
│   └── styles/      # Стили
├── src/             # Общие Python модули
│   ├── data_loader.py
│   ├── forecasting.py
│   ├── visualization.py
│   └── config.py
└── data/            # CSV файлы с данными
```

## Технологии

**Backend:**
- FastAPI - современный web framework
- Prophet - прогнозирование временных рядов
- Pandas - обработка данных

**Frontend:**
- Next.js 14 - React framework
- TypeScript - типизация
- Tailwind CSS - стили
- Leaflet - интерактивные карты
- Recharts - графики
- SWR - кеширование данных

## API Endpoints

- `GET /api/datasets` - список датасетов
- `GET /api/dataset/{filename}` - информация о датасете
- `POST /api/forecast` - прогнозирование
- `GET /api/entity-data/{filename}/{year}` - данные по объектам
- `GET /api/rivers` - список рек
- `GET /api/timeseries/{filename}` - временной ряд

