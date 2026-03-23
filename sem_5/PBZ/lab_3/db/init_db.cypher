MATCH (n) DETACH DELETE n;

CREATE (o1:Owner {
  fullName: "Иванов Иван Иванович",
  driverLicense: "AB1234567",
  address: "г. Минск, ул. Ленина, д. 10",
  birthYear: 1985,
  gender: "М"
})
CREATE (o2:Owner {
  fullName: "Петрова Мария Сергеевна",
  driverLicense: "CD2345678",
  address: "г. Минск, пр. Независимости, д. 25",
  birthYear: 1990,
  gender: "Ж"
})
CREATE (o3:Owner {
  fullName: "Сидоров Петр Александрович",
  driverLicense: "EF3456789",
  address: "г. Минск, ул. Победителей, д. 5",
  birthYear: 1978,
  gender: "М"
})
CREATE (o4:Owner {
  fullName: "Козлова Анна Викторовна",
  driverLicense: "GH4567890",
  address: "г. Минск, ул. Козлова, д. 15",
  birthYear: 1992,
  gender: "Ж"
})
CREATE (o5:Owner {
  fullName: "Новиков Дмитрий Олегович",
  driverLicense: "IJ5678901",
  address: "г. Минск, ул. Некрасова, д. 30",
  birthYear: 1988,
  gender: "М"
});

CREATE (v1:Vehicle {
  licensePlate: "1234 AB-7",
  engineNumber: "ENG001234",
  color: "Черный",
  brand: "Toyota Camry",
  techPassport: "TP123456"
})
CREATE (v2:Vehicle {
  licensePlate: "5678 CD-7",
  engineNumber: "ENG005678",
  color: "Белый",
  brand: "BMW X5",
  techPassport: "TP234567"
})
CREATE (v3:Vehicle {
  licensePlate: "9012 EF-7",
  engineNumber: "ENG009012",
  color: "Серый",
  brand: "Mercedes-Benz C-Class",
  techPassport: "TP345678"
})
CREATE (v4:Vehicle {
  licensePlate: "3456 GH-7",
  engineNumber: "ENG003456",
  color: "Красный",
  brand: "Audi A4",
  techPassport: "TP456789"
})
CREATE (v5:Vehicle {
  licensePlate: "7890 IJ-7",
  engineNumber: "ENG007890",
  color: "Синий",
  brand: "Volkswagen Passat",
  techPassport: "TP567890"
})
CREATE (v6:Vehicle {
  licensePlate: "2468 KL-7",
  engineNumber: "ENG002468",
  color: "Зеленый",
  brand: "Ford Focus",
  techPassport: "TP678901"
});

CREATE (e1:Employee {
  fullName: "Смирнов Алексей Владимирович",
  position: "Инспектор",
  rank: "Старший лейтенант",
  employeeId: "EMP001"
})
CREATE (e2:Employee {
  fullName: "Волков Сергей Николаевич",
  position: "Инспектор",
  rank: "Лейтенант",
  employeeId: "EMP002"
})
CREATE (e3:Employee {
  fullName: "Лебедева Ольга Петровна",
  position: "Старший инспектор",
  rank: "Капитан",
  employeeId: "EMP003"
})
CREATE (e4:Employee {
  fullName: "Соколов Андрей Игоревич",
  position: "Инспектор",
  rank: "Лейтенант",
  employeeId: "EMP004"
});

// Owners -> Vehicles 
MATCH (o1:Owner {driverLicense: "AB1234567"}), (v1:Vehicle {licensePlate: "1234 AB-7"})
CREATE (o1)-[:OWNS]->(v1);

MATCH (o2:Owner {driverLicense: "CD2345678"}), (v2:Vehicle {licensePlate: "5678 CD-7"})
CREATE (o2)-[:OWNS]->(v2);

MATCH (o3:Owner {driverLicense: "EF3456789"}), (v3:Vehicle {licensePlate: "9012 EF-7"})
CREATE (o3)-[:OWNS]->(v3);

MATCH (o4:Owner {driverLicense: "GH4567890"}), (v4:Vehicle {licensePlate: "3456 GH-7"})
CREATE (o4)-[:OWNS]->(v4);

MATCH (o5:Owner {driverLicense: "IJ5678901"}), (v5:Vehicle {licensePlate: "7890 IJ-7"})
CREATE (o5)-[:OWNS]->(v5);

MATCH (o1:Owner {driverLicense: "AB1234567"}), (v6:Vehicle {licensePlate: "2468 KL-7"})
CREATE (o1)-[:OWNS]->(v6);

CREATE (i1:Inspection {
  inspectionId: "INS001",
  date: date("2024-01-15"),
  result: "Пройден",
  conclusion: "Автомобиль соответствует требованиям безопасности"
})
CREATE (i2:Inspection {
  inspectionId: "INS002",
  date: date("2024-01-15"),
  result: "Пройден",
  conclusion: "Все системы в норме"
})
CREATE (i3:Inspection {
  inspectionId: "INS003",
  date: date("2024-01-16"),
  result: "Не пройден",
  conclusion: "Обнаружены неисправности тормозной системы"
})
CREATE (i4:Inspection {
  inspectionId: "INS004",
  date: date("2024-01-16"),
  result: "Пройден",
  conclusion: "Техническое состояние удовлетворительное"
})
CREATE (i5:Inspection {
  inspectionId: "INS005",
  date: date("2024-01-17"),
  result: "Пройден",
  conclusion: "Автомобиль в хорошем состоянии"
})
CREATE (i6:Inspection {
  inspectionId: "INS006",
  date: date("2024-01-17"),
  result: "Пройден",
  conclusion: "Все проверки пройдены успешно"
})
CREATE (i7:Inspection {
  inspectionId: "INS007",
  date: date("2024-01-18"),
  result: "Пройден",
  conclusion: "Соответствует нормам"
})
CREATE (i8:Inspection {
  inspectionId: "INS008",
  date: date("2024-01-18"),
  result: "Не пройден",
  conclusion: "Требуется замена шин"
})
CREATE (i9:Inspection {
  inspectionId: "INS009",
  date: date("2024-01-19"),
  result: "Пройден",
  conclusion: "Техосмотр пройден"
})
CREATE (i10:Inspection {
  inspectionId: "INS010",
  date: date("2024-01-19"),
  result: "Пройден",
  conclusion: "Все системы работают корректно"
})
CREATE (i11:Inspection {
  inspectionId: "INS011",
  date: date("2024-02-10"),
  result: "Пройден",
  conclusion: "Повторный осмотр после ремонта"
})
CREATE (i12:Inspection {
  inspectionId: "INS012",
  date: date("2024-02-15"),
  result: "Пройден",
  conclusion: "Плановый техосмотр"
});

// Employees -> Inspections
MATCH (e1:Employee {employeeId: "EMP001"}), (i1:Inspection {inspectionId: "INS001"})
CREATE (e1)-[:CONDUCTED {conductedAt: datetime("2024-01-15T10:00:00")}]->(i1);

MATCH (e1:Employee {employeeId: "EMP001"}), (i2:Inspection {inspectionId: "INS002"})
CREATE (e1)-[:CONDUCTED {conductedAt: datetime("2024-01-15T11:30:00")}]->(i2);

MATCH (e2:Employee {employeeId: "EMP002"}), (i3:Inspection {inspectionId: "INS003"})
CREATE (e2)-[:CONDUCTED {conductedAt: datetime("2024-01-16T09:15:00")}]->(i3);

MATCH (e2:Employee {employeeId: "EMP002"}), (i4:Inspection {inspectionId: "INS004"})
CREATE (e2)-[:CONDUCTED {conductedAt: datetime("2024-01-16T14:20:00")}]->(i4);

MATCH (e3:Employee {employeeId: "EMP003"}), (i5:Inspection {inspectionId: "INS005"})
CREATE (e3)-[:CONDUCTED {conductedAt: datetime("2024-01-17T10:45:00")}]->(i5);

MATCH (e3:Employee {employeeId: "EMP003"}), (i6:Inspection {inspectionId: "INS006"})
CREATE (e3)-[:CONDUCTED {conductedAt: datetime("2024-01-17T15:30:00")}]->(i6);

MATCH (e4:Employee {employeeId: "EMP004"}), (i7:Inspection {inspectionId: "INS007"})
CREATE (e4)-[:CONDUCTED {conductedAt: datetime("2024-01-18T09:00:00")}]->(i7);

MATCH (e4:Employee {employeeId: "EMP004"}), (i8:Inspection {inspectionId: "INS008"})
CREATE (e4)-[:CONDUCTED {conductedAt: datetime("2024-01-18T13:15:00")}]->(i8);

MATCH (e1:Employee {employeeId: "EMP001"}), (i9:Inspection {inspectionId: "INS009"})
CREATE (e1)-[:CONDUCTED {conductedAt: datetime("2024-01-19T10:30:00")}]->(i9);

MATCH (e2:Employee {employeeId: "EMP002"}), (i10:Inspection {inspectionId: "INS010"})
CREATE (e2)-[:CONDUCTED {conductedAt: datetime("2024-01-19T14:00:00")}]->(i10);

MATCH (e2:Employee {employeeId: "EMP002"}), (i11:Inspection {inspectionId: "INS011"})
CREATE (e2)-[:CONDUCTED {conductedAt: datetime("2024-02-10T11:00:00")}]->(i11);

MATCH (e3:Employee {employeeId: "EMP003"}), (i12:Inspection {inspectionId: "INS012"})
CREATE (e3)-[:CONDUCTED {conductedAt: datetime("2024-02-15T10:00:00")}]->(i12);

// Vehicles -> Inspections
MATCH (v1:Vehicle {licensePlate: "1234 AB-7"}), (i1:Inspection {inspectionId: "INS001"})
CREATE (v1)-[:HAS_INSPECTION]->(i1);

MATCH (v2:Vehicle {licensePlate: "5678 CD-7"}), (i2:Inspection {inspectionId: "INS002"})
CREATE (v2)-[:HAS_INSPECTION]->(i2);

MATCH (v3:Vehicle {licensePlate: "9012 EF-7"}), (i3:Inspection {inspectionId: "INS003"})
CREATE (v3)-[:HAS_INSPECTION]->(i3);

MATCH (v4:Vehicle {licensePlate: "3456 GH-7"}), (i4:Inspection {inspectionId: "INS004"})
CREATE (v4)-[:HAS_INSPECTION]->(i4);

MATCH (v5:Vehicle {licensePlate: "7890 IJ-7"}), (i5:Inspection {inspectionId: "INS005"})
CREATE (v5)-[:HAS_INSPECTION]->(i5);

MATCH (v6:Vehicle {licensePlate: "2468 KL-7"}), (i6:Inspection {inspectionId: "INS006"})
CREATE (v6)-[:HAS_INSPECTION]->(i6);

MATCH (v1:Vehicle {licensePlate: "1234 AB-7"}), (i7:Inspection {inspectionId: "INS007"})
CREATE (v1)-[:HAS_INSPECTION]->(i7);

MATCH (v2:Vehicle {licensePlate: "5678 CD-7"}), (i8:Inspection {inspectionId: "INS008"})
CREATE (v2)-[:HAS_INSPECTION]->(i8);

MATCH (v3:Vehicle {licensePlate: "9012 EF-7"}), (i9:Inspection {inspectionId: "INS009"})
CREATE (v3)-[:HAS_INSPECTION]->(i9);

MATCH (v4:Vehicle {licensePlate: "3456 GH-7"}), (i10:Inspection {inspectionId: "INS010"})
CREATE (v4)-[:HAS_INSPECTION]->(i10);

MATCH (v3:Vehicle {licensePlate: "9012 EF-7"}), (i11:Inspection {inspectionId: "INS011"})
CREATE (v3)-[:HAS_INSPECTION]->(i11);

MATCH (v1:Vehicle {licensePlate: "1234 AB-7"}), (i12:Inspection {inspectionId: "INS012"})
CREATE (v1)-[:HAS_INSPECTION]->(i12);