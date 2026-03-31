import streamlit as st
import json
import os
from pathlib import Path
from scanner import scan_directory, save_graph
from brain import create_or_load_index, query_index, get_chat_engine
from agent import edit_file, ai_edit_file, run_command, scaffold_component, self_healing_execution, git_commit_changes
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
if "studio_chats" not in st.session_state:
    st.session_state.studio_chats = {} # component_name: [messages]
if "chat_engines" not in st.session_state:
    st.session_state.chat_engines = {} # component_name: ChatEngine

# Sidebar - Project Navigation
st.sidebar.title("🛠️ Monorepo Agent")
st.sidebar.subheader("Project Structure")
if st.sidebar.button("Scan Repository"):
    with st.sidebar:
        with st.spinner("Actualizando Mapa y Memoria de IA..."):
            # 1. Update visual graph
            st.session_state.graph = scan_directory()
            save_graph(st.session_state.graph)

            # 2. Force index refresh for AI Memory (RAG)
            st.session_state.index = create_or_load_index(force_refresh=True)

            # 3. Clear chat engines to pick up new context
            st.session_state.chat_engines = {}

            st.success("Mapa y Memoria IA actualizados.")

# Status check for AI
google_api_key = os.environ.get("GOOGLE_API_KEY")
if not google_api_key:
    st.sidebar.warning("⚠️ GOOGLE_API_KEY not found. AI features running in mock mode.")
else:
    st.sidebar.success("✅ Gemini AI Connected")

# Main Interface Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Graph Map", "🧠 RAG Intelligence", "🤖 Agent Action", "⚙️ Process Control", "🎨 Project Studio"])

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
                        # Ensure we show the resolved path to the user
                        resolved_path = Path(ai_target).resolve().as_posix()
                        st.success(f"Archivo editado con éxito en: {resolved_path}")
                        st.session_state.graph = scan_directory()
                        st.session_state.index = create_or_load_index(force_refresh=True)
                        st.session_state.chat_engines = {}
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
                    st.session_state.index = create_or_load_index(force_refresh=True)
                    st.session_state.chat_engines = {}
                else:
                    st.error(f"Error al actualizar {target_file}")

    with col2:
        st.subheader("Ejecutar Comando de Consola")
        command = st.text_input("Comando:", key="run_cmd", placeholder="pytest tests/test_scanner.py")

        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            if st.button("Ejecutar Normal", key="exec_btn", use_container_width=True):
                with st.spinner("Ejecutando..."):
                    result = run_command(command)
                    st.code(f"Código de salida: {result['returncode']}")
                    if result["stdout"]:
                        st.text_area("STDOUT:", result["stdout"], height=200, key="stdout_out")
                    if result["stderr"]:
                        st.error("STDERR:")
                        st.text(result["stderr"])

        with col_ex2:
            sh_target = st.text_input("Archivo a curar (opcional):", key="sh_target", placeholder="src/main.py")
            if st.button("🪄 Ejecutar con Autocuración", key="sh_btn", use_container_width=True):
                if command:
                    with st.spinner("Ejecutando con autocuración de IA..."):
                        sh_res = self_healing_execution(command, filepath=sh_target)
                        if sh_res["status"] == "success":
                            st.success("✅ Comando exitoso tras curación.")
                        else:
                            st.error(f"❌ Falló tras {len(sh_res['history'])} reintentos.")

                        st.code(f"Resultado final: {sh_res['result']['returncode']}")
                        if sh_res["history"]:
                            with st.expander("Ver historial de curación"):
                                for h in sh_res["history"]:
                                    st.write(h)

                        if sh_res["result"]["stdout"]:
                            st.text_area("STDOUT:", sh_res["result"]["stdout"], height=200, key="sh_stdout")
                else:
                    st.warning("Ingresa un comando.")

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
                        st.session_state.index = create_or_load_index(force_refresh=True)
                        st.session_state.chat_engines = {}
                        # Initialize Studio Chat for this new component
                        intro_prompt = "Explica brevemente qué archivos creaste y qué hace cada uno. También indica cómo se debe inicializar y qué dependencias tiene."
                        intro_res = query_index(st.session_state.index, f"En el nuevo componente {sc_name}: {intro_prompt}")
                        st.session_state.studio_chats[sc_name] = [
                            {"role": "assistant", "content": f"¡He terminado de crear **{sc_name}**! Aquí tienes un resumen de lo que hice:\n\n{intro_res}"}
                        ]
                    else:
                        st.error("Error al crear el componente. Revisa el nombre o la API Key.")
            else:
                st.warning("Por favor completa todos los campos.")

    with col_sc2:
        if st.button("💾 Auto-Commit Cambios", key="git_commit_btn", use_container_width=True):
            with st.spinner("Generando mensaje de commit con IA..."):
                res = git_commit_changes()
                if res["status"] == "success":
                    st.success(f"Commit realizado: {res['message']}")
                else:
                    st.info(res["message"])

        st.write("")
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
    col_s1, col_s2, col_s3 = st.columns([3, 3, 1])
    with col_s1:
        s_name = st.text_input("Nombre del Servicio:", key="srv_name", placeholder="backend-api")
    with col_s2:
        s_cmd = st.text_input("Comando de Inicio:", key="srv_cmd", placeholder="python -m http.server 8000")
    with col_s3:
        st.write("")
        st.write("")
        if st.button("🚀 Iniciar", key="srv_start", use_container_width=True):
            if s_name and s_cmd:
                if st.session_state.manager.start_service(s_name, s_cmd):
                    st.success(f"{s_name} OK")
                else:
                    st.error("Error")

    st.subheader("Servicios en Ejecución")
    col_start1, col_start2, col_stop = st.columns([4, 1, 1])
    with col_start2:
        if st.button("🚀 Levantar Sistema", key="start_all_btn", use_container_width=True):
            # Define services to start (usually those that are configured in packages)
            packages_dir = "packages"
            if os.path.exists(packages_dir):
                for comp in os.listdir(packages_dir):
                    comp_path = os.path.join(packages_dir, comp)
                    if os.path.isdir(comp_path):
                        main_py = next((f for f in os.listdir(comp_path) if f.endswith("main.py") or f.endswith("app.py")), None)
                        if main_py:
                            cmd = f"python3 {os.path.join(comp_path, main_py)}"
                            st.session_state.manager.start_service(comp, cmd)
            st.rerun()

    with col_stop:
        if st.button("🛑 Detener TODO", key="stop_all", use_container_width=True):
            st.session_state.manager.stop_all()
            st.rerun()

    status = st.session_state.manager.get_status()
    if status:
        for name, state in status.items():
            with st.container(border=True):
                col_a, col_b, col_c = st.columns([3, 2, 1])
                col_a.write(f"**{name}**")
                col_a.caption(f"Status: {state}")

                # Dynamic Port Check
                cmd = st.session_state.manager.processes[name]["command"]
                ports = st.session_state.manager.detect_ports(cmd)
                if ports:
                    p_status = []
                    for p in ports:
                        is_up = st.session_state.manager.check_port(p)
                        icon = "✅" if is_up else "⏳"
                        p_status.append(f"{icon} {p}")
                    col_b.write(f"Puertos: {', '.join(p_status)}")

                if col_c.button(f"🛑 Detener", key=f"stop_{name}", use_container_width=True):
                    st.session_state.manager.stop_service(name)
                    st.rerun()

                # Logs
                with st.expander(f"Ver Logs de {name}"):
                    logs = st.session_state.manager.get_logs(name)
                    st.code(logs)
    else:
        st.info("No hay servicios en ejecución.")

# TAB 5: Project Studio (The iterative workbench)
with tab5:
    st.header("🎨 Project Studio: Desarrollo Persistente")
    st.info("Aquí puedes trabajar en un componente específico de forma continua: preguntar, instalar, correr y mejorar.")

    # 1. Component Selection
    packages_dir = "packages"
    if not os.path.exists(packages_dir):
        os.makedirs(packages_dir)

    available_components = [d for d in os.listdir(packages_dir) if os.path.isdir(os.path.join(packages_dir, d))]

    if available_components:
        selected_comp = st.selectbox("Selecciona un componente para trabajar:", available_components)
        comp_path = os.path.join(packages_dir, selected_comp)

        # Pre-calculate component files to avoid NameErrors in all scopes
        comp_files = []
        for root, dirs, files in os.walk(comp_path):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), comp_path)
                comp_files.append(rel)

        col_st1, col_st2 = st.columns([2, 1])

        with col_st1:
            st.subheader(f"💬 Studio Chat: {selected_comp}")

            # Initialize history if not exists
            if selected_comp not in st.session_state.studio_chats:
                st.session_state.studio_chats[selected_comp] = [
                    {"role": "assistant", "content": f"Hola. Estoy listo para ayudarte con el componente **{selected_comp}**. ¿Qué quieres hacer hoy?"}
                ]

            # Display Chat History
            chat_container = st.container(height=400)
            with chat_container:
                for msg in st.session_state.studio_chats[selected_comp]:
                    st.chat_message(msg["role"]).write(msg["content"])

            # Chat Input
            if prompt := st.chat_input(f"Pregunta o pide un cambio para {selected_comp}..."):
                # Initialize ChatEngine if not exists for this component
                if selected_comp not in st.session_state.chat_engines:
                    history = st.session_state.studio_chats.get(selected_comp, [])
                    st.session_state.chat_engines[selected_comp] = get_chat_engine(st.session_state.index, chat_history_dicts=history)

                # User message
                st.session_state.studio_chats[selected_comp].append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)

                # Assistant Response
                with st.spinner("Gemini está pensando..."):
                    # Use the REAL chat engine with memory
                    chat_engine = st.session_state.chat_engines[selected_comp]

                    # Check if it's an edit instruction
                    if any(word in prompt.lower() for word in ["cambia", "edita", "agrega", "modifica", "mejora", "corrige"]):
                        # Use Gemini to find the most relevant file to edit
                        file_finder_prompt = f"Basado en esta instrucción: '{prompt}', ¿cuál de estos archivos debería editar? RESPONDE SOLO CON LA RUTA DEL ARCHIVO: {comp_files}"
                        target_file_guess = query_index(st.session_state.index, file_finder_prompt).strip()

                        # Normalize target_file_guess to handle different slashes
                        norm_guess = target_file_guess.replace("\\", "/")
                        norm_comp_files = [f.replace("\\", "/") for f in comp_files]

                        if norm_guess in norm_comp_files:
                            # Construct path safely using pathlib
                            full_path = (Path(comp_path) / norm_guess).resolve()
                            if ai_edit_file(str(full_path), prompt):
                                response = f"✅ He aplicado los cambios en: `{full_path.as_posix()}`"
                                st.session_state.index = create_or_load_index(force_refresh=True)
                                # Re-initialize chat engine to pick up new file content
                                st.session_state.chat_engines[selected_comp] = get_chat_engine(
                                    st.session_state.index,
                                    chat_history_dicts=st.session_state.studio_chats[selected_comp]
                                )
                            else:
                                response = f"❌ Tuve un problema al intentar editar el archivo en `{full_path.as_posix()}`."
                        else:
                            # Use chat engine for response
                            chat_res = chat_engine.chat(prompt)
                            response = str(chat_res)
                    else:
                        # Use chat engine for response
                        chat_res = chat_engine.chat(prompt)
                        response = str(chat_res)

                st.session_state.studio_chats[selected_comp].append({"role": "assistant", "content": response})
                st.rerun()

        with col_st2:
            st.subheader("⚙️ Control Directo")

            # Check for requirements.txt
            req_exists = os.path.exists(os.path.join(comp_path, "requirements.txt"))
            if req_exists:
                if st.button("📦 Instalar Dependencias", key="studio_install", use_container_width=True):
                    with st.spinner("Instalando..."):
                        res = run_command(f"pip install -r {os.path.join(comp_path, 'requirements.txt')}")
                        if res["returncode"] == 0: st.success("Instalado.")
                        else: st.error("Error.")

            # Start/Stop Logic
            main_py = next((f for f in comp_files if f.endswith("main.py") or f.endswith("app.py")), None)
            if main_py:
                start_cmd = f"python {os.path.join(comp_path, main_py)}"
                if st.button("🚀 Iniciar Servicio", key="studio_start", use_container_width=True):
                    if st.session_state.manager.start_service(selected_comp, start_cmd):
                        st.success(f"{selected_comp} iniciado.")

                if st.button("🛑 Detener Servicio", key="studio_stop", use_container_width=True):
                    if st.session_state.manager.stop_service(selected_comp):
                        st.info(f"{selected_comp} detenido.")

                st.divider()
                if st.button("🪄 Correr y Autocurar", key="studio_sh", use_container_width=True):
                    with st.spinner(f"Ejecutando {selected_comp} con autocuración..."):
                        sh_res = self_healing_execution(start_cmd, filepath=os.path.join(comp_path, main_py))
                        if sh_res["status"] == "success":
                            st.success("✅ Funciona correctamente.")
                        else:
                            st.error("❌ No se pudo curar automáticamente.")
                        with st.expander("Detalles"):
                            st.code(sh_res["result"]["stdout"] or sh_res["result"]["stderr"])

            st.divider()
            st.subheader("📝 Guía del Componente")
            readme_path = os.path.join(comp_path, "README.md")
            if os.path.exists(readme_path):
                with open(readme_path, "r") as f:
                    st.markdown(f.read())
            else:
                st.write("No hay README.md.")

    else:
        st.warning("No se encontraron componentes en 'packages/'. Crea uno primero en la pestaña 'Agent Action'.")
