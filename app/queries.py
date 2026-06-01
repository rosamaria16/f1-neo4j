QUERY_CONSTRUCTOR_DOMINANCE = """
MATCH (c:Constructor)-[st:STANDING_IN]->(s:Season)
WHERE st.position = 1
RETURN s.year AS temporada, c.name AS campeon, st.points AS puntos, st.wins AS victorias
ORDER BY temporada DESC
"""

QUERY_TEAM_EARLY_DOMINANCE_STANDING_COMPARISON = """
MATCH (r:Race) WHERE r.season = $season
WITH r ORDER BY r.round
WITH collect(r)[0..5] as primeras_carreras
UNWIND primeras_carreras as r

MATCH (d:Driver)-[p:PARTICIPATED_IN]->(r)
MATCH (d)-[df:DROVE_FOR]->(c:Constructor)
WHERE df.season = r.season AND p.position <= 3

WITH c, count(*) AS podios_iniciales,
     sum(CASE WHEN p.position = 1 THEN 1 ELSE 0 END) AS victorias_iniciales

MATCH (c)-[st:STANDING_IN]->(s:Season)
WHERE s.year = $season

RETURN 
    c.name AS constructor,
    podios_iniciales,
    victorias_iniciales,
    st.position AS resultado_campeonato,
    st.wins AS victorias_totales
ORDER BY resultado_campeonato,  podios_iniciales DESC
"""

QUERY_TEAM_RELIABILITY = """
MATCH (d:Driver)-[p:PARTICIPATED_IN]->(r:Race)
MATCH (d)-[df:DROVE_FOR]->(c:Constructor)
WHERE df.season = r.season

WITH c, r.season AS temporada, count(*) AS participaciones_anyo,
     sum(CASE WHEN p.status <> 'Finished' AND NOT p.status CONTAINS 'Lap' THEN 1 ELSE 0 END) AS dnfs_anyo

MATCH (c)-[st:STANDING_IN]->(s:Season)
WHERE s.year = temporada

WITH c, collect({anyo:temporada, tasa_abandono:round(100*dnfs_anyo/participaciones_anyo, 2), resultado_mundial:st.position}) AS historial_fiabilidad,
     sum(dnfs_anyo) AS total_abandonos, sum(participaciones_anyo) AS total_participaciones
     
RETURN c.name AS equipo,
     total_abandonos AS abandonos_totales,
     total_participaciones AS participaciones,
     round(100.0*total_abandonos/total_participaciones, 1) AS tasa_global,
     historial_fiabilidad
ORDER BY tasa_global DESC
"""

QUERY_TEAM_EVOLUTION = """
MATCH (d:Driver)-[p:PARTICIPATED_IN]->(r:Race)
MATCH (d)-[df:DROVE_FOR]->(c:Constructor)
WHERE df.season = r.season
WITH c, r.season AS anyo, avg(p.position) AS pos_media
ORDER BY c.name, anyo
WITH c, collect({anyo: anyo, pos_media: round(pos_media, 2)}) AS tendencia
WHERE size(tendencia) >= 2
RETURN c.name AS equipo,
     tendencia,
     round(tendencia[0].pos_media - tendencia[-1].pos_media, 2) AS mejora
ORDER BY mejora DESC
"""

QUERY_DRIVER_CONSISTENCY = """
MATCH (d:Driver)-[p:PARTICIPATED_IN]->(r:Race)
WHERE r.season=$season
WITH d,
     sum(CASE WHEN p.position <=3 THEN 1 ELSE 0 END) AS podios,
     sum(CASE WHEN p.position = 1 THEN 1 ELSE 0 END) AS p1,
     sum(CASE WHEN p.position = 2 THEN 1 ELSE 0 END) AS p2,
     sum(CASE WHEN p.position = 3 THEN 1 ELSE 0 END) AS p3,
     sum(CASE WHEN p.status <> 'Finished' AND NOT p.status CONTAINS 'Lap' THEN 1 ELSE 0 END) AS dnfs

MATCH (d)-[st:STANDING_IN]->(s:Season)
WHERE s.year = $season
WITH st.position AS posicion, d, podios, p1, p2, p3, dnfs

RETURN d.fullName AS piloto, podios, p1 AS victorias, p2 AS segundos, p3 AS terceros, dnfs AS abandonos, posicion AS resultado_mundial
ORDER BY resultado_mundial
"""

QUERY_QUALIFYING_TO_RACE = """
MATCH (d:Driver)-[q:QUALIFIED]->(r:Race)<-[p:PARTICIPATED_IN]-(d)
WITH d, r,
     q.position AS pos_quali,
     p.position AS pos_carrera,
     q.position - p.position AS ganancia
WITH d, 
     count(*) AS participaciones,
     avg(ganancia) AS ganancia_media,
     sum(CASE WHEN ganancia > 0 THEN 1 ELSE 0 END) AS carreras_mejora,
     sum(CASE WHEN ganancia < 0 THEN 1 ELSE 0 END) AS carreras_empeora
RETURN d.fullName AS piloto,
       round(ganancia_media, 2) AS posiciones_ganadas_media,
       carreras_mejora AS veces_mejora,
       carreras_empeora AS veces_empeora,
       participaciones
ORDER BY ganancia_media DESC
"""

QUERY_DRIVER_SEASON_EVOLUTION = """
MATCH (d:Driver)-[p:PARTICIPATED_IN]->(r:Race)
MATCH (d)-[df:DROVE_FOR]->(c:Constructor)
WHERE df.season = r.season AND r.season IN [$season1, $season2]
WITH d, c.name AS equipo, r.season AS temporada,
     avg(p.position) AS pos_media,
     collect(p.position) AS posiciones
ORDER BY temporada
WITH d, equipo, collect({anyo: temporada, pos_media: round(pos_media, 2), posiciones: posiciones}) AS evolucion
WHERE size(evolucion) = 2
RETURN d.fullName AS piloto, equipo,
     evolucion,
     round(evolucion[0].pos_media - evolucion[1].pos_media, 2) AS mejora_posicion_media
ORDER BY mejora_posicion_media DESC
"""

QUERY_DRIVER_CIRCUIT_TYPE_PERFORMANCE = """
MATCH (d:Driver)-[p:PARTICIPATED_IN]->(r:Race)-[:HELD_AT]->(c:Circuit)
WHERE p.position IS NOT NULL AND p.position > 0
WITH d, c.circuit_type AS tipo_circuito,
     avg(p.position) AS pos_media,
     count(*) AS carreras,
     sum(CASE WHEN p.position <= 3 THEN 1 ELSE 0 END) AS podios,
     sum(CASE WHEN p.position = 1 THEN 1 ELSE 0 END) AS victorias
     
ORDER BY pos_media

WITH d, 
     collect({tipo: tipo_circuito, pos_media: round(pos_media, 2), carreras: carreras, podios: podios, victorias: victorias}) AS rendimiento

RETURN d.fullName AS piloto,
     rendimiento[0].tipo AS mejor_tipo_circuito,
     rendimiento[0].pos_media AS pos_media,
     rendimiento AS desglose_por_tipo
"""

QUERY_DRIVERS_MOST_DIFFERENT_TEAMS = """
MATCH (d:Driver)-[df:DROVE_FOR]->(c:Constructor)
WITH d, collect(DISTINCT c.name) AS equipos, count(DISTINCT c) AS num_equipos,
     min(df.season) AS primera_temporada, max(df.season) AS ultima_temporada
WHERE num_equipos >= 2
RETURN d.fullName AS piloto,
       equipos,
       num_equipos,
       ultima_temporada - primera_temporada + 1 AS temporadas_activo,
       round(1.0*num_equipos/(ultima_temporada-primera_temporada + 1), 2) AS equipos_por_temporada
ORDER BY num_equipos DESC, equipos_por_temporada DESC
LIMIT 5
"""

QUERY_DRIVER_NETWORK = """
MATCH (d:Driver {driver_id: $driver_id})-[df1:DROVE_FOR]->(c:Constructor)<-[df2:DROVE_FOR]-(teammate:Driver)
WHERE d <> teammate
WITH d, c, teammate, collect(DISTINCT df1.season) AS temporadas_piloto,
          collect(DISTINCT df2.season) AS temporadas_teammate
          
WITH d,c,teammate,
     any(anyo in temporadas_teammate WHERE anyo IN temporadas_piloto) AS directo
     
WITH d,c, collect(DISTINCT CASE WHEN directo THEN teammate.fullName END) AS companeros_directos,
          collect(DISTINCT CASE WHEN NOT directo THEN teammate.fullName END) AS companeros_indirectos

RETURN d.fullName AS piloto, c.name AS equipo, companeros_directos, companeros_indirectos
"""

QUERY_TEAMMATES_MOST_YEARS = """
MATCH (d1:Driver)-[df1:DROVE_FOR]->(c:Constructor)<-[df2:DROVE_FOR]-(d2:Driver)
WHERE df1.season = df2.season AND d1.driver_id <> d2.driver_id
WITH d1, d2, c, collect(DISTINCT df1.season) AS temporadas
RETURN d1.fullName AS piloto1, d2.fullName AS piloto2, 
     c.name AS equipo, temporadas, size(temporadas) AS anyos_juntos
ORDER BY anyos_juntos DESC
LIMIT 5
"""

QUERY_DRIVER_RIVALRIES = """
MATCH (d1:Driver)-[p1:PARTICIPATED_IN]->(r:Race)<-[p2:PARTICIPATED_IN]-(d2:Driver)
WHERE d1.driver_id < d2.driver_id
  AND p1.position IS NOT NULL 
  AND p2.position IS NOT NULL
  AND abs(p1.position - p2.position) <= 2
WITH d1, d2, count(r) AS batallas_cercanas,
     sum(CASE WHEN p1.position < p2.position THEN 1 ELSE 0 END) AS victorias_d1,
     sum(CASE WHEN p2.position < p1.position THEN 1 ELSE 0 END) AS victorias_d2
WHERE batallas_cercanas >= 5
RETURN d1.fullName AS piloto1, 
       d2.fullName AS piloto2,
       batallas_cercanas,
       victorias_d1 AS gana_p1,
       victorias_d2 AS gana_p2,
       CASE WHEN victorias_d1 > victorias_d2 THEN d1.fullName
          WHEN victorias_d2 > victorias_d1 THEN d2.fullName
          ELSE 'Empate' END AS domina
ORDER BY batallas_cercanas DESC
LIMIT 10
"""

QUERY_SIMILAR_CAREER_PATH = """
MATCH (d1:Driver {driver_id: $driver_id})-[:DROVE_FOR]->(c:Constructor)<-[:DROVE_FOR]-(d2:Driver)
WHERE d1 <> d2
WITH d2, collect(DISTINCT c.name) AS equipos_comunes, count(DISTINCT c) AS num_equipos
MATCH (d1:Driver {driver_id: $driver_id})-[:DROVE_FOR]->(c1:Constructor)
WITH d2, equipos_comunes, num_equipos, count(DISTINCT c1) AS total_equipos_d1
RETURN d2.fullName AS piloto_similar, 
     equipos_comunes,
     num_equipos AS equipos_compartidos,
     round(100.0 * num_equipos / total_equipos_d1, 1) AS porcentaje_similitud
ORDER BY num_equipos DESC, porcentaje_similitud DESC
LIMIT 10
"""

QUERY_TEAMMATE_CHAIN = """
MATCH path = SHORTEST 1 (
    (d1:Driver {driver_id: $driver1})-[:DROVE_FOR*]-(d2:Driver {driver_id: $driver2})
)
WITH nodes(path) AS nodos
UNWIND range(0, size(nodos)-1) AS grado
WITH nodos[grado] AS nodo, grado 
RETURN grado,
     CASE WHEN "Driver" IN labels(nodo) THEN 'Piloto - ' + nodo.fullName 
          WHEN "Constructor" IN labels(nodo) THEN 'Constructor - ' + nodo.name 
          END AS elemento
ORDER BY grado
"""

QUERY_CIRCUIT_SPECIALISTS = """
MATCH (c:Circuit)<-[:HELD_AT]-(r:Race)<-[p:PARTICIPATED_IN]-(d:Driver)
WHERE p.position IS NOT NULL AND p.position > 0
WITH c, d,
     count(r) AS carreras,
     avg(p.position) AS pos_media,
     sum(CASE WHEN p.position = 1 THEN 1 ELSE 0 END) AS victorias,
     sum(CASE WHEN p.position <= 3 THEN 1 ELSE 0 END) AS podios
WHERE carreras >= 2
WITH c, d, carreras, round(pos_media, 2) AS pos_media, victorias, podios
ORDER BY c.name, pos_media ASC
WITH c, collect({piloto: d.fullName, pos_media: pos_media, victorias: victorias, podios: podios, carreras: carreras})[0..3] AS top3
RETURN c.name AS circuito,
       c.country AS pais,
       c.circuit_type AS tipo,
       top3[0] AS primero,
       top3[1] AS segundo,
       top3[2] AS tercero
ORDER BY circuito
"""