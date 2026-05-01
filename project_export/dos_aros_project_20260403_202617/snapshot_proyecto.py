import os

# --- CONFIGURACIÓN ---
OUTPUT_FILE = "contexto_proyecto.txt"
IGNORE_DIRS = {'.git', '__pycache__', 'venv', '.venv', 'node_modules', '.pytest_cache'}
IGNORE_EXTENSIONS = {'.pyc', '.pyo', '.db', '.png', '.jpg', '.jpeg', '.gif', '.zip', '.tar', '.gz'}

def generate_snapshot():
    root_dir = os.getcwd()
    content_output = []
    tree_output = ["### ESTRUCTURA DEL PROYECTO ###\n"]

    # Diccionario para controlar el listado único de logs por carpeta
    logs_per_folder = {}

    # 1. CONSTRUCCIÓN DEL ÁRBOL
    for root, dirs, files in os.walk(root_dir):
        # Filtrar directorios pesados in-place
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * level
        folder_name = os.path.basename(root) or "."
        tree_output.append(f"{indent}📂 {folder_name}/")
        
        sub_indent = ' ' * 4 * (level + 1)
        
        # Lógica para logs: solo el primero por carpeta
        found_log_in_dir = False
        
        for f in sorted(files):
            ext = os.path.splitext(f)[1].lower()
            
            # Si es un log, solo añadimos el primero que encontremos
            if ext == '.log':
                if not found_log_in_dir:
                    tree_output.append(f"{sub_indent}📄 {f} (único log mostrado)")
                    found_log_in_dir = True
                continue
            
            # Ignorar archivos pesados o binarios en el árbol
            if ext in IGNORE_EXTENSIONS:
                tree_output.append(f"{sub_indent}📦 {f} (archivo binario/datos)")
                continue

            tree_output.append(f"{sub_indent}📄 {f}")

    # 2. LISTADO Y CONTENIDO DE ARCHIVOS .PY
    tree_output.append("\n" + "="*50 + "\n")
    tree_output.append("### CONTENIDO DE ARCHIVOS FUENTE (.PY) ###\n")

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in sorted(files):
            if f.endswith('.py') and f != os.path.basename(__file__):
                full_path = os.path.join(root, f)
                relative_path = os.path.relpath(full_path, root_dir)
                
                tree_output.append(f"\n--- PATH: {relative_path} ---")
                tree_output.append(f"--- NOMBRE: {f} ---\n")
                
                try:
                    with open(full_path, 'r', encoding='utf-8') as source_file:
                        tree_output.append(source_file.read())
                except Exception as e:
                    tree_output.append(f"Error leyendo archivo: {e}")
                
                tree_output.append("\n" + "-"*30)

    # 3. GUARDAR EN TXT
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        f_out.write("\n".join(tree_output))

    print(f"✅ Snapshot generado con éxito en: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_snapshot()