import streamlit as st
from neo4j_connection import get_session
from query_categories import *

st.set_page_config(
    page_title="F1 Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 4rem;
        font-weight: 800;
        color: #E10600;
        text-align: center;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .sub-header {
        font-size: 1.3rem;
        color: var(--text-color, inherit);
        opacity: 0.7;
        text-align: center;
        margin-bottom: 2rem;
    }
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
    }
    .custom-table th {
        border: 1px solid var(--border-color);
        padding: 8px;
        text-align: left;
        background-color: var(--header-bg);
    }
    .custom-table td {
        border: 1px solid var(--border-color);
        padding: 8px;
        vertical-align: top;
    }
    
    /* Light theme */
    @media (prefers-color-scheme: light) {
        :root {
            --border-color: #ddd;
            --header-bg: #f5f5f5;
        }
    }
    
    /* Dark theme */
    @media (prefers-color-scheme: dark) {
        :root {
            --border-color: #444;
            --header-bg: #1e1e1e;
        }
    }
    
    /* Streamlit theme detection fallback */
    [data-testid="stAppViewContainer"] {
        --border-color: #ddd;
        --header-bg: #f5f5f5;
    }
    [data-testid="stAppViewContainer"][data-theme="dark"],
    .stApp[data-theme="dark"] [data-testid="stAppViewContainer"],
    html[data-theme="dark"] [data-testid="stAppViewContainer"] {
        --border-color: #444;
        --header-bg: #1e1e1e;
    }
</style>
""", unsafe_allow_html=True)


def execute_query(query: str, params: dict = None) -> list:
    try:
        with get_session() as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]
    except Exception as e:
        st.error(f"Error ejecutando query: {e}")
        return []


def format_value(value) -> str:
    if isinstance(value, list):
        formatted = []
        for item in value:
            if isinstance(item, dict):
                formatted.append(", ".join(f"{k}: {v}" for k, v in item.items()))
            else:
                formatted.append(str(item))
        return "<br>".join(formatted)
    if isinstance(value, dict):
        return "<br>".join(f"{k}: {v}" for k, v in value.items())
    return str(value) if value is not None else ""


def has_complex_data(results: list) -> bool:
    return any(
        isinstance(v, (dict, list))
        for record in results
        for v in record.values()
    )


def render_html_table(results: list):
    headers = list(results[0].keys())
    
    rows = []
    for record in results:
        cells = [f'<td>{format_value(record.get(h, ""))}</td>' for h in headers]
        rows.append("<tr>" + "".join(cells) + "</tr>")
    
    html = f'''
    <table class="custom-table">
        <tr>{"".join(f'<th>{h}</th>' for h in headers)}</tr>
        {"".join(rows)}
    </table>
    '''
    st.markdown(html, unsafe_allow_html=True)


def render_results(results: list, display_type: str = "table"):
    if not results:
        st.info("No se encontraron resultados")
        return

    if display_type == "table":
        if has_complex_data(results):
            render_html_table(results)
        else:
            st.dataframe(results, use_container_width=True)
    elif display_type == "list":
        for record in results:
            keys = list(record.keys())
            main = record.get(keys[0], "")
            details = " | ".join(f"{k}: {format_value(v)}" for k, v in record.items() if k != keys[0])
            st.write(f"**{main}** - {details}")

def render_param_input(param_name: str, param_config: dict, query_key: str) -> any:
    key = f"{query_key}_{param_name}"
    label = param_config["label"]
    param_type = param_config["type"]
    
    if param_type == "driver":
        drivers = get_drivers_list()
        return st.selectbox(
            label,
            options=[d["driver_id"] for d in drivers],
            format_func=lambda x: next((d["fullName"] for d in drivers if d["driver_id"] == x), x),
            key=key
        )
    elif param_type == "constructor":
        constructors = get_constructors_list()
        return st.selectbox(
            label,
            options=[c["constructor_id"] for c in constructors],
            format_func=lambda x: next((c["name"] for c in constructors if c["constructor_id"] == x), x),
            key=key
        )
    elif param_type == "season":
        seasons = get_seasons_list()
        return st.selectbox(label, options=[s["season"] for s in seasons], key=key)
    elif param_type == "number":
        return st.number_input(
            label,
            min_value=param_config.get("min", 1),
            max_value=param_config.get("max", 100),
            value=param_config.get("default", 10),
            key=key
        )
    elif param_type == "select":
        return st.selectbox(label, options=param_config["options"], key=key)
    return None


def validate_params(params: dict, query_info: dict) -> str | None:
    param_configs = query_info.get("params", {})
    
    driver_values = [v for k, v in params.items() if param_configs.get(k, {}).get("type") == "driver"]
    if len(driver_values) == 2 and driver_values[0] == driver_values[1]:
        return "Los dos pilotos deben ser diferentes."
    
    season_values = [v for k, v in params.items() if param_configs.get(k, {}).get("type") == "season"]
    if len(season_values) == 2 and season_values[0] == season_values[1]:
        return "Las dos temporadas deben ser diferentes."
    
    return None


def main():
    st.markdown('<p class="main-header">F1 Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Análisis de datos de la Fórmula 1 con Neo4j</p>', unsafe_allow_html=True)
    
    st.sidebar.title("Navegación")
    st.sidebar.markdown("---")
    
    category_names = list(QUERY_CATEGORIES.keys())
    selected_category = st.sidebar.selectbox(
        "Categoría",
        category_names,
        format_func=lambda x: QUERY_CATEGORIES[x]["title"]
    )
    
    category = QUERY_CATEGORIES[selected_category]
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{category['title']}**")
    st.sidebar.markdown(category["description"])
    
    st.markdown(f"## {category['title']}")
    st.markdown("---")
    
    query_names = list(category["queries"].keys())
    tabs = st.tabs([category["queries"][q]["name"] for q in query_names])
    
    for tab, query_key in zip(tabs, query_names):
        with tab:
            query_info = category["queries"][query_key]
            st.markdown(f"### {query_info['name']}")
            st.markdown(query_info.get("description", ""))
            
            params = {}
            if query_info.get("params"):
                st.markdown("#### Parámetros")
                cols = st.columns(len(query_info["params"]))
                for i, (param_name, param_config) in enumerate(query_info["params"].items()):
                    with cols[i]:
                        params[param_name] = render_param_input(param_name, param_config, query_key)
            
            if st.button("Ejecutar", key=f"exec_{query_key}"):
                error = validate_params(params, query_info)
                if error:
                    st.error(error)
                    continue
                
                with st.spinner("Ejecutando..."):
                    results = execute_query(query_info["query"], params)
                
                st.markdown("#### Resultados")
                render_results(results, query_info.get("display"))
                
                if results and query_info.get("insight"):
                    st.info(f"**Insight:** {query_info['insight']}")
            
            with st.expander("Ver query Cypher"):
                st.code(query_info["query"], language="cypher")


if __name__ == "__main__":
    main()