// Запрос 1: Получить все автомобили с их владельцами
MATCH (o:Owner)-[:OWNS]->(v:Vehicle)
RETURN o.fullName AS ownerName, v.licensePlate AS licensePlate, v.brand AS brand, v.color AS color
ORDER BY o.fullName;

// Запрос 2: Подсчитать количество автомобилей, прошедших техосмотр за период времени, с разбивкой по дням
MATCH (v:Vehicle)-[:HAS_INSPECTION]->(i:Inspection)
WHERE i.date >= date('2024-01-15') AND i.date <= date('2024-01-19')
RETURN i.date AS inspectionDate, count(DISTINCT v) AS vehiclesCount
ORDER BY i.date;

// Запрос 3: Получить сотрудников, проводивших осмотр на указанную дату, с госномерами автомобилей
MATCH (e:Employee)-[:CONDUCTED]->(i:Inspection)<-[:HAS_INSPECTION]-(v:Vehicle)
WHERE i.date = date('2024-01-18')
RETURN e.fullName AS employeeName, e.rank AS rank, collect(DISTINCT v.licensePlate) AS licensePlates
ORDER BY e.fullName;

// Запрос 4: Получить историю прохождения техосмотра для конкретного автомобиля
MATCH (v:Vehicle {licensePlate: "1234 AB-7"})-[:HAS_INSPECTION]->(i:Inspection)
MATCH (e:Employee)-[:CONDUCTED]->(i)
RETURN i.date AS inspectionDate, i.result AS result, 
       i.conclusion AS conclusion, e.fullName AS inspectorName
ORDER BY i.date DESC;

// Запрос 5: Найти автомобили, не прошедшие техосмотр
MATCH (v:Vehicle)-[:HAS_INSPECTION]->(i:Inspection)
WHERE i.result = "Не пройден"
MATCH (o:Owner)-[:OWNS]->(v)
RETURN v.licensePlate AS licensePlate, v.brand AS brand,
       i.date AS inspectionDate, i.conclusion AS conclusion,
       o.fullName AS ownerName
ORDER BY i.date DESC;

// Запрос 6: Получить сотрудников и количество проведенных ими осмотров по дням
MATCH (e:Employee)-[:CONDUCTED]->(i:Inspection)
WHERE i.date >= date('2024-01-15') AND i.date <= date('2024-01-19')
RETURN e.fullName AS employeeName, e.rank AS rank,
       i.date AS inspectionDate, count(i) AS inspectionsCount
ORDER BY e.fullName, i.date;

// Запрос 7: Найти владельцев с несколькими автомобилями
MATCH (o:Owner)-[:OWNS]->(v:Vehicle)
WITH o, count(v) AS vehicleCount
WHERE vehicleCount > 1
RETURN o.fullName AS ownerName, o.driverLicense AS driverLicense,
       vehicleCount AS numberOfVehicles
ORDER BY vehicleCount DESC;

// Запрос 8: Получить все осмотры, проведенные конкретным сотрудником
MATCH (e:Employee {fullName: "Смирнов Алексей Владимирович"})-[:CONDUCTED]->(i:Inspection)
MATCH (v:Vehicle)-[:HAS_INSPECTION]->(i)
RETURN i.date AS inspectionDate, v.licensePlate AS licensePlate,
       i.result AS result, i.conclusion AS conclusion
ORDER BY i.date DESC;

// Запрос 9: Найти автомобили, прошедшие повторный осмотр (не прошли, затем прошли)
MATCH (v:Vehicle)-[:HAS_INSPECTION]->(i1:Inspection)
WHERE i1.result = "Не пройден"
MATCH (v)-[:HAS_INSPECTION]->(i2:Inspection)
WHERE i2.result = "Пройден" AND i2.date > i1.date
MATCH (o:Owner)-[:OWNS]->(v)
RETURN v.licensePlate AS licensePlate, v.brand AS brand,
       i1.date AS failedDate, i2.date AS passedDate,
       o.fullName AS ownerName
ORDER BY i2.date DESC;

// Запрос 10: Получить статистику: общее количество осмотров, пройденных и не пройденных за период
MATCH (i:Inspection)
WHERE i.date >= date('2024-01-15') AND i.date <= date('2024-01-19')
WITH i.date AS inspectionDate,
     count(i) AS totalInspections,
     sum(CASE WHEN i.result = "Пройден" THEN 1 ELSE 0 END) AS passedCount,
     sum(CASE WHEN i.result = "Не пройден" THEN 1 ELSE 0 END) AS failedCount
RETURN inspectionDate, totalInspections, passedCount, failedCount,
       round(toFloat(passedCount) / totalInspections * 100, 2) AS passRate
ORDER BY inspectionDate;

// Запрос 11: Найти кратчайший путь между двумя владельцами
MATCH path = shortestPath(
  (o1:Owner {fullName: "Иванов Иван Иванович"})-[*]-(o2:Owner {fullName: "Петрова Мария Сергеевна"})
)
RETURN path, length(path) AS pathLength;

// Запрос 12: Найти кратчайший путь между владельцем и сотрудником
MATCH path = shortestPath(
  (o:Owner {fullName: "Иванов Иван Иванович"})-[*]-(e:Employee {fullName: "Смирнов Алексей Владимирович"})
)
RETURN path, length(path) AS pathLength;

// Запрос 13: Найти все кратчайшие пути между двумя узлами с деталями
MATCH (start:Owner {fullName: "Иванов Иван Иванович"}), (end:Owner {fullName: "Петрова Мария Сергеевна"})
MATCH path = shortestPath((start)-[*..10]-(end))
RETURN [node in nodes(path) | 
  CASE 
    WHEN node:Owner THEN 'Владелец: ' + node.fullName
    WHEN node:Vehicle THEN 'Автомобиль: ' + node.licensePlate
    WHEN node:Employee THEN 'Сотрудник: ' + node.fullName
    WHEN node:Inspection THEN 'Осмотр: ' + node.inspectionId
    ELSE labels(node)[0]
  END
] AS pathNodes, length(path) AS pathLength;

// Запрос 14: Найти все узлы на расстоянии 1 (радиус 1) от владельца
MATCH (start:Owner {fullName: "Иванов Иван Иванович"})-[*1]-(end)
RETURN start, end, labels(end) AS endType, 
       CASE 
         WHEN end:Vehicle THEN end.licensePlate
         WHEN end:Owner THEN end.fullName
         WHEN end:Employee THEN end.fullName
         WHEN end:Inspection THEN end.inspectionId
         ELSE toString(id(end))
       END AS endInfo;

// Запрос 15: Найти все узлы на расстоянии 1-2 (радиус 2) от владельца
MATCH (start:Owner {fullName: "Иванов Иван Иванович"})-[*1..2]-(end)
RETURN start, end, labels(end) AS endType,
       CASE 
         WHEN end:Vehicle THEN end.licensePlate
         WHEN end:Owner THEN end.fullName
         WHEN end:Employee THEN end.fullName
         WHEN end:Inspection THEN end.inspectionId
         ELSE toString(id(end))
       END AS endInfo;

