from src.orchestrator import ProcessManager
import os

def audit_port_detection():
    pm = ProcessManager()

    # 1. Standard python server
    assert pm.detect_ports("python3 -m http.server 8000") == [8000]

    # 2. FastAPI/Uvicorn style
    assert pm.detect_ports("uvicorn main:app --port 3000 --host 0.0.0.0") == [3000]

    # 3. Node/NPM style
    assert pm.detect_ports("npm start -- :4000") == [4000]

    # 4. Environment variable style (often at the end)
    assert pm.detect_ports("PORT=5000 node index.js") == [5000]

    # 5. Multiple ports
    res = pm.detect_ports("docker run -p 8080:80 -p 3030:30 my-app")
    assert 8080 in res
    assert 3030 in res

    print("Port detection granular audit passed!")

if __name__ == "__main__":
    audit_port_detection()
