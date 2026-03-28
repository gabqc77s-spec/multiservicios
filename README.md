Guía Maestra: Sistema de Gestión de Monorepo Autónomo (Local Nativo)
1. Capa de Ingesta y "Reflejo" (El Mapa Genético)
Qué es: Escáner de disco que mapea tu arquitectura.
Detalle Técnico: Igual que el anterior, pero con un enfoque en rutas absolutas del sistema operativo. Utiliza pathlib para encontrar archivos de entorno (.env, venv, node_modules).
Funcionamiento: Crea el graph.json. Es vital porque le dice a la IA dónde están tus ejecutables locales (ej: C:\Python310\python.exe o /usr/bin/node).
2. Capa de Inteligencia Contextual (RAG de Código)
Qué es: Índice semántico local.
Detalle Técnico: LlamaIndex crea un índice vectorial persistente en una carpeta local (ej: .brain/).
Funcionamiento: Permite que la IA busque fragmentos de código sin leer todo el disco cada vez. La búsqueda es instantánea y privada.
3. El Agente de Ejecución Atómica (La "Mano" de la IA)
Qué es: El script que edita archivos y ejecuta comandos de consola.
Detalle Técnico: Un agente de Python que usa shutil para mover archivos y os.system o subprocess para instalar dependencias (pip install, npm install) en tus carpetas reales.
Funcionamiento: Si pides un cambio, la IA escribe directamente en tus archivos. Importante: Aquí el Agente debe hacer un git stash o un commit preventivo antes de actuar para evitar desastres.
4. Interfaz de Comando Visual (Streamlit Frontend)
Qué es: Tu panel de control localhost:8501.
Detalle Técnico: Gráficos con st-pyvis. Incluye un panel de "Procesos Activos" donde verás qué servicios están corriendo en tu RAM en ese momento.
Funcionamiento: Centraliza la comunicación. Desde aquí lanzas las órdenes y ves cómo la IA "navega" por tus carpetas.
5. Sistema de Autosanación (CI/CD Nativo)
Qué es: Validación mediante tus propias herramientas de consola.
Detalle Técnico: El programa ejecuta pytest, eslint o go test directamente en la terminal oculta.
Funcionamiento: Si el comando devuelve un código de error (exit code != 0), la IA captura la salida de la consola, entiende el error de compilación y re-edita el código hasta que el comando de consola pase en limpio.
6. Orquestador de Procesos (Sustituto de Docker)
Qué es: Gestión de ejecución de servicios en tiempo real.
Detalle Técnico: En lugar de docker-compose, usamos Gestión de Procesos en Segundo Plano (subprocess.Popen).
Funcionamiento: El botón "Play" en Streamlit lanza los microservicios como procesos independientes en tu PC. El programa monitorea los puertos (ej: 8080, 3000) y te avisa cuando están listos. Para "limpiar", el programa mata los procesos (PID terminate) al cerrar la app.
🚀 El Flujo "End-to-End" Local Puro
Inicio: Abres Streamlit. El programa detecta tus entornos virtuales instalados y te muestra el grafo.
Orden: "Agrega un campo 'teléfono' al perfil de usuario en el backend y frontend".
Acción:
La IA localiza los archivos vía RAG.
El Agente edita los archivos físicos.
El Sistema de Autosanación lanza un npm run lint y un pytest. Si hay error, lo corrige en segundos.
Prueba (Sin Docker): Pulsas "Levantar Sistema". Streamlit ejecuta los comandos de inicio en ventanas de consola invisibles.
Validación: Abres tu navegador en localhost:3000 y ves el cambio aplicado.
Cierre: Pulsas "Detener" en Streamlit (limpia procesos de memoria) y la IA hace el git commit.
