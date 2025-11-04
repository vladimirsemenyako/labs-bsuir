# Банк данных насаждений парков

## Запуск через Docker

```bash
docker-compose up --build
```

Приложение доступно по адресу: http://localhost:8501

## Запуск без Docker

### База данных

```bash
psql -d park_db -f db/schema.sql
psql -d park_db -f db/functions.sql
psql -d park_db -f db/triggers.sql
psql -d park_db -f db/views.sql
psql -d park_db -f db/test_data.sql
```

### Приложение

```bash
pip install -r requirements.txt
streamlit run src/app_streamlit.py
```

## Структура проекта

- `db/schema.sql` - схема базы данных
- `db/functions.sql` - функции PostgreSQL
- `db/triggers.sql` - триггеры
- `db/views.sql` - представления
- `db/test_data.sql` - тестовые данные
- `src/app_streamlit.py` - веб-интерфейс
