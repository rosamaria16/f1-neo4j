from neo4j_connection import get_session
import queries

#Funciones auxiliares
def get_drivers_list() -> list:
    try:
        with get_session() as session:
            result = session.run("""
                MATCH (d:Driver)
                RETURN d.driver_id AS driver_id, d.fullName AS fullName
                ORDER BY d.fullName
            """)
            return [dict(r) for r in result]
    except:
        return []

def get_seasons_list() -> list:
    try:
        with get_session() as session:
            result = session.run("""
                MATCH ANY (r:Race)
                RETURN DISTINCT r.season AS season
                ORDER BY season
                """)
            return [dict(r) for r in result]
    except:
        return []

#Diccionario queries
QUERY_CATEGORIES = {
    
    "teams": {
        "title": "Análisis de Equipos",
        "description": """
        Explora el rendimiento de los constructores a lo largo de los años.
        """,
        "queries": {
            "constructor_dominance": {
                "name": "Campeones por Temporada",
                "description": "¿Qué equipo ha ganado cada temporada?",
                "query": getattr(queries, "QUERY_CONSTRUCTOR_DOMINANCE"),
                "display": "table",
                "insight": """
                Lo común es que en el primer año de reglamento haya un equipo dominante claro. Con el paso del tiempo, 
                el resto de equipos avanzan y quedan algo más igualados, quedando los resultados más reñidos. Esto se puede ver en el número de victorias durante estos años de "transición de dominancia",
                donde los equipos que ganan los campeonatos suelen tener menor margen de victorias con respecto a temporadas anteriores.
                """
            },
             
            "team_early_dominance": {
                "name": "Dominio Temprano",
                "description": "¿Qué equipos son más fuertes al comienzo del año?",
                "query": getattr(queries, "QUERY_TEAM_EARLY_DOMINANCE_STANDING_COMPARISON"),
                "display": "table",
                "params": {
                    "season": {
                        "type": "season",
                        "label": "Temporada"
                    }
                },
                "insight": """
                El inicio de temporada, aunque no sea determinante, sí da una buena 
                visión de cómo puede avanzar el campeonato. Especialmente durante los 
                primeros años de una nueva regulación, la relación entre resultados 
                iniciales y finales de un constructor suele ser estrecha.
                """
            },
            
            "team_reliability": {
                "name": "Fiabilidad",
                "description": "¿Qué equipos tienen mayor tasa de abandono durante el año? ¿Hay relación entre esta tasa y sus resultados en el mundial?",
                "query": getattr(queries, "QUERY_TEAM_RELIABILITY"),
                "display": "table",
                "insight": """
                Es común que los equipos tengan problemas de fiabilidad al principio de cada temporada, especialmente
                durante el primer año de una nueva regulación al estar adaptándose a ella. Es interesante ver el resultado final en el mundial
                frente al número de DNFs que sufre un equipo y comparar en qué posición quedaron en años donde tuvieron más o menos abandonos.
                """
            },
            
            "team_evolution": {
                "name": "Evolución",
                "description": "¿Qué equipos han ido mejorando sus resultados en el mundial a lo largo del tiempo?",
                "query": getattr(queries, "QUERY_TEAM_EVOLUTION"),
                "display": "table",
                "insight": """
                A medida que avanza el tiempo en una era de regulación dada, lo esperable es que el rendimiento de los equipos se iguale y 
                las competiciones sean más reñidas entre ellos tras enfocar sus esfuerzos en mejorar sus monoplazas. A partir de estos datos, 
                es interesante ver aquellos equipos que mejoran, que empeoran, o que quizá no tienen malos resultados pero se han quedado estancados.
                """
            }
        }
    },


    "drivers": {
        "title": "Análisis de Pilotos", 
        "description": """
        Analiza el rendimiento de cada piloto.
        """,
        "queries": {
            "podium_consistency": {
                "name": "Consistencia",
                "description": """
                ¿Qué pilotos son más consistentes con sus resultados?
                """,
                "query": getattr(queries, "QUERY_DRIVER_CONSISTENCY"),
                "display": "table",
                "params": {
                    "season": {
                        "type": "season",
                        "label": "Temporada"
                    }
                },
                "insight": """
                En la Fórmula 1, lo que apremia es la consistencia, no el número de victorias. 
                Un piloto consistente y un coche fiable son clave para llegar a lo más alto del mundial. 
                """
            },
            
            "qualifying_to_race": {
                "name": "Clasificación vs Carrera",
                "description": "¿Quién gana más posiciones en carrera, partiendo de su posición de clasificación?",
                "query": getattr(queries, "QUERY_QUALIFYING_TO_RACE"),
                "display": "table",
                "insight": """
                Igual que hay coches que son mejores a una vuelta y luego peores en carrera y viceversa, 
                hay pilotos que pueden clasificar muy bien y luego obtener resultados inferiores. También puede 
                darse el caso contrario, donde en carrera mejoran. Esto depende de muchos factores, siendo algunos de ellos
                el manejo de desgaste de neumáticos en carrera, las estrategias de equipo, accidentes propios o ajenos,
                tiempos de parada en boxes, Safety Cars...
                """
                
            },
            
            "driver_evolution": {
                "name": "Evolución entre Temporadas",
                "description": "¿Cómo ha evolucionado cada piloto entre dos temporadas dadas?",
                "query": getattr(queries, "QUERY_DRIVER_SEASON_EVOLUTION"),
                "display": "table",
                "params": {
                    "season1": {
                        "type": "season",
                        "label": "Temporada"
                    },
                    "season2": {
                        "type": "season",
                        "label": "Temporada"
                    }
                },
                "insight": """Si hay dos pilotos de la misma escudería que tienen aumentos
                similares, es indicador de que el coche/equipo ha dado un salto cualitativo.
                """
            },
            
            "driver_circuit_type": {
                "name": "Rendimiento por Tipo de Circuito",
                "description": "¿Qué tipo de circuito (callejero, permanente, híbrido) se le da mejor a cada piloto?",
                "query": getattr(queries, "QUERY_DRIVER_CIRCUIT_TYPE_PERFORMANCE"),
                "display": "table",
                "insight": """
                Algunos pilotos destacan en circuitos callejeros por su precisión,
                mientras que otros brillan en permanentes de alta velocidad.
                Los híbridos suelen favorecer a pilotos versátiles.
                """
            },
            "most_teams": {
                "name": "Pilotos con más equipos",
                "description": "¿Qué pilotos han corrido para más equipos?",
                "query": getattr(queries, "QUERY_DRIVERS_MOST_DIFFERENT_TEAMS"),
                "display": "table"
            },
            "circuit_specialists": {
                "name": "Especialistas por Circuito",
                "description": "¿Qué pilotos tienen mejor rendimiento en cada circuito?",
                "query": getattr(queries, "QUERY_CIRCUIT_SPECIALISTS"),
                "display": "table",
                "insight": """
                Algunos pilotos destacan consistentemente en ciertos circuitos por su 
                estilo de conducción, experiencia o adaptación al coche.
                """
            }
        }
    },
    

    "relationships": {
        "title": "Red Social",
        "description": """
        Análisis de relaciones entre pilotos,
        compañeros de equipo, rivalidades y conexiones a través de los años.
        """,
        "queries": {
            "driver_network": {
                "name": "Conexiones y compañeros",
                "description": """¿Para qué escuderías ha corrido un piloto? 
                ¿Quiénes han sido sus compañeros de equipo en cada una?
                ¿Con quiénes ha compartido equipo indirectamente?""",
                "query": getattr(queries, "QUERY_DRIVER_NETWORK"),
                "params": {
                    "driver_id": {
                        "type": "driver",
                        "label": "Piloto"
                    }
                },
                "display": "table"
            },
            
            "teammates": {
                "name": "Parejas más antiguas",
                "description": "¿Qué parejas de pilotos han compartido más años juntos?",
                "query": getattr(queries, "QUERY_TEAMMATES_MOST_YEARS"),
                "display": "table",
            },
            
            "rivalries": {
                "name": "Rivalidades",
                "description": "¿Qué pilotos suelen terminar cerca en carrera?",
                "query": getattr(queries, "QUERY_DRIVER_RIVALRIES"),
                "display": "table",
                "insight": "Las rivalidades más intensas suelen ser entre compañeros de equipo o pilotos de equipos similares"
            },
            "similar_careers": {
                "name": "Carreras Similares",
                "description": "¿Qué pilotos han tenido trayectorias parecidas?",
                "query": getattr(queries, "QUERY_SIMILAR_CAREER_PATH"),
                "params": {
                    "driver_id": {
                        "type": "driver",
                        "label": "Piloto de referencia"
                    }
                },
                "display": "table",
                "insight": "A mayor cantidad de pilotos se tenga en la base de datos, más interesantes y veraces serán los datos mostrados."
            },
            "shortest_path": {
                "name": "Camino más Corto entre Pilotos",
                "description": "¿Cómo se conectan dos pilotos cualesquiera?",
                "query": getattr(queries, "QUERY_TEAMMATE_CHAIN"),
                "params": {
                    "driver1": {
                        "type": "driver",
                        "label": "Piloto 1"
                    },
                    "driver2": {
                        "type": "driver",
                        "label": "Piloto 2"
                    }
                },
                "display": "table"
            }
        }
    }
}

