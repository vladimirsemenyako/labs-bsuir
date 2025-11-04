#!/bin/bash

# Скрипт для быстрой инициализации базы данных
# Использование: ./setup.sh [имя_базы_данных]

DB_NAME=${1:-park_db}

echo "Инициализация базы данных: $DB_NAME"

# Проверка существования базы данных
if psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "База данных $DB_NAME уже существует."
    read -p "Пересоздать? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        dropdb "$DB_NAME"
        createdb "$DB_NAME"
        echo "База данных $DB_NAME пересоздана."
    fi
else
    createdb "$DB_NAME"
    echo "База данных $DB_NAME создана."
fi

# Применение схемы
echo "Применение схемы базы данных..."
psql -d "$DB_NAME" -f schema.sql
echo "✓ Схема применена"

# Применение функций
echo "Применение функций..."
psql -d "$DB_NAME" -f functions.sql
echo "✓ Функции применены"

# Применение триггеров
echo "Применение триггеров..."
psql -d "$DB_NAME" -f triggers.sql
echo "✓ Триггеры применены"

# Применение представлений
echo "Применение представлений..."
psql -d "$DB_NAME" -f views.sql
echo "✓ Представления применены"

echo ""
echo "База данных $DB_NAME успешно инициализирована!"
echo ""
echo "Для подключения используйте:"
echo "  psql -d $DB_NAME"
echo ""
echo "Не забудьте настроить .env файл для приложения!"

