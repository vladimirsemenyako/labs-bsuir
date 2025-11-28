INSERT INTO firm (name, legal_address) VALUES
('ООО "ПаркСервис"', 'г. Минск, ул. Ленина, д. 10, офис 5'),
('ИП Петров А.В.', 'г. Минск, ул. Советская, д. 25, кв. 12'),
('ЗАО "Зеленый Город"', 'г. Минск, пр-т Независимости, д. 100, офис 301'),
('ООО "ЭкоПарк"', 'г. Минск, ул. Богдановича, д. 50, офис 12'),
('ИП Сидорова М.П.', 'г. Минск, ул. Янки Купалы, д. 15, кв. 45')
ON CONFLICT (name) DO NOTHING;

INSERT INTO parks (firm_id, name) VALUES
((SELECT firm_id FROM firm WHERE name = 'ООО "ПаркСервис"'), 'Центральный парк'),
((SELECT firm_id FROM firm WHERE name = 'ООО "ПаркСервис"'), 'Парк Победы'),
((SELECT firm_id FROM firm WHERE name = 'ИП Петров А.В.'), 'Сквер на Набережной'),
((SELECT firm_id FROM firm WHERE name = 'ЗАО "Зеленый Город"'), 'Парк Челюскинцев'),
((SELECT firm_id FROM firm WHERE name = 'ООО "ЭкоПарк"'), 'Лошицкий парк'),
((SELECT firm_id FROM firm WHERE name = 'ИП Сидорова М.П.'), 'Сквер Дружбы')
ON CONFLICT (name) DO NOTHING;

INSERT INTO zones (park_id, name) VALUES
((SELECT park_id FROM parks WHERE name = 'Центральный парк'), 'Зона А - центральная аллея'),
((SELECT park_id FROM parks WHERE name = 'Центральный парк'), 'Зона Б - детская площадка'),
((SELECT park_id FROM parks WHERE name = 'Центральный парк'), 'Зона В - спортивная зона'),
((SELECT park_id FROM parks WHERE name = 'Парк Победы'), 'Зона 1 - мемориальная'),
((SELECT park_id FROM parks WHERE name = 'Парк Победы'), 'Зона 2 - аллея славы'),
((SELECT park_id FROM parks WHERE name = 'Сквер на Набережной'), 'Прибрежная зона'),
((SELECT park_id FROM parks WHERE name = 'Парк Челюскинцев'), 'Входная группа'),
((SELECT park_id FROM parks WHERE name = 'Парк Челюскинцев'), 'Центральная часть'),
((SELECT park_id FROM parks WHERE name = 'Лошицкий парк'), 'Историческая зона'),
((SELECT park_id FROM parks WHERE name = 'Лошицкий парк'), 'Парковая зона'),
((SELECT park_id FROM parks WHERE name = 'Сквер Дружбы'), 'Центральная площадь')
ON CONFLICT DO NOTHING;

INSERT INTO plant_species (species_name) VALUES
('Клен остролистный'),
('Береза повислая'),
('Дуб черешчатый'),
('Липа мелколистная'),
('Ель обыкновенная'),
('Сосна обыкновенная'),
('Рябина обыкновенная'),
('Ясень обыкновенный'),
('Каштан конский'),
('Тополь белый'),
('Ива плакучая'),
('Туя западная')
ON CONFLICT DO NOTHING;

INSERT INTO plants (local_plant_number, zone_id, species_id, date_planted, age_at_planting_months) VALUES
-- Центральный парк - Зона А
('A-001', (SELECT zone_id FROM zones WHERE name = 'Зона А - центральная аллея'), (SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), '2020-05-15', 24),
('A-002', (SELECT zone_id FROM zones WHERE name = 'Зона А - центральная аллея'), (SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), '2020-05-15', 24),
('A-003', (SELECT zone_id FROM zones WHERE name = 'Зона А - центральная аллея'), (SELECT species_id FROM plant_species WHERE species_name = 'Липа мелколистная'), '2021-04-10', 36),
('A-004', (SELECT zone_id FROM zones WHERE name = 'Зона А - центральная аллея'), (SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), '2024-03-10', 6),
('A-005', (SELECT zone_id FROM zones WHERE name = 'Зона А - центральная аллея'), (SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), '2023-06-20', 18),
-- Центральный парк - Зона Б
('B-001', (SELECT zone_id FROM zones WHERE name = 'Зона Б - детская площадка'), (SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), '2019-09-20', 12),
('B-002', (SELECT zone_id FROM zones WHERE name = 'Зона Б - детская площадка'), (SELECT species_id FROM plant_species WHERE species_name = 'Рябина обыкновенная'), '2022-03-25', 18),
('B-003', (SELECT zone_id FROM zones WHERE name = 'Зона Б - детская площадка'), (SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), '2024-05-01', 6),
('B-004', (SELECT zone_id FROM zones WHERE name = 'Зона Б - детская площадка'), (SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), '2021-08-15', 30),
-- Центральный парк - Зона В
('V-001', (SELECT zone_id FROM zones WHERE name = 'Зона В - спортивная зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Дуб черешчатый'), '2018-06-05', 48),
('V-002', (SELECT zone_id FROM zones WHERE name = 'Зона В - спортивная зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Ель обыкновенная'), '2020-10-12', 60),
('V-003', (SELECT zone_id FROM zones WHERE name = 'Зона В - спортивная зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Дуб черешчатый'), '2022-04-20', 12),
-- Парк Победы - Зона 1
('1-001', (SELECT zone_id FROM zones WHERE name = 'Зона 1 - мемориальная'), (SELECT species_id FROM plant_species WHERE species_name = 'Сосна обыкновенная'), '2015-05-09', 72),
('1-002', (SELECT zone_id FROM zones WHERE name = 'Зона 1 - мемориальная'), (SELECT species_id FROM plant_species WHERE species_name = 'Ель обыкновенная'), '2015-05-09', 84),
('1-003', (SELECT zone_id FROM zones WHERE name = 'Зона 1 - мемориальная'), (SELECT species_id FROM plant_species WHERE species_name = 'Сосна обыкновенная'), '2020-06-15', 36),
-- Парк Победы - Зона 2
('2-001', (SELECT zone_id FROM zones WHERE name = 'Зона 2 - аллея славы'), (SELECT species_id FROM plant_species WHERE species_name = 'Ясень обыкновенный'), '2023-04-15', 12),
('2-002', (SELECT zone_id FROM zones WHERE name = 'Зона 2 - аллея славы'), (SELECT species_id FROM plant_species WHERE species_name = 'Липа мелколистная'), '2023-04-15', 18),
('2-003', (SELECT zone_id FROM zones WHERE name = 'Зона 2 - аллея славы'), (SELECT species_id FROM plant_species WHERE species_name = 'Ясень обыкновенный'), '2021-09-10', 30),
-- Сквер на Набережной
('PR-001', (SELECT zone_id FROM zones WHERE name = 'Прибрежная зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), '2021-07-20', 24),
('PR-002', (SELECT zone_id FROM zones WHERE name = 'Прибрежная зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Ива плакучая'), '2022-04-10', 12),
('PR-003', (SELECT zone_id FROM zones WHERE name = 'Прибрежная зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Ива плакучая'), '2020-05-20', 36),
-- Парк Челюскинцев - Входная группа
('VG-001', (SELECT zone_id FROM zones WHERE name = 'Входная группа'), (SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), '2022-05-10', 36),
('VG-002', (SELECT zone_id FROM zones WHERE name = 'Входная группа'), (SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), '2022-05-10', 24),
('VG-003', (SELECT zone_id FROM zones WHERE name = 'Входная группа'), (SELECT species_id FROM plant_species WHERE species_name = 'Туя западная'), '2023-03-15', 18),
-- Парк Челюскинцев - Центральная часть
('CENT-001', (SELECT zone_id FROM zones WHERE name = 'Центральная часть'), (SELECT species_id FROM plant_species WHERE species_name = 'Дуб черешчатый'), '2020-09-30', 48),
('CENT-002', (SELECT zone_id FROM zones WHERE name = 'Центральная часть'), (SELECT species_id FROM plant_species WHERE species_name = 'Каштан конский'), '2019-06-10', 60),
('CENT-003', (SELECT zone_id FROM zones WHERE name = 'Центральная часть'), (SELECT species_id FROM plant_species WHERE species_name = 'Каштан конский'), '2023-04-20', 12),
-- Лошицкий парк - Историческая зона
('LOSH-H-001', (SELECT zone_id FROM zones WHERE name = 'Историческая зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Дуб черешчатый'), '2010-05-15', 120),
('LOSH-H-002', (SELECT zone_id FROM zones WHERE name = 'Историческая зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Липа мелколистная'), '2015-06-20', 72),
('LOSH-H-003', (SELECT zone_id FROM zones WHERE name = 'Историческая зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Ясень обыкновенный'), '2020-04-10', 48),
-- Лошицкий парк - Парковая зона
('LOSH-P-001', (SELECT zone_id FROM zones WHERE name = 'Парковая зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), '2022-05-15', 18),
('LOSH-P-002', (SELECT zone_id FROM zones WHERE name = 'Парковая зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Рябина обыкновенная'), '2023-06-10', 6),
('LOSH-P-003', (SELECT zone_id FROM zones WHERE name = 'Парковая зона'), (SELECT species_id FROM plant_species WHERE species_name = 'Тополь белый'), '2021-04-20', 30),
-- Сквер Дружбы
('DRUZH-001', (SELECT zone_id FROM zones WHERE name = 'Центральная площадь'), (SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), '2024-04-15', 3),
('DRUZH-002', (SELECT zone_id FROM zones WHERE name = 'Центральная площадь'), (SELECT species_id FROM plant_species WHERE species_name = 'Туя западная'), '2023-09-10', 12),
('DRUZH-003', (SELECT zone_id FROM zones WHERE name = 'Центральная площадь'), (SELECT species_id FROM plant_species WHERE species_name = 'Туя западная'), '2022-05-20', 24)
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
-- Клен остролистный (3 режима: молодые, средние, взрослые)
((SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), 0, 12, 'ежедневно', '08:00:00', 5.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), 13, 24, 'раз в неделю', '08:00:00', 10.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Клен остролистный'), 25, NULL, 'раз в 2 недели', '08:00:00', 15.0),

-- Береза повислая (3 режима)
((SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), 0, 12, 'ежедневно', '07:00:00', 8.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), 13, 36, 'раз в неделю', '07:00:00', 12.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Береза повислая'), 37, NULL, 'раз в 2 недели', '07:00:00', 18.0),

-- Дуб черешчатый (3 режима)
((SELECT species_id FROM plant_species WHERE species_name = 'Дуб черешчатый'), 0, 24, 'раз в неделю', '09:00:00', 15.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Дуб черешчатый'), 25, 60, 'раз в 2 недели', '09:00:00', 20.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Дуб черешчатый'), 61, NULL, 'раз в месяц', '09:00:00', 25.0),

-- Липа мелколистная (2 режима)
((SELECT species_id FROM plant_species WHERE species_name = 'Липа мелколистная'), 0, 18, 'раз в неделю', '08:30:00', 10.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Липа мелколистная'), 19, NULL, 'раз в 2 недели', '08:30:00', 15.0),

-- Ель обыкновенная (2 режима)
((SELECT species_id FROM plant_species WHERE species_name = 'Ель обыкновенная'), 0, 36, 'раз в неделю', '07:30:00', 12.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Ель обыкновенная'), 37, NULL, 'раз в 2 недели', '07:30:00', 18.0),

-- Сосна обыкновенная (2 режима)
((SELECT species_id FROM plant_species WHERE species_name = 'Сосна обыкновенная'), 0, 48, 'раз в 2 недели', '08:00:00', 15.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Сосна обыкновенная'), 49, NULL, 'раз в месяц', '08:00:00', 20.0),

-- Рябина обыкновенная (2 режима)
((SELECT species_id FROM plant_species WHERE species_name = 'Рябина обыкновенная'), 0, 12, 'раз в неделю', '08:00:00', 8.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Рябина обыкновенная'), 13, NULL, 'раз в 2 недели', '08:00:00', 12.0),

-- Ясень обыкновенный (2 режима)
((SELECT species_id FROM plant_species WHERE species_name = 'Ясень обыкновенный'), 0, 24, 'раз в неделю', '08:00:00', 10.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Ясень обыкновенный'), 25, NULL, 'раз в 2 недели', '08:00:00', 15.0),

-- Каштан конский (3 режима)
((SELECT species_id FROM plant_species WHERE species_name = 'Каштан конский'), 0, 18, 'ежедневно', '08:30:00', 12.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Каштан конский'), 19, 48, 'раз в неделю', '08:30:00', 18.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Каштан конский'), 49, NULL, 'раз в 2 недели', '08:30:00', 25.0),

-- Тополь белый (2 режима)
((SELECT species_id FROM plant_species WHERE species_name = 'Тополь белый'), 0, 24, 'раз в неделю', '07:30:00', 14.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Тополь белый'), 25, NULL, 'раз в 2 недели', '07:30:00', 20.0),

-- Ива плакучая (3 режима - требует больше воды)
((SELECT species_id FROM plant_species WHERE species_name = 'Ива плакучая'), 0, 12, 'ежедневно', '07:00:00', 15.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Ива плакучая'), 13, 36, 'раз в неделю', '07:00:00', 20.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Ива плакучая'), 37, NULL, 'раз в неделю', '07:00:00', 25.0),

-- Туя западная (3 режима)
((SELECT species_id FROM plant_species WHERE species_name = 'Туя западная'), 0, 12, 'ежедневно', '08:00:00', 6.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Туя западная'), 13, 24, 'раз в неделю', '08:00:00', 10.0),
((SELECT species_id FROM plant_species WHERE species_name = 'Туя западная'), 25, NULL, 'раз в 2 недели', '08:00:00', 12.0)
ON CONFLICT DO NOTHING;

