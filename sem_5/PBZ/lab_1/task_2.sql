CREATE TABLE provider(
    provider_code VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    status INT,
    city VARCHAR(255)
);

CREATE TABLE detail(
    detail_code VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    color VARCHAR(255),
    size INT,
    city VARCHAR(255)
);

CREATE TABLE project(
    project_code VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    city VARCHAR(255)
);

CREATE TABLE number_of_details(
    provider_code VARCHAR(255) REFERENCES provider(provider_code),
    detail_code VARCHAR(255) REFERENCES detail(detail_code),
    project_code VARCHAR(255) REFERENCES project(project_code),
    number INT
);

INSERT INTO provider (provider_code, name, status, city)
VALUES ('P1', 'Petrov', 20, 'Moscow'),
       ('P2', 'Sinicin', 10, 'Tallin'),
       ('P3', 'Federov', 30, 'Tallin'),
       ('P4', 'Chaianov', 20, 'Minsk'),
       ('P5', 'Krykov', 30, 'Kiev');

INSERT INTO detail (detail_code, name, color, size, city)
VALUES ('D1', 'Bolt', 'Red', 12, 'Moscow'),
       ('D2', 'Gaika', 'Green', 17, 'Minsk'),
       ('D3', 'Disk', 'Black', 17, 'Vilnus'),
       ('D4', 'Disk', 'Black', 14, 'Moscow'),
       ('D5', 'Korpus', 'Red', 12, 'Minsk'),
       ('D6', 'Krishki', 'Red', 19, 'Moscow');

INSERT INTO project (project_code, name, city)
VALUES ('PR1', 'IPR1', 'Minsk'),
       ('PR2', 'IPR2', 'Tallin'),
       ('PR3', 'IPR3', 'Pskov'),
       ('PR4', 'IPR4', 'Pskov'),
       ('PR5', 'IPR4', 'Moscow'),
       ('PR6', 'IPR6', 'Saratov'),
       ('PR7', 'IPR7', 'Moscow');

INSERT INTO number_of_details (provider_code, detail_code, project_code, number)
VALUES ('P1', 'D1', 'PR1', 200),
       ('P1', 'D1', 'PR2', 700),
       ('P2', 'D3', 'PR1', 400),
       ('P2', 'D2', 'PR2', 200),
       ('P2', 'D3', 'PR3', 200),
       ('P2', 'D3', 'PR4', 500),
       ('P2', 'D3', 'PR5', 600),
       ('P2', 'D3', 'PR6', 400),
       ('P2', 'D3', 'PR7', 800),
       ('P2', 'D5', 'PR2', 100),
       ('P3', 'D3', 'PR1', 200),
       ('P3', 'D4', 'PR2', 500),
       ('P4', 'D6', 'PR3', 300),
       ('P4', 'D6', 'PR7', 300),
       ('P5', 'D2', 'PR2', 200),
       ('P5', 'D2', 'PR4', 100),
       ('P5', 'D5', 'PR5', 500),
       ('P5', 'D5', 'PR7', 100),
       ('P5', 'D6', 'PR2', 200),
       ('P5', 'D1', 'PR2', 100),
       ('P5', 'D3', 'PR4', 200),
       ('P5', 'D4', 'PR4', 800),
       ('P5', 'D5', 'PR4', 400),
       ('P5', 'D6', 'PR4', 500);

-- 11. Получить все пары названий городов, для которых поставщик из первого города обеспечивает проект во втором городе.
SELECT DISTINCT
    P.city AS provider_city,
    PR.city AS project_city
FROM number_of_details ND
JOIN provider P ON ND.provider_code = P.provider_code
JOIN project PR ON ND.project_code = PR.project_code;

-- 32. Получить номера проектов, обеспечиваемых по крайней мере всеми деталями поставщика П1.
SELECT DISTINCT project_code
FROM number_of_details
WHERE detail_code IN (
    SELECT detail_code
    FROM number_of_details
    WHERE provider_code = 'P1'
);
-- 4. Получить все отправки, где количество находится в диапазоне от 300 до 750 включительно.
SELECT * FROM number_of_details
WHERE number BETWEEN 300 AND 750;

-- 7. Получить все такие тройки "номера поставщиков-номера деталей-номера проектов", для которых
-- выводимые поставщик, деталь и проект не размещены в одном городе.
SELECT DISTINCT
    P.provider_code,
    D.detail_code,
    PR.project_code
FROM number_of_details ND
JOIN provider P ON ND.provider_code = P.provider_code
JOIN detail D ON ND.detail_code = D.detail_code
JOIN project PR ON ND.project_code = PR.project_code
WHERE NOT (P.city = D.city AND D.city = PR.city);

-- 16. Получить общее количество деталей Д1, поставляемых поставщиком П1.
SELECT COUNT(*) FROM number_of_details
WHERE provider_code = 'P1' AND detail_code = 'D1';

-- 31. Получить номера поставщиков, поставляющих одну и ту же деталь для всех проектов.
SELECT provider_code
FROM number_of_details
GROUP BY provider_code
HAVING COUNT(DISTINCT detail_code) = 1;
-- 26. Получить номера проектов, для которых среднее количество поставляемых деталей Д1 больше,
-- чем наибольшее количество любых деталей, поставляемых для проекта ПР1.
SELECT ND.project_code
FROM number_of_details ND
WHERE ND.detail_code = 'D1'
GROUP BY ND.project_code
HAVING AVG(ND.number) > (
    SELECT MAX(ND2.number)
    FROM number_of_details ND2
    WHERE ND2.project_code = 'PR1'
);

-- 22. Получить номера проектов, использующих по крайней мере одну деталь, имеющуюся у
-- поставщика П1.
SELECT DISTINCT project_code
FROM number_of_details
WHERE detail_code IN (
    SELECT detail_code
    FROM number_of_details
    WHERE provider_code = 'P1'
);

-- 8. Получить все такие тройки "номера поставщиков-номера деталей-номера проектов", для которых
-- никакие из двух выводимых поставщиков, деталей и проектов не размещены в одном городе.
SELECT ND.provider_code, ND.detail_code, ND.project_code
FROM number_of_details ND
JOIN provider P ON ND.provider_code = P.provider_code
JOIN detail D ON ND.detail_code = D.detail_code
JOIN project PR ON ND.project_code = PR.project_code
WHERE P.city <> D.city
  AND P.city <> PR.city
  AND D.city <> PR.city;

-- 28. Получить номера проектов, для которых не поставляются красные детали поставщиками из
-- Лондона.
SELECT P.project_code
FROM project P
WHERE NOT EXISTS (
    SELECT 1
    FROM number_of_details ND
    JOIN provider PR ON ND.provider_code = PR.provider_code
    JOIN detail D ON ND.detail_code = D.detail_code
    WHERE ND.project_code = P.project_code
      AND D.color = 'Red'
      AND PR.city = 'London'
);
