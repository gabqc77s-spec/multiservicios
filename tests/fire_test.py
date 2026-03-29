import os
import sys
import time
from src.agent import scaffold_component, run_command, self_healing_execution

def fire_test():
    print("--- INICIANDO PRUEBA DE FUEGO REAL ---")

    # 1. Scaffolding real
    name = "fire-service"
    target_dir = "packages"
    prompt = "Un script de Python que sume dos números pasados por consola, pero que tenga un error de sintaxis inicial para probar la autocuración."

    print(f"Paso 1: Scaffolding de {name}...")
    success = scaffold_component(name, target_dir, prompt)
    if not success:
        print("Fallo en scaffolding.")
        return

    file_path = os.path.join(target_dir, name, "main.py")

    # 2. Forzar un error real si la IA lo hizo bien (o si no lo hizo mal)
    print(f"Paso 2: Asegurando error en {file_path}...")
    with open(file_path, "w") as f:
        f.write("import sys\n\ndef main():\n    # Error de tipo int + str\n    print('Resultado: ' + 10)\n\nif __name__ == '__main__':\n    main()")

    # 3. Ejecución inicial (debe fallar)
    print("Paso 3: Ejecución inicial (debe fallar)...")
    cmd = f"python3 {file_path}"
    res = run_command(cmd)
    print(f"Resultado esperado (fallo): {res['returncode']}")
    if res['returncode'] == 0:
        print("La prueba falló: el comando no debería haber tenido éxito.")
        return

    # 4. Autocuración real con Gemini
    print("Paso 4: Iniciando Autocuración con IA...")
    sh_res = self_healing_execution(cmd, filepath=file_path, max_retries=2)

    if sh_res["status"] == "success":
        print("✅ AUTOCURACIÓN EXITOSA")
        print(f"Historial: {sh_res['history']}")
        print(f"Salida final: {sh_res['result']['stdout']}")

        # 5. Verificar contenido corregido
        with open(file_path, "r") as f:
            content = f.read()
            print("--- CONTENIDO CORREGIDO ---")
            print(content)
            print("---------------------------")
    else:
        print("❌ LA AUTOCURACIÓN FALLÓ")
        print(f"Error final: {sh_res['result']['stderr']}")

if __name__ == "__main__":
    # Asegurar que el directorio de paquetes existe
    os.makedirs("packages", exist_ok=True)
    fire_test()
