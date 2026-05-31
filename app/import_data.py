import csv
import os
from neo4j_connection import get_session

CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'csv')


def clear_database():
    with get_session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("Base de datos limpiada")


def create_constraints():
    constraints = [("Driver", "driver_id"),("Constructor", "constructor_id"),("Circuit", "circuit_id"),("Race", "race_id"),]
    
    with get_session() as session:
        for label, prop in constraints:
            try:
                session.run(f"""
                    CREATE CONSTRAINT {label.lower()}_{prop.lower()}_unique IF NOT EXISTS 
                    FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE""")
                
            except Exception as e:
                print(f"Constraint {label}.{prop}: {e}")
                
        print("Constraints creados")


def load_drivers():
    filepath = os.path.join(CSV_PATH, 'drivers.csv')
    count = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with get_session() as session:
            for row in reader:
                session.run("""
                    MERGE (d:Driver {driver_id: $driver_id})
                    SET d.givenName = $givenName,
                        d.familyName = $familyName,
                        d.fullName = $givenName + ' ' + $familyName,
                        d.nationality = $nationality,
                        d.dob = $dob
                    """, row)
                count += 1
    
    print(f"Cargados {count} pilotos")


def load_constructors():
    filepath = os.path.join(CSV_PATH, 'constructors.csv')
    count = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with get_session() as session:
            for row in reader:
                session.run("""
                    MERGE (c:Constructor {constructor_id: $constructor_id})
                    SET c.name = $name,
                        c.nationality = $nationality,
                        c.predecessor = $predecessor
                    """, row)
                count += 1
    
    print(f"{count} constructores cargados")


def load_circuits():
    filepath = os.path.join(CSV_PATH, 'circuits.csv')
    count = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with get_session() as session:
            for row in reader:
                session.run("""
                    MERGE (c:Circuit {circuit_id: $circuit_id})
                    SET c.name = $name,
                        c.country = $country,
                        c.circuit_type = $circuit_type
                    """, row)
                count += 1
    
    print(f"{count} circuitos cargados")


def load_races():
    filepath = os.path.join(CSV_PATH, 'races.csv')
    count = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with get_session() as session:
            for row in reader:
                session.run("""
                    MERGE (r:Race {race_id: $race_id})
                    SET r.season = toInteger($season),
                        r.round = toInteger($round),
                        r.name = $race_name
                    MATCH (c:Circuit {circuit_id: $circuit_id})
                    MERGE (r)-[:HELD_AT]->(c)
                    """, row)
                count += 1
    
    print(f"{count} carreras cargadas relacionadas con la relación HELD_AT")


def load_results():
    filepath = os.path.join(CSV_PATH, 'results.csv')
    count = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with get_session() as session:
            for row in reader:
                session.run("""
                    MATCH (d:Driver {driver_id: $driver_id})
                    MATCH (r:Race {race_id: $race_id})
                    
                    MERGE (d)-[p:PARTICIPATED_IN]->(r)
                    SET p.grid = toInteger($grid),
                        p.position = CASE WHEN $position = '' THEN null
                                    WHEN toInteger($position) IS NOT NULL THEN toInteger($position)
                                    ELSE 23 END,
                        p.position_order = toInteger($position_order),
                        p.points = toFloat($points),
                        p.laps = toInteger($laps),
                        p.status = $status,
                        p.constructor_id = $constructor_id
                    """, row)
                count += 1
    
    print(f"{count} resultados de carrera cargados con la relación PARTICIPATED_IN")


def load_qualifying():
    filepath = os.path.join(CSV_PATH, 'qualifying.csv')
    count = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with get_session() as session:
            for row in reader:
                session.run("""
                    MATCH (d:Driver {driver_id: $driver_id})
                    MATCH (r:Race {race_id: $race_id})
                    MERGE (d)-[q:QUALIFIED]->(r)
                    SET q.position = toInteger($position),
                        q.q1 = $q1,
                        q.q2 = $q2,
                        q.q3 = $q3
                    """, row)
                count += 1
    
    print(f"{count} clasificaciones de carrera cargadas con la relación QUALIFIED")


def load_driver_standings():
    filepath = os.path.join(CSV_PATH, 'driver_standings.csv')
    count = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with get_session() as session:
            for row in reader:

                session.run("""
                    MERGE (s:Season {year: toInteger($season)})
                    MATCH (d:Driver {driver_id: $driver_id})
                    MERGE (d)-[st:STANDING_IN]->(s)
                    SET st.position = toInteger($position),
                        st.points = toFloat($points),
                        st.wins = toInteger($wins),
                        st.round = toInteger($round)
                    """, row)
                count += 1
    
    print(f"{count} resultados finales de temporadas de pilotos cargados con la relación STANDING_IN")


def load_constructor_standings():
    filepath = os.path.join(CSV_PATH, 'constructor_standings.csv')
    count = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with get_session() as session:
            for row in reader:
                session.run("""
                    MERGE (s:Season {year: toInteger($season)})
                    WITH s
                    MATCH (c:Constructor {constructor_id: $constructor_id})
                    MERGE (c)-[st:STANDING_IN]->(s)
                    SET st.position = toInteger($position),
                        st.points = toFloat($points),
                        st.wins = toInteger($wins),
                        st.round = toInteger($round)
                    """, row)
                count += 1
    
    print(f"{count} resultados finales de temporadas de constructores cargados con la relación STANDING_IN")


def load_driver_constructors():
    filepath = os.path.join(CSV_PATH, 'driver_constructors.csv')
    count = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with get_session() as session:
            for row in reader:
                session.run("""
                    MATCH (d:Driver {driver_id: $driver_id})
                    MATCH (c:Constructor {constructor_id: $constructor_id})
                    MERGE (d)-[df:DROVE_FOR {season: toInteger($season)}]->(c)
                    """, row)
                count += 1
    
    print(f"{count} relaciones piloto-escudería por temporada cargadas (DROVE_FOR)")


def import_all():
    
    clear_database()
    create_constraints()
    
    print("--Cargando nodos--")
    load_drivers()
    load_constructors()
    load_circuits()
    
    print("--Cargando carreras y relaciones--")
    load_races()
    load_results()
    load_qualifying()
    
    print("--Cargando relaciones piloto-escudería--")
    load_driver_constructors()
    
    print("--Cargando resultados finales de temporadas--")
    load_driver_standings()
    load_constructor_standings()
    
    print("--Importación completada--")


if __name__ == "__main__":
    import_all()
