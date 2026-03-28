import streamlit as st
import json
import os
from scanner import scan_directory, save_graph
from brain import create_or_load_index, query_index
from agent import edit_file, ai_edit_file, run_command, scaffold_component
from orchestrator import ProcessManager
from pyvis.network import Network
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(page_title="Monorepo Manager Agent", layout="wide")

# Persistent State Management
if "manager" not in st.session_state:
    st.session_state.manager = ProcessManager()
if "graph" not in st.session_state:
    st.session_state.graph = scan_directory()
if "index" not in st.session_state:
    st.session_state.index = create_or_load_index()

# Sidebar - Project Navigation
st.sidebar.title("🛠️ Monorepo Agent")
st.sidebar.subheader("Project Structure")
if st.sidebar.button("Scan Repository"):
    st.session_state.graph = scan_directory()
    save_graph(st.session_state.graph)
    st.sidebar.success("Repo Rescanned")

# Status check for AI
google_api_key = os.environ.get("GOOGLE_API_KEY")
if not google_api_key:
    st.sidebar.warning("⚠️ GOOGLE_API_KEY not found. AI features running in mock mode.")
else:
    st.sidebar.success("✅ Gemini AI Connected")

# Main Interface Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Graph Map", "🧠 RAG Intelligence", "🤖 Agent Action", "⚙️ Process Control"])

# TAB 1: Graph Visualization
with tab1:
    st.header("Project Gene Map")

    if st.session_state.graph.get("nodes"):
        try:
            # Create network
            net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white', notebook=False)

            for node in st.session_state.graph["nodes"]:
                color = "#ff4b4b" if node["type"] == "directory" else "#4bafff"
                net.add_node(node["id"], label=node["id"], color=color, shape="dot", size=15)

            for edge in st.session_state.graph["edges"]:
                net.add_edge(edge["from"], edge["to"])

            net.toggle_physics(True)
            # Desactivar improvedLayout para evitar advertencias en la consola y mejorar rendimiento
            net.set_options('{"layout": {"improvedLayout": false}}')

            # Generate HTML with CDN links
            # We explicitly replace any local script paths if they exist, though pyvis usually uses CDN
            html_content = net.generate_html()

            # Inject a small script to ensure vis-network is loaded from CDN if missing
            if 'https://unpkg.com/vis-network' not in html_content:
                html_content = html_content.replace(
                    '<head>',
                    '<head><script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>'
                )

            components.html(html_content, height=600, scrolling=True)
            st.info("💡 Puedes interactuar con el mapa (arrastrar y hacer zoom).")
        except Exception as e:
            st.error(f"Error al generar el mapa: {e}")
    else:
        st.warning("No se encontró estructura del proyecto. Usa 'Scan Repository'.")

# TAB 2: Semantic Search (RAG)
with tab2:
    st.header("Contextual Intelligence (RAG)")
    st.info("💡 **Uso:** Haz preguntas abiertas sobre cualquier parte del proyecto. Gemini buscará automáticamente en todos tus archivos sin que tengas que especificar rutas.")
    if not google_api_key:
        st.warning("Conecta Gemini para habilitar el razonamiento avanzado sobre el código.")
    query = st.text_input("Pregunta sobre el código:", key="rag_query", placeholder="Ej: ¿Cómo funciona el orquestador? o ¿Dónde se definen las rutas del API?")
    if st.button("Consultar", key="rag_btn"):
        if query:
            with st.spinner("Gemini está pensando..."):
                response = query_index(st.session_state.index, query)
                st.markdown(f"**Respuesta:**\n{response}")
        else:
            st.warning("Por favor ingresa una consulta.")

# TAB 3: Agentic Execution
with tab3:
    st.header("Atomic Actions Agent")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Editar Archivo con IA (Gemini)")
        st.caption("💡 **Uso:** Indica el archivo específico que deseas mejorar y dale una instrucción clara.")
        ai_target = st.text_input("Ruta del archivo a editar:", key="ai_edit_path", placeholder="packages/mi-servicio/main.py")
        ai_instruction = st.text_area("Instrucción para la IA:", key="ai_instruction", placeholder="Agrega un endpoint de suma que acepte a y b.")
        if st.button("🪄 Editar con IA"):
            if ai_target and ai_instruction:
                with st.spinner(f"Gemini está editando {ai_target}..."):
                    if ai_edit_file(ai_target, ai_instruction):
                        st.success(f"Archivo {ai_target} editado con éxito.")
                        st.session_state.graph = scan_directory()
                    else:
                        st.error(f"Error al editar {ai_target}.")
            else:
                st.warning("Completa la ruta y la instrucción.")

        st.divider()
        st.subheader("Edición Manual")
        target_file = st.text_input("Ruta (Manual):", key="edit_path", placeholder="src/example.py")
        new_content = st.text_area("Nuevo contenido:", key="edit_content", height=200)
        if st.button("Aplicar Edición Manual"):
            if target_file and new_content:
                if edit_file(target_file, new_content):
                    st.success(f"Actualizado {target_file}")
                    st.session_state.graph = scan_directory()
                else:
                    st.error(f"Error al actualizar {target_file}")

    with col2:
        st.subheader("Ejecutar Comando de Consola")
        command = st.text_input("Comando:", key="run_cmd", placeholder="pytest tests/test_scanner.py")
        if st.button("Ejecutar", key="exec_btn"):
            with st.spinner("Ejecutando..."):
                result = run_command(command)
                st.code(f"Código de salida: {result['returncode']}")
                if result["stdout"]:
                    st.text_area("STDOUT:", result["stdout"], height=200, key="stdout_out")
                if result["stderr"]:
                    st.error("STDERR:")
                    st.text(result["stderr"])

    st.divider()
    st.subheader("🚀 Crear Componente con IA (Scaffolding)")
    sc_name = st.text_input("Nombre del Componente:", key="sc_name", placeholder="mi-nuevo-servicio")
    sc_dir = st.text_input("Directorio Destino:", key="sc_dir", value="packages")
    sc_desc = st.text_area("Descripción (Prompt para IA):", key="sc_desc", placeholder="Un backend Python FastAPI con un endpoint básico.")

    col_sc1, col_sc2 = st.columns(2)
    with col_sc1:
        if st.button("🚀 Crear Componente", key="sc_btn", use_container_width=True):
            if sc_name and sc_dir and sc_desc:
                with st.spinner(f"Gemini está generando {sc_name}..."):
                    if scaffold_component(sc_name, sc_dir, sc_desc):
                        st.success(f"Componente {sc_name} creado con éxito en {sc_dir}/")
                        st.session_state.graph = scan_directory()
                    else:
                        st.error("Error al crear el componente. Revisa el nombre o la API Key.")
            else:
                st.warning("Por favor completa todos los campos.")

    with col_sc2:
        if st.button("📦 Instalar Dependencias", key="install_deps_btn", use_container_width=True):
            if sc_name and sc_dir:
                target_path = os.path.join(sc_dir, sc_name)
                req_path = os.path.join(target_path, "requirements.txt")
                if os.path.exists(req_path):
                    with st.spinner(f"Instalando dependencias en {target_path}..."):
                        res = run_command(f"pip install -r {req_path}")
                        if res["returncode"] == 0:
                            st.success("Dependencias instaladas correctamente.")
                        else:
                            st.error(f"Error en la instalación: {res['stderr']}")
                else:
                    # Intentar buscar en subcarpetas (a veces el scaffolding crea una subcarpeta con el mismo nombre)
                    deep_req = next(Path(target_path).glob("**/requirements.txt"), None)
                    if deep_req:
                        with st.spinner(f"Instalando dependencias desde {deep_req}..."):
                            res = run_command(f"pip install -r {deep_req}")
                            if res["returncode"] == 0:
                                st.success(f"Dependencias instaladas desde {deep_req}")
                            else:
                                st.error(f"Error: {res['stderr']}")
                    else:
                        st.error(f"No se encontró requirements.txt en {target_path}")
            else:
                st.warning("Indica el nombre y directorio del componente.")

# TAB 4: Process Management
with tab4:
    st.header("Local Process Orchestrator")
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        s_name = st.text_input("Nombre del Servicio:", key="srv_name", placeholder="backend-api")
        s_cmd = st.text_input("Comando de Inicio:", key="srv_cmd", placeholder="python -m http.server 8000")
    with col_s2:
        st.write("")
        st.write("")
        if st.button("🚀 Iniciar Servicio", key="srv_start"):
            if s_name and s_cmd:
                if st.session_state.manager.start_service(s_name, s_cmd):
                    st.success(f"Servicio {s_name} iniciado.")
                else:
                    st.error("Error al iniciar el servicio.")

    st.subheader("Servicios en Ejecución")
    status = st.session_state.manager.get_status()
    if status:
        for name, state in status.items():
            col_a, col_b = st.columns([4, 1])
            col_a.write(f"**{name}**: {state}")
            if col_b.button(f"Detener {name}", key=f"stop_{name}"):
                st.session_state.manager.stop_service(name)
                st.rerun()
    else:
        st.info("No hay servicios en ejecución.")
