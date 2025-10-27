## Банк данных насаждений парков (вариант 22)

Требования: все операции — чистый SQL поверх SQLite (без ORM). Проект состоит из схемы БД (`db/schema.sql`), файла БД (`db/park.db`) и CLI на Python (`src/cli.py`).

### Установка

- Python 3.9+
- SQLite 3

База уже инициализирована. При необходимости пересоздать:

```bash
sqlite3 /Users/vivi/LabsBSUIR/sem_5/PBZ/lab_2/db/park.db ".read /Users/vivi/LabsBSUIR/sem_5/PBZ/lab_2/db/schema.sql"
```

### Веб-интерфейс (Streamlit)

Установка зависимостей (локально):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r /Users/vivi/LabsBSUIR/sem_5/PBZ/lab_2/requirements.txt
```

Запуск приложения:

```bash
streamlit run /Users/vivi/LabsBSUIR/sem_5/PBZ/lab_2/src/app_streamlit.py
```

Страницы: Компания, Виды, Парки/Зоны, Растения, Сотрудники, Режимы/Поливы, Отчёты. Все операции выполняются чистым SQL через `sqlite3`.

### Схема

- `company` — сведения о предприятии (одна запись id=1)
- `park`, `zone` — парки и их зоны
- `species` — виды растений
- `plant` — растения (уникальный `plant_number` в пределах `zone_id`)
- `watering_regime` — режимы полива по виду и возрасту
- `watering` — факт полива (не более одного в день для растения)
- `attendant` — служители парка
- `attendant_assignment` — закрепление служителя за растением на дату (один на дату)
- `decorator` — декораторы парка

Ограничения реализованы уникальными индексами и внешними ключами (`PRAGMA foreign_keys=ON`).

### Запуск CLI

```bash
python3 /Users/vivi/LabsBSUIR/sem_5/PBZ/lab_2/src/cli.py -h
```

Ключевые команды:

- Компания:
  - Просмотр: `company get`
  - Изменить: `company set "Название" "Юр. адрес"`
- Виды: `species add <latin> <common> | list | update <id> <latin> <common> | delete <id>`
- Парки: `park add <name> <address> | list | update <id> <name> <address> | delete <id>`
- Зоны: `zone add <park_id> <name> | list | update <id> <park_id> <name> | delete <id>`
- Растения: `plant add <zone_id> <species_id> <number> <YYYY-MM-DD> <age_years> | list | update <id> ... | delete <id>`
- Служители: `attendant add <name> <YYYY-MM-DD> <phone> <address> | list | update <id> ... | delete <id>`
- Закрепления: `assignment assign <plant_id> <YYYY-MM-DD> <attendant_id> | list | delete <id>`
- Декораторы: `decorator add <name> <YYYY-MM-DD> <phone> <address> <education> <institution> <category> | list | update <id> ... | delete <id>`
- Режимы полива: `regime add <species_id> <min_age> <max_age> <pattern> <HH:MM> <liters> | list | delete <id>`
- Полив: `watering add <plant_id> <YYYY-MM-DD> <HH:MM> <liters> | list | delete <id>`

Отчёты:

- Полная информация по насаждениям вида: `report_species <common_or_latin>`
- Сотрудники, работающие на дату: `report_staff_on_date <YYYY-MM-DD>`
- Растения вида и режимы полива на сегодня: `report_plants_regimes_today <common_or_latin>`

### Замечания по предметной области

- Возраст на сегодня вычисляется как годы от `planting_date` плюс `age_years_at_planting`.
- `day_pattern` в `watering_regime` текстовый (например, `daily`, `weekly:2` и т.п.). Логика интерпретации может быть расширена при необходимости.


