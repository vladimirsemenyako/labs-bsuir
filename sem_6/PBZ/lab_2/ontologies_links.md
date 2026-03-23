# Готовые онтологии для задания 3 (Транспорт)

Использовать **минимум 2** онтологии. Импорт в Protege: **File → Import → Load from URL** или скачать .owl и **Import from file**.

---

## Рекомендуемые источники

### 1. Transportation System Ontology (University of Toronto)
- Страница: https://enterpriseintegrationlab.github.io/icity/TransportationSystem/doc/index-en.html  
- Прямая загрузка (проверить актуальную версию):  
  http://ontology.eil.utoronto.ca/icity/TransportationSystem/1.2/TransportationSystem.owl  

### 2. Vehicle Ontology (University of Toronto)
- Страница: https://enterpriseintegrationlab.github.io/icity/Vehicle/doc/index-en.html  
- Загрузка: http://ontology.eil.utoronto.ca/icity/Vehicle/1.2/Vehicle.owl  

### 3. Automotive Urban Traffic Ontology (AUTO)
- GitHub: https://github.com/lu-w/auto  
- OWL-файл: в репозитории искать `*.owl` (например automotive_urban_traffic_ontology.owl)  

### 4. Библиотеки из задания
- Protege Ontology Library: http://protegewiki.stanford.edu/wiki/Protege_Ontology_Library  
- Manchester OWL repositories: http://owl.cs.manchester.ac.uk/tools/repositories/  
- Oxford ontologies: http://www.cs.ox.ac.uk/isg/ontologies/lib/  

---

После импорта в своей онтологии можно, например:
- связать свой класс `TransportVehicle` с классом `Vehicle` из импортированной онтологии (эквивалентность или подкласс);
- написать запросы, в которых участвуют классы и из своей онтологии, и из импортированной.
