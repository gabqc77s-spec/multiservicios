import streamlit as st
import json
import os
from scanner import scan_directory, save_graph
from brain import create_or_load_index, query_index
from agent import edit_file, run_command
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

# Main Interface Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Graph Map", "🧠 RAG Intelligence", "🤖 Agent Action", "⚙️ Process Control"])

# TAB 1: Graph Visualization
with tab1:
    st.header("Project Gene Map")

    # Create pyvis network - using CDN for resources to avoid local path issues in iframe
    net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white')

    for node in st.session_state.graph["nodes"]:
        color = "#ff4b4b" if node["type"] == "directory" else "#4bafff"
        net.add_node(node["id"], label=node["id"], color=color)

    for edge in st.session_state.graph["edges"]:
        net.add_edge(edge["from"], edge["to"])

    # Generate HTML string with CDN resources
    html_content = net.generate_html()

    # Replace local paths with CDNs if pyvis didn't do it (it usually does by default or has options)
    # For extra safety, we ensure it's a standalone HTML
    components.html(html_content, height=550, scrolling=True)

# TAB 2: Semantic Search (RAG)
with tab2:
    st.header("Contextual Intelligence (RAG)")
    st.info("Note: Full RAG requires a valid OPENAI_API_KEY environment variable.")
    query = st.text_input("Ask about the codebase:", placeholder="Where is the file editing logic?")
    if st.button("Query"):
        if query:
            with st.spinner("Searching..."):
                response = query_index(st.session_state.index, query)
                st.write(f"**Answer:** {response}")
        else:
            st.warning("Please enter a query.")

# TAB 3: Agentic Execution
with tab3:
    st.header("Atomic Actions Agent")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Edit File")
        target_file = st.text_input("File path:", placeholder="src/example.py")
        new_content = st.text_area("New content:")
        if st.button("Apply Edit"):
            if target_file and new_content:
                if edit_file(target_file, new_content):
                    st.success(f"Updated {target_file}")
                else:
                    st.error(f"Failed to update {target_file}")

    with col2:
        st.subheader("Run Console Command")
        command = st.text_input("Command:", placeholder="pytest tests/test_scanner.py")
        if st.button("Execute"):
            with st.spinner("Running..."):
                result = run_command(command)
                st.code(f"Exit code: {result['returncode']}")
                if result["stdout"]:
                    st.text_area("STDOUT:", result["stdout"], height=200)
                if result["stderr"]:
                    st.error("STDERR:")
                    st.text(result["stderr"])

# TAB 4: Process Management
with tab4:
    st.header("Local Process Orchestrator")

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        s_name = st.text_input("Service Name:", placeholder="backend-api")
        s_cmd = st.text_input("Launch Command:", placeholder="python -m http.server 8000")
    with col_s2:
        st.write("")
        st.write("")
        if st.button("🚀 Start Service"):
            if s_name and s_cmd:
                if st.session_state.manager.start_service(s_name, s_cmd):
                    st.success(f"{s_name} started.")
                else:
                    st.error("Failed to start service.")

    st.subheader("Running Services")
    status = st.session_state.manager.get_status()
    if status:
        for name, state in status.items():
            col_a, col_b = st.columns([4, 1])
            col_a.write(f"**{name}**: {state}")
            if col_b.button(f"Stop {name}", key=name):
                st.session_state.manager.stop_service(name)
                st.rerun()
    else:
        st.info("No services running.")
