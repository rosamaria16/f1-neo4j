# F1 Analytics

- **Autora:** Rosa María Espinosa Martínez, rosespmar@alum.us.es
- **Asignatura:** Complemento de base de datos. Grado en Ingeniería Informática - Ingeniería del Software. Universidad de Sevilla.
- **Curso académico:** 2025/2026
- **Repositorio:** https://github.com/rosamaria16/F1-Analytics
- **Enlace al despliegue:** https://f1-analytics-neo4j.streamlit.app/


## Descripción
F1 Analytics permite al usuario visualizar consultas de diversa índole sobre una base de datos no relacional (Neo4j+AuraDB).

# Índice
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuración del entorno](#configuración-del-entorno)
- [Ejecución](#ejecución)
- [Consultas Disponibles](#análisis-de-equipos)
- [Modelado de Datos](#modelado-de-datos)
  - [Nodos](#nodos)
  - [Relaciones](#relaciones)
  - [Esquemas Cypher](#esquemas-cypher)

## Estructura del Proyecto
- `app/`: Código fuente de la aplicación. Contiene los archivos de importación de datos, conexión a Neo4j, consultas a la base de datos y el frontend.
- `csv/`: Archivos .csv con los datos cargados en la base de datos.
- `resources/`: Contiene tipografías concretas para el título de la aplicación web.

## Configuración del entorno
1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`
3. Activar el entorno virtual: `.\venv\Scripts\activate` (o `source venv/bin/activate` en entornos Linux)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Añadir variables de entorno (ejemplo disponible en el archivo `.env.example`).

## Ejecución
1. Para poblar la base de datos, ejecutar dentro del directorio `\app` el comando `python import_data.py`
2. Para ejecutar la aplicación web en local, ejecutar el comando `streamlit run app/streamlit_app.py` en el directorio raíz del proyecto.


Una vez en la aplicación, se da a elegir entre tres categorías de consultas:

### Análisis de Equipos

| Query | Descripción | Relevancia |
|-------|-------------|------------|
| **Campeones por Temporada** | Muestra qué equipo ganó cada campeonato con sus puntos y victorias | Permite identificar ciclos de dominancia y transiciones de poder entre equipos. Refleja cómo los cambios de reglamento afectan a la competitividad de los equipos a lo largo de los años. |
| **Dominio Temprano** | Analiza qué equipos destacan en las primeras 5 carreras vs. resultado final | Valida si el rendimiento inicial predice el resultado del campeonato, especialmente relevante en años de cambio de regulación. |
| **Fiabilidad** | Calcula la tasa de abandono (DNF/DSQ) por equipo y temporada | La fiabilidad es crucial para ganar campeonatos, pues no se suma ningún punto si se abandona. Relaciona abandonos con resultados finales para mostrar su impacto real. |
| **Evolución** | Mide la mejora de posición media de cada equipo a lo largo del tiempo | Identifica equipos en ascenso/descenso y detecta estancamientos. Es útil para analizar tendencias a largo plazo. |

### Análisis de Pilotos

| Query | Descripción | Relevancia |
|-------|-------------|------------|
| **Consistencia** | Muestra podios, victorias y abandonos por piloto en una temporada | En la F1, la consistencia es la que gana los campeonatos. Un piloto con menos victorias pero más podios puede superar a uno con más victorias pero irregular en sus resultados. |
| **Clasificación vs Carrera** | Compara la posición de clasificación con el resultado final de cada carrera | Revela habilidades de adelantamiento, gestión de neumáticos y adaptación a circunstancias de carrera. Diferencia pilotos "de sábado" (día de clasificación) vs "de domingo"(día de carrera). Si se comparan entre compañeros de equipo, un ascenso/descenso parejo puede ser indicador de varios aspectos del coche (más rápido a una vuelta, menor desgaste de neumáticos, mejor velocidad punta...).|
| **Evolución entre Temporadas** | Compara rendimiento del mismo piloto en dos años | Detecta progresión de pilotos. Si ambos pilotos de un equipo mejoran igual, indica mejora del coche. |
| **Rendimiento por Tipo de Circuito** | Clasifica pilotos según circuitos callejeros/permanentes/híbridos | Identifica especialistas: algunos pilotos brillan en callejeros, otros en permanentes. |
| **Piloto con más Equipos** | Lista a los pilotos que han corrido para más constructores | Muestra versatilidad y longevidad. Pilotos que han pasado por muchos equipos tienen amplia experiencia pero también pueden indicar inestabilidad. |
| **Especialistas por Circuito** | Top 3 pilotos con mejor rendimiento en cada circuito | Algunos pilotos dominan ciertos trazados concretos por su estilo de conducción o experiencia. |

### Red Social

| Query | Descripción | Relevancia |
|-------|-------------|------------|
| **Conexiones y Compañeros** | Muestra compañeros directos e indirectos de un piloto por equipo | Explota la naturaleza de grafos de Neo4j para mostrar la red de relaciones entre compañeros. |
| **Parejas más Antiguas** | Identifica duplas de pilotos que más años han compartido equipo | Las relaciones prolongadas suelen significar que uno de los dos pilotos es el "primero", mientras que el otro asume el rol de "ayudante" cuando el equipo así lo estima. |
| **Rivalidades** | Detecta pilotos que frecuentemente terminan en posiciones cercanas | Identifica enfrentamientos recurrentes en pista más allá de compañeros de equipo en base a sus resultados en carrera. |
| **Carreras Similares** | Encuentra pilotos con trayectorias parecidas (mismos equipos) | Permite comparaciones históricas: "¿Quién tuvo una carrera similar a X?". Aprovecha relaciones de grafo. |
| **Camino más Corto entre Pilotos** | Calcula la cadena de conexiones entre dos pilotos cualesquiera | Query de grafos (SHORTEST PATH). Demuestra cómo cualquier piloto está conectado con otro a través de equipos compartidos y otros pilotos. |

---

> **¿Por qué estas consultas?** Cada consulta está diseñada para aprovechar las capacidades de Neo4j como base de datos de grafos:
> - Las queries de **Análisis de Equipos** analizan relaciones `STANDING_IN`, `DROVE_FOR` y `PARTICIPATED_IN` para extraer métricas agregadas.
> - Las queries de **Análisis de Pilotos** combinan múltiples relaciones para calcular estadísticas de rendimiento individual.
> - Las queries de **Red Social** explotan la naturaleza de grafos con patrones como caminos, conexiones directas/indirectas y cadenas de relaciones, algo difícil de lograr con bases de datos relacionales.


## Modelado de Datos

### Nodos

| Nodo | Propiedades | Descripción |
|------|-------------|-------------|
| **Driver** | `driver_id`, `givenName`, `familyName`, `fullName`, `nationality`, `dob` | Piloto de F1 |
| **Constructor** | `constructor_id`, `name`, `nationality`, `predecessor` | Escudería/equipo |
| **Circuit** | `circuit_id`, `name`, `country`, `circuit_type` | Circuito (callejero/permanente/híbrido) |
| **Race** | `race_id`, `season`, `round`, `name` | Gran Premio específico |
| **Season** | `year` | Temporada del campeonato |

### Relaciones

| Relación | Origen → Destino | Propiedades | Descripción |
|----------|------------------|-------------|-------------|
| **PARTICIPATED_IN** | Driver → Race | `grid`, `position`, `position_order`, `points`, `laps`, `status`, `constructor_id` | Participación de un piloto en una carrera con su resultado |
| **QUALIFIED** | Driver → Race | `position`, `q1`, `q2`, `q3` | Resultado de clasificación del piloto |
| **DROVE_FOR** | Driver → Constructor | `season` | El piloto corrió para ese equipo en esa temporada |
| **STANDING_IN** | Driver/Constructor → Season | `position`, `points`, `wins`, `round` | Clasificación final en el campeonato |
| **HELD_AT** | Race → Circuit | - | La carrera se celebró en ese circuito |

### Esquemas Cypher

#### Creación de Nodos

```cypher
// Piloto
CREATE (d:Driver {
    driver_id: "hamilton",
    givenName: "Lewis",
    familyName: "Hamilton",
    fullName: "Lewis Hamilton",
    nationality: "British",
    dob: "1985-01-07"
})

// Constructor
CREATE (c:Constructor {
    constructor_id: "mercedes",
    name: "Mercedes",
    nationality: "German",
    predecessor: ""
})

// Circuito
CREATE (ci:Circuit {
    circuit_id: "monaco",
    name: "Circuit de Monaco",
    country: "Monaco",
    circuit_type: "street"
})

// Carrera
CREATE (r:Race {
    race_id: "2024_monaco",
    season: 2024,
    round: 8,
    name: "Monaco Grand Prix"
})

// Temporada
CREATE (s:Season {year: 2024})
```

#### Creación de Relaciones

```cypher
// Piloto participó en carrera
MATCH (d:Driver {driver_id: "hamilton"})
MATCH (r:Race {race_id: "2024_monaco"})
CREATE (d)-[:PARTICIPATED_IN {
    grid: 3,
    position: 2,
    position_order: 2,
    points: 18.0,
    laps: 78,
    status: "Finished",
    constructor_id: "mercedes"
}]->(r)

// Piloto clasificó en carrera
MATCH (d:Driver {driver_id: "hamilton"})
MATCH (r:Race {race_id: "2024_monaco"})
CREATE (d)-[:QUALIFIED {
    position: 3,
    q1: "1:12.345",
    q2: "1:11.234",
    q3: "1:10.567"
}]->(r)

// Piloto corrió para constructor
MATCH (d:Driver {driver_id: "hamilton"})
MATCH (c:Constructor {constructor_id: "mercedes"})
CREATE (d)-[:DROVE_FOR {season: 2024}]->(c)

// Clasificación final de temporada (piloto)
MATCH (d:Driver {driver_id: "hamilton"})
MATCH (s:Season {year: 2024})
CREATE (d)-[:STANDING_IN {
    position: 3,
    points: 211.0,
    wins: 2,
    round: 24
}]->(s)

// Clasificación final de temporada (constructor)
MATCH (c:Constructor {constructor_id: "mercedes"})
MATCH (s:Season {year: 2024})
CREATE (c)-[:STANDING_IN {
    position: 4,
    points: 409.0,
    wins: 3,
    round: 24
}]->(s)

// Carrera celebrada en circuito
MATCH (r:Race {race_id: "2024_monaco"})
MATCH (ci:Circuit {circuit_id: "monaco"})
CREATE (r)-[:HELD_AT]->(ci)
```

#### Queries de Ejemplo (Traversal de Grafo)

```cypher
// Encontrar todos los compañeros de equipo de un piloto
MATCH (d:Driver {driver_id: "hamilton"})-[:DROVE_FOR]->(c:Constructor)<-[:DROVE_FOR]-(teammate:Driver)
WHERE d <> teammate
RETURN DISTINCT teammate.fullName, c.name

// Camino más corto entre dos pilotos
MATCH path = SHORTEST 1 (
    (d1:Driver {driver_id: "hamilton"})-[:DROVE_FOR*]-(d2:Driver {driver_id: "verstappen"})
)
RETURN nodes(path)

// Rendimiento de un piloto por tipo de circuito
MATCH (d:Driver)-[p:PARTICIPATED_IN]->(r:Race)-[:HELD_AT]->(c:Circuit)
WHERE d.driver_id = "hamilton"
RETURN c.circuit_type, avg(p.position) AS pos_media, count(*) AS carreras
ORDER BY pos_media
```

### Constraints (Unicidad)

```cypher
CREATE CONSTRAINT driver_driver_id_unique IF NOT EXISTS 
FOR (n:Driver) REQUIRE n.driver_id IS UNIQUE

CREATE CONSTRAINT constructor_constructor_id_unique IF NOT EXISTS 
FOR (n:Constructor) REQUIRE n.constructor_id IS UNIQUE

CREATE CONSTRAINT circuit_circuit_id_unique IF NOT EXISTS 
FOR (n:Circuit) REQUIRE n.circuit_id IS UNIQUE

CREATE CONSTRAINT race_race_id_unique IF NOT EXISTS 
FOR (n:Race) REQUIRE n.race_id IS UNIQUE
```
