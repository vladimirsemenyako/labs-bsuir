INSERT INTO firm (name, legal_address) VALUES
('ООО "ПаркСервис"', 'г. Минск, ул. Ленина, д. 10, офис 5'),
('ИП Петров А.В.', 'г. Минск, ул. Советская, д. 25, кв. 12'),
('ЗАО "Зеленый Город"', 'г. Минск, пр-т Независимости, д. 100, офис 301')
ON CONFLICT (name) DO NOTHING;

INSERT INTO parks (firm_id, name) VALUES
((SELECT firm_id FROM firm WHERE name = 'ООО "ПаркСервис"'), 'Центральный парк'),
((SELECT firm_id FROM firm WHERE name = 'ООО "ПаркСервис"'), 'Парк Победы'),
((SELECT firm_id FROM firm WHERE name = 'ИП Петров А.В.'), 'Сквер на Набережной'),
((SELECT firm_id FROM firm WHERE name = 'ЗАО "Зеленый Город"'), 'Парк Челюскинцев')
ON CONFLICT (name) DO NOTHING;

INSERT INTO zones (park_id, name) VALUES
((SELECT park_id FROM parks WHERE name = 'Центральный парк'), 'Зона А - центральная аллея'),
((SELECT park_id FROM parks WHERE name = 'Центральный парк'), 'Зона Б - детская площадка'),
((SELECT park_id FROM parks WHERE name = 'Центральный парк'), 'Зона В - спортивная зона'),
((SELECT park_id FROM parks WHERE name = 'Парк Победы'), 'Зона 1 - мемориальная'),
((SELECT park_id FROM parks WHERE name = 'Парк Победы'), 'Зона 2 - аллея славы'),
((SELECT park_id FROM parks WHERE name = 'Сквер на Набережной'), 'Прибрежная зона'),
((SELECT park_id FROM parks WHERE name = 'Парк Челюскинцев'), 'Входная группа'),
((SELECT park_id FROM parks WHERE name = 'Парк Челюскинцев'), 'Центральная часть')
ON CONFLICT DO NOTHING;

INSERT INTO plant_species (species_name) VALUES
('Клен остролистный'),
('Береза повислая'),
('Дуб черешчатый'),
('Липа мелколистная'),
('Ель обыкновенная'),
('Сосна обыкновенная'),
('Рябина обыкновенная'),
('Ясень обыкновенный')
ON CONFLICT DO NOTHING;

INSERT INTO plants (local_plant_number, zone_id, species_id, date_planted, age_at_planting_months) VALUES
('A-001', (SELECT zone_id FROM zones WHERE name = 'Зона А - центральная аллея'), (SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), '2020-05-15', 24),
('A-002', (SELECT zone_id FROM zones WHERE name = 'Зона А - центральная аллея'), (SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), '2020-05-15', 24),
('A-003', (SELECT zone_id FROM zones WHERE name = 'Зона А - центральная аллея'), (SELECT species_id FROM plant_species WHERE species_name = 'Липа мелколистная'), '2021-04-10', 36),
('B-001', (SELECT zone_id FROM zones WHERE name = 'Зона Б - детская площадка'), (SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), '2019-09-20', 12),
('B-002', (SELECT zone_id FROM zones WHERE name = 'Зона Б - детская площадка'), (SELECT species_id FROM plant_species WHERE species_name = 'Рябина обыкновенная'), '2022-03-25', 18),
('V-001', (SELECT zone_id FROM zones WHERE name = 'Зона В - спортивная зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Дуб черешчатый'), '2018-06-05', 48),
('V-002', (SELECT zone_id FROM zones WHERE name = 'Зона В - спортивная зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Ель обыкновенная'), '2020-10-12', 60),
('1-001', (SELECT zone_id FROM zones WHERE name = 'Зона 1 - мемориальная'), (SELECT species_id FROM plant_species WHERE species_name = 'Сосна обыкновенная'), '2015-05-09', 72),
('1-002', (SELECT zone_id FROM zones WHERE name = 'Зона 1 - мемориальная'), (SELECT species_id FROM plant_species WHERE species_name = 'Ель обыкновенная'), '2015-05-09', 84),
('2-001', (SELECT zone_id FROM zones WHERE name = 'Зона 2 - аллея славы'), (SELECT species_id FROM plant_species WHERE species_name = 'Ясень обыкновенный'), '2023-04-15', 12),
('2-002', (SELECT zone_id FROM zones WHERE name = 'Зона 2 - аллея славы'), (SELECT species_id FROM plant_species WHERE species_name = 'Липа мелколистная'), '2023-04-15', 18),
('PR-001', (SELECT zone_id FROM zones WHERE name = 'Прибрежная зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), '2021-07-20', 24),
('VG-001', (SELECT zone_id FROM zones WHERE name = 'Входная группа'), (SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), '2022-05-10', 36),
('VG-002', (SELECT zone_id FROM zones WHERE name = 'Входная группа'), (SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), '2022-05-10', 24),
('CENT-001', (SELECT zone_id FROM zones WHERE name = 'Центральная часть'), (SELECT species_id FROM plant_species WHERE species_name = 'Дуб черешчатый'), '2020-09-30', 48)
ON CONFLICT DO NOTHING;

INSERT INTO employees (full_name, phone, address, employee_type, education, university, category) VALUES
('Иванов Иван Иванович', '+375291234567', 'г. Минск, ул. Парковая, д. 15, кв. 8', 'служитель', NULL, NULL, NULL),
('Петров Петр Петрович', '+375292345678', 'г. Минск, ул. Садовая, д. 20, кв. 12', 'служитель', NULL, NULL, NULL),
('Сидоров Сидор Сидорович', '+375293456789', 'г. Минск, ул. Лесная, д. 5, кв. 3', 'служитель', NULL, NULL, NULL),
('Козлова Мария Сергеевна', '+375294567890', 'г. Минск, ул. Цветочная, д. 30, кв. 15', 'служитель', NULL, NULL, NULL),
('Смирнов Алексей Владимирович', '+375295678901', 'г. Минск, ул. Зеленая, д. 10, кв. 7', 'служитель', NULL, NULL, NULL),
('Новикова Елена Дмитриевна', '+375296789012', 'г. Минск, ул. Садовая, д. 25, кв. 20', 'декоратор', 'Высшее', 'БГУ, биологический факультет', 'высшая'),
('Волкова Анна Александровна', '+375297890123', 'г. Минск, ул. Парковая, д. 40, кв. 10', 'декоратор', 'Высшее', 'БГПУ, биолого-экологический факультет', 'первая'),
('Лебедев Дмитрий Николаевич', '+375298901234', 'г. Минск, ул. Лесная, д. 12, кв. 5', 'декоратор', 'Среднее специальное', 'Минский государственный колледж архитектуры и строительства', 'средняя'),
('Морозова Ольга Викторовна', '+375299012345', 'г. Минск, ул. Цветочная, д. 8, кв. 14', 'декоратор', 'Высшее', 'БГТУ, факультет ландшафтной архитектуры', 'высшая')
ON CONFLICT (phone) DO NOTHING;

INSERT INTO schedule (plant_id, employee_id, assignment_date) VALUES
((SELECT plant_id FROM plants WHERE local_plant_number = 'A-001'), (SELECT employee_id FROM employees WHERE full_name = 'Иванов Иван Иванович'), '2024-11-01'),
((SELECT plant_id FROM plants WHERE local_plant_number = 'A-002'), (SELECT employee_id FROM employees WHERE full_name = 'Иванов Иван Иванович'), '2024-11-01'),
((SELECT plant_id FROM plants WHERE local_plant_number = 'A-003'), (SELECT employee_id FROM employees WHERE full_name = 'Петров Петр Петрович'), '2024-11-01'),
((SELECT plant_id FROM plants WHERE local_plant_number = 'B-001'), (SELECT employee_id FROM employees WHERE full_name = 'Петров Петр Петрович'), '2024-11-02'),
((SELECT plant_id FROM plants WHERE local_plant_number = 'B-002'), (SELECT employee_id FROM employees WHERE full_name = 'Сидоров Сидор Сидорович'), '2024-11-02'),
((SELECT plant_id FROM plants WHERE local_plant_number = 'V-001'), (SELECT employee_id FROM employees WHERE full_name = 'Сидоров Сидор Сидорович'), '2024-11-03'),
((SELECT plant_id FROM plants WHERE local_plant_number = 'V-002'), (SELECT employee_id FROM employees WHERE full_name = 'Козлова Мария Сергеевна'), '2024-11-03'),
((SELECT plant_id FROM plants WHERE local_plant_number = '1-001'), (SELECT employee_id FROM employees WHERE full_name = 'Козлова Мария Сергеевна'), '2024-11-04'),
((SELECT plant_id FROM plants WHERE local_plant_number = '1-002'), (SELECT employee_id FROM employees WHERE full_name = 'Смирнов Алексей Владимирович'), '2024-11-04'),
((SELECT plant_id FROM plants WHERE local_plant_number = '2-001'), (SELECT employee_id FROM employees WHERE full_name = 'Смирнов Алексей Владимирович'), '2024-11-05'),
((SELECT plant_id FROM plants WHERE local_plant_number = 'A-001'), (SELECT employee_id FROM employees WHERE full_name = 'Иванов Иван Иванович'), '2024-11-06'),
((SELECT plant_id FROM plants WHERE local_plant_number = 'A-002'), (SELECT employee_id FROM employees WHERE full_name = 'Петров Петр Петрович'), '2024-11-06')
ON CONFLICT DO NOTHING;

INSERT INTO watering_regimes (species_id, min_age_months, max_age_months, periodicity, time_of_day, water_liters) VALUES
((SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), 0, 12, 'ежедневно', '08:00:00', 5.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), 13, 24, 'раз в неделю', '08:00:00', 10.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), 25, NULL, 'раз в 2 недели', '08:00:00', 15.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), 0, 12, 'ежедневно', '07:00:00', 8.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), 13, 36, 'раз в неделю', '07:00:00', 12.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), 37, NULL, 'раз в 2 недели', '07:00:00', 18.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Дуб черешчатый'), 0, 24, 'раз в неделю', '09:00:00', 15.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Дуб черешчатый'), 25, 60, 'раз в 2 недели', '09:00:00', 20.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Дуб черешчатый'), 61, NULL, 'раз в месяц', '09:00:00', 25.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Липа мелколистная'), 0, 18, 'раз в неделю', '08:30:00', 10.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Липа мелколистная'), 19, NULL, 'раз в 2 недели', '08:30:00', 15.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Ель обыкновенная'), 0, 36, 'раз в неделю', '07:30:00', 12.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Ель обыкновенная'), 37, NULL, 'раз в 2 недели', '07:30:00', 18.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Сосна обыкновенная'), 0, 48, 'раз в 2 недели', '08:00:00', 15.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Сосна обыкновенная'), 49, NULL, 'раз в месяц', '08:00:00', 20.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Рябина обыкновенная'), 0, 12, 'раз в неделю', '08:00:00', 8.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Рябина обыкновенная'), 13, NULL, 'раз в 2 недели', '08:00:00', 12.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Ясень обыкновенный'), 0, 24, 'раз в неделю', '08:00:00', 10.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Ясень обыкновенный'), 25, NULL, 'раз в 2 недели', '08:00:00', 15.0)
ON CONFLICT DO NOTHING;

