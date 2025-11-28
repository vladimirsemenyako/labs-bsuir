#!/bin/bash

echo "🚀 Запуск системы анализа водных ресурсов Беларуси"
echo ""

echo "📦 Backend (FastAPI) на http://localhost:8000"
cd backend
python3 -m uvicorn main:app --reload &
BACKEND_PID=$!

sleep 2

echo ""
echo "🌐 Frontend (Next.js) на http://localhost:3000"
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Приложение запущено!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Для остановки нажмите Ctrl+C"

wait

