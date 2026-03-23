# Merge водной, наземной и авиа-онтологий

## Что сделано для "идеального" merge

Создана отдельная мостовая онтология `transport_merged_bridge.owx`, которая:
- импортирует `ontology_land_air.owx`, `ontology_water_infra.owx` и `airtransportsys_ontology.owx`;
- выравнивает общие классы (`tm:Cargo ≡ air:Cargo`);
- связывает близкие концепты через `SubClassOf` (`tm:AirTransport ⊑ air:Aircraft`, `tm:Operator ⊑ air:Airline`, `tm:Infrastructure ⊑ air:AirportInfrastructure`);
- выравнивает свойства (`tm:locatedAt ≡ air:locatedAt`, `tm:carries ⊑ air:carriesCargo`, `tm:hasCapacity ≡ air:hasCapacity`, `tm:hasRange ≡ air:hasRange`, `tm:hasMaxSpeed ⊑ air:hasSpeed`).

Преимущество: исходные онтологии не ломаются и остаются самостоятельными, а интеграция делается в одном месте.

## Prefixes для запросов

```sparql
PREFIX tm:  <http://www.semanticweb.org/vivi/ontologies/2026/2/transport-merge#>
PREFIX air: <http://www.semanticweb.org/vivi/ontologies/2026/2/untitled-ontology-10#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
```

---

## 5 DL Query + SPARQL (экземпляры из всех онтологий сразу)

### 1) Все транспортные средства (земля+вода+авиа)

**DL Query**
```text
tm:TransportVehicle or air:Aircraft
```

**SPARQL**
```sparql
SELECT DISTINCT ?x WHERE {
  { ?x rdf:type tm:TransportVehicle . }
  UNION
  { ?x rdf:type air:Aircraft . }
}
ORDER BY ?x
```

### 2) Все грузовые объекты

**DL Query**
```text
tm:Cargo or air:Cargo
```

**SPARQL**
```sparql
SELECT DISTINCT ?x WHERE {
  { ?x rdf:type tm:Cargo . }
  UNION
  { ?x rdf:type air:Cargo . }
}
ORDER BY ?x
```

### 3) Все операторы/авиалинии

**DL Query**
```text
tm:Operator or air:Airline
```

**SPARQL**
```sparql
SELECT DISTINCT ?x WHERE {
  { ?x rdf:type tm:Operator . }
  UNION
  { ?x rdf:type air:Airline . }
}
ORDER BY ?x
```

### 4) Все объекты, у которых задано местоположение

**DL Query**
```text
(tm:locatedAt some (tm:Infrastructure or air:Airport))
or
(air:locatedAt some (tm:Infrastructure or air:Airport))
```

**SPARQL**
```sparql
SELECT DISTINCT ?x ?place WHERE {
  { ?x tm:locatedAt ?place . }
  UNION
  { ?x air:locatedAt ?place . }
}
ORDER BY ?x
```

### 5) Операционные сущности: рейсы и транспорт с маршрутами

**DL Query**
```text
(air:FlightOperation and (air:operatedBy some air:Airline))
or
(tm:TransportVehicle and (tm:servesRoute some tm:Route))
```

**SPARQL**
```sparql
SELECT DISTINCT ?x WHERE {
  {
    ?x rdf:type air:FlightOperation ;
       air:operatedBy ?op .
    ?op rdf:type air:Airline .
  }
  UNION
  {
    ?x rdf:type tm:TransportVehicle ;
       tm:servesRoute ?r .
    ?r rdf:type tm:Route .
  }
}
ORDER BY ?x
```

---

## 3 способа merge онтологий

### 1) Bridge ontology (рекомендуется)
- Делается отдельная "прослойка" с `owl:imports` + mapping axioms (`EquivalentClass`, `SubClassOf`, `EquivalentProperty`).
- Плюсы: не трогаются исходники, легко откатить/доработать, прозрачная интеграция.
- Минусы: требуется reasoner для полной отдачи результата.

### 2) Физический merge в одну онтологию
- Все аксиомы копируются в один файл, IRI унифицируются, дубликаты удаляются вручную.
- Плюсы: один артефакт, проще деплой.
- Минусы: сложно сопровождать, риск поломок и конфликтов IRI выше.

### 3) Виртуальный merge на уровне запросов (federation)
- Онтологии остаются раздельно, объединение делается в SPARQL (`UNION`, `SERVICE`, named graphs) и/или через ETL/mapping слой.
- Плюсы: минимум изменений в моделях, удобно при распределенных источниках.
- Минусы: логическая интеграция слабее, сложнее обеспечить единые выводы OWL-уровня.

