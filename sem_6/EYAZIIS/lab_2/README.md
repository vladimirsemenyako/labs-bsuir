# EYAZIIS Lab 2 (Docker: Frontend + Backend + MongoDB)

Эта версия ЛР переведена на клиент-серверную архитектуру:

- `frontend` - отдельный контейнер c веб-интерфейсом (Nginx + HTML/CSS/JS);
- `backend` - отдельный контейнер с API (`FastAPI`);
- `mongodb` - отдельный контейнер с БД.

## Почему здесь лучше MongoDB

Для текущей ЛР данные имеют документную структуру:

- один текстовый документ;
- вложенный массив токенов (`word`, `lemma`, `pos`);
- метаданные (`title`, `author`, `year`, `source`).

Такую модель удобнее хранить в `MongoDB`, чем раскладывать по нескольким реляционным таблицам.  
Для учебной задачи это дает более простой backend-код и быстрый старт.

## Запуск

Из папки `sem_6/EYAZIIS/lab_2`:

```bash
docker compose up --build
```

После запуска:

- frontend: [http://localhost:8080](http://localhost:8080)
- backend API: [http://localhost:8080/api/docs](http://localhost:8080/api/docs)
- mongo: `localhost:27017`

**Сохранение данных:** документы хранятся в Docker volume `lab_2_mongo_data`. Чтобы при перезапуске они не пропадали, не удаляйте volumes:

- Перезапуск без потери данных: `docker compose down` затем `docker compose up -d` (без флага `-v`).
- Если выполнить `docker compose down -v`, volume будет удалён и корпус очистится.

## Что реализовано

Backend endpoints:

- `GET /health`
- `GET /documents`
- `POST /documents`
- `DELETE /documents/{doc_id}`
- `GET /documents/{doc_id}` (текст + метаданные)
- `POST /documents/upload` (загрузка файлов TXT/RTF/PDF/DOC/DOCX)
- `GET /search?query=...&by=lemma|word&context_size=5` (можно с `doc_ids=...` для фильтра)
- `GET /frequencies?kind=word|lemma|pos&limit=...` (можно с `doc_ids=...`)
- `GET /morphology/{lemma}` (можно с `doc_ids=...`)
- `GET /corpus/export`
- `POST /corpus/import`

Frontend:

- добавление документов файлами (`TXT/RTF/PDF/DOC/DOCX`);
- сохранение/загрузка корпуса JSON;
- просмотр текста документа по двойному клику;
- фильтр по выбранным документам (для поиска/частот/морфологии);
- просмотр метаданных;
- поиск/конкорданс;
- частотные характеристики;
- морфология леммы.

## Примечание

Старые файлы (`app_gui.py`, `corpus.py`) оставлены в репозитории как предыдущая desktop-версия ЛР.
