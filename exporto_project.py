import os
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path.cwd()
EXPORT_DIR = PROJECT_ROOT / 'project_export'
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
EXPORT_NAME = f'dos_aros_project_{TIMESTAMP}'

# Crear directorio
export_path = EXPORT_DIR / EXPORT_NAME
export_path.mkdir(parents=True, exist_ok=True)

# Archivos/carpetas a incluir
PATTERNS = {
    'Scripts Python': ['*.py'],
    'Documentación': ['*.md', 'docs/*'],
    'Configuración': ['.env', '.env.example', '.gitignore', 'requirements.txt'],
    'Assets - Avatares': ['assets/avatars/avatars_base/*.png', 'assets/avatars/logos_base/*.png'],
    'Assets - Datos': ['assets/data/*.csv'],
    'GitHub': ['.github/workflows/*.yml', '.github/copilot-instructions.md'],
}

def copy_files(pattern, dest_subdir=None):
    """Copia archivos según pattern"""
    for file_pattern in (pattern if isinstance(pattern, list) else [pattern]):
        files = list(PROJECT_ROOT.glob(file_pattern))
        for file in files:
            if file.is_file():
                if dest_subdir:
                    target_dir = export_path / dest_subdir
                else:
                    target_dir = export_path / file.parent.relative_to(PROJECT_ROOT)
                
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, target_dir / file.name)
                print(f"✅ {file.name}")

print(f"📦 Exportando proyecto a: {EXPORT_NAME}\n")

for category, patterns in PATTERNS.items():
    print(f"\n📁 {category}:")
    for pattern in patterns:
        copy_files(pattern)

# Crear INDEX
index = f"""# DOS AROS PROJECT - SNAPSHOT
**Exportado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 Estructura
```
{EXPORT_NAME}/
├── Scripts Python (.py)
│   ├── master_sync.py
│   ├── avatar_prompt_generator.py
│   ├── image_generator.py
│   ├── telegram_avatar_handler.py
│   └── ...otros scripts
│
├── Documentación (.md)
│   ├── README.md
│   ├── AVATAR_SYSTEM_DOCS.md
│   ├── AVATAR_BIBLE.md
│   └── ...guías
│
├── Configuración
│   ├── .env (SENSITIVO - actualizar tokens)
│   ├── .env.example
│   ├── .gitignore
│   └── requirements.txt
│
├── Assets
│   ├── avatars_base/ (4 variantes PNG)
│   ├── logos_base/ (2 logos PNG)
│   └── data/ (CSV con colores de equipos)
│
└── GitHub
    ├── workflows/ (CI/CD)
    └── copilot-instructions.md
```

## 🔑 Archivos Sensibles
- `.env` - Contiene tokens de API (ROTAR antes de usar)
- `credentials.json` - NO incluido por seguridad

## 🚀 Estado del Proyecto
- ✅ BBDD: 67 equipos + 60 colores + 68 prompts
- ✅ Assets: 4 avatares + 2 logos en GitHub
- ✅ Sistema: Prompts dinámicos generados
- ⏳ Telegram: Script listo para integrar
- ⏳ Imágenes: Manual con Google ImageFX

## 📖 Documentos Clave
1. **AVATAR_SYSTEM_DOCS.md** - Documentación completa
2. **AVATAR_BIBLE.md** - Especificaciones avatar
3. **.env** - Configuración (actualizar tokens)
"""

with open(export_path / 'INDEX.md', 'w', encoding='utf-8') as f:
    f.write(index)

print(f"\n✅ {EXPORT_NAME} creado exitosamente")
print(f"📦 ZIP creado: {EXPORT_NAME}.zip")

# Crear ZIP (opcional)
shutil.make_archive(export_path, 'zip', EXPORT_DIR, EXPORT_NAME)
print(f"\n📦 ZIP creado: {EXPORT_NAME}.zip")