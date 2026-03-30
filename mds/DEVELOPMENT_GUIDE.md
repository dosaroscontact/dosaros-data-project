# 🛠️ Development Guide - Dos Aros para Claude Code

**Cómo trabajar en el proyecto de forma segura y eficiente.**

---

## 📋 ANTES DE EMPEZAR

### Checklist Pre-Cambio
- [ ] ¿Es cambio en Windows (código) o Pi (ejecución)?
- [ ] ¿Necesito acceso a BBDD? (si sí, especificar queries)
- [ ] ¿Afecta al bot en vivo? (si sí, coordinar reinicio)
- [ ] ¿Cambio requiere dependencias nuevas? (revisar requirements.txt)
- [ ] ¿Hay que actualizar .env?
- [ ] ¿Hay que actualizar documentación?

---

## 🔄 FLUJO DE DESARROLLO ESTÁNDAR

### **PASO 1: Crear/Editar Archivo (Windows)**

```
Archivo a crear/editar:
  C:\Users\rover\dosaros-data-project\nuevo_archivo.py

Estructura básica:
"""
================================================================================
Descripción de qué hace el archivo
================================================================================
"""

import necessary_modules

def function_name():
    """Docstring de la función"""
    pass

if __name__ == "__main__":
    print("Descripción de ejecución")
```

### **PASO 2: Testing Local (Windows)**

```bash
# Activar venv (si existe en Windows)
venv\Scripts\activate

# Instalar si falta algo
pip install -r requirements.txt

# Test el archivo
python nuevo_archivo.py

# Si tiene errores, revisar:
# - Imports faltantes
# - Rutas incorrectas (usar /home/pi/... si es para Pi)
# - Variables de entorno (.env)
```

### **PASO 3: Commit a GitHub**

```bash
git status
git add nuevo_archivo.py

# Mensaje de commit claro
git commit -m "Add: descripción de lo que hace" 

# O si es fix:
git commit -m "Fix: descripción del problema resuelto"

# O si es cambio:
git commit -m "Update: descripción del cambio"

git push origin main
```

### **PASO 4: Sync en Pi**

```bash
# En Pi
cd /home/pi/dosaros-data-project
git pull origin main

# Verificar que llegó
git log --oneline -3
ls -la nuevo_archivo.py
```

### **PASO 5: Testing en Pi (si es necesario)**

```bash
cd /home/pi/dosaros-data-project
source venv/bin/activate

# Test
PYTHONPATH=/home/pi/dosaros-data-project python nuevo_archivo.py

# Si cambió bot_consultas.py, reiniciar:
tmux kill-session -t bot_consultas
tmux new-session -d -s bot_consultas "cd /home/pi/dosaros-data-project && source venv/bin/activate && PYTHONPATH=/home/pi/dosaros-data-project python src/automation/bot_consultas.py"

# Verificar
ps aux | grep bot_consultas.py | grep -v grep
```

### **PASO 6: Validar en Producción**

```bash
# En Telegram, probar los comandos afectados
/avatar_random
/avatar_today
/avatar_prompt Lakers

# Ver logs
tail -f /home/pi/dosaros-data-project/logs/*.log

# Confirmar éxito
echo "✅ Cambio validado en producción"
```

---

## 📝 PATRONES DE EDICIÓN COMUNES

### PATRÓN 1: Agregar función a script existente

```python
# En archivo existente, ANTES de if __name__ == "__main__":

def nueva_funcion(parametro):
    """
    Descripción de qué hace
    
    Args:
        parametro: tipo y descripción
        
    Returns:
        tipo y descripción del retorno
    """
    result = procesar(parametro)
    return result

# SIEMPRE documentar con docstrings
```

### PATRÓN 2: Editar función existente

```python
# ANTES de cambiar, crear respaldo mental:
# def funcion_original(param):
#     return algo_viejo

# NUEVO (mejorado):
def funcion_original(param):
    """Versión mejorada con razón del cambio"""
    # Cambio: razón específica del cambio
    return algo_nuevo

# Mensaje commit: "Update: función_original para [razón]"
```

### PATRÓN 3: Agregar variable de entorno

```python
# En script:
import os
from dotenv import load_dotenv

load_dotenv()

MI_NUEVA_VAR = os.getenv('MI_NUEVA_VAR', 'valor_por_defecto')

# En .env (Pi):
MI_NUEVA_VAR=valor_real

# En .env.example (para documentar):
MI_NUEVA_VAR=ejemplo_valor

# Commit el .env.example, NO el .env
git add .env.example
git commit -m "Add: MI_NUEVA_VAR to .env.example"
```

### PATRÓN 4: Cambiar query SQL

```python
# ANTES:
query = "SELECT * FROM avatar_prompts WHERE id = 1"

# DESPUÉS (mejorado):
query = """
SELECT team_name, prompt_text, avatar_url, logo_url
FROM avatar_prompts
WHERE id = ?
LIMIT 1
"""

# Usar parametrización siempre:
cursor.execute(query, (id_value,))  # ✅ SEGURO
# NO: cursor.execute(f"WHERE id = {id_value}")  # ❌ INSEGURO
```

### PATRÓN 5: Agregar test

```python
# En test file o al final de script:

def test_funcion():
    """Test para funcion()"""
    resultado = funcion(parametro_test)
    assert resultado == expected_value, f"Esperado {expected_value}, got {resultado}"
    print("✅ Test pasó")

if __name__ == "__main__":
    test_funcion()
    print("Todos los tests pasaron")
```

---

## 🚨 CAMBIOS CRÍTICOS (REQUIEREN CUIDADO EXTRA)

### Cambiar bot_consultas.py

**Riesgo:** Bot se cae, usuarios sin servicio

**Procedimiento:**
```
1. Edita archivo en Windows
2. Test LOCAL (si es posible):
   python -c "from src.automation.bot_consultas import escuchar_y_procesar"
3. Commit y push
4. Pull en Pi
5. Detén bot actual
6. Reinicia en tmux
7. ESPERA 30 segundos
8. Verifica en Telegram que responde
9. Si falla, revertir:
   git revert HEAD
   git push
   git pull (en Pi)
   Reiniciar bot
```

### Cambiar estructura BBDD

**Riesgo:** Pérdida de datos, queries que ya no funcionan

**Procedimiento:**
```
1. BACKUP obligatorio:
   cp /mnt/nba_data/dosaros_local.db /mnt/nba_data/dosaros_local.db.backup_FECHA
2. Hacer cambio en script (no directo en BBDD)
3. Probar en datos de PRUEBA primero
4. Documentar cambio en docs/CHANGELOG.md
5. Commit con descripción DETALLADA
6. Ejecutar en Pi con CUIDADO
7. Verificar integridad: PRAGMA integrity_check;
8. Guardar backup nuevo
```

### Cambiar .env

**Riesgo:** Bot pierde credenciales, no responde

**Procedimiento:**
```
1. NUNCA agregar valores reales a Windows
2. Usar .env.example para documentar ESTRUCTURA
3. En Pi, editar manualmente:
   nano /home/pi/dosaros-data-project/.env
4. NO hacer commit de .env a GitHub
5. Reiniciar bot si cambió tokens:
   tmux kill-session -t bot_consultas
   # ... reiniciar
6. Verificar que bot responde en Telegram
```

### Cambiar cron jobs

**Riesgo:** Automatización se rompe, procesos no ejecutan

**Procedimiento:**
```
1. LISTAR cron actual:
   crontab -l > cron_backup.txt
2. Editar:
   crontab -e
3. SIEMPRE incluir PYTHONPATH:
   PYTHONPATH=/home/pi/dosaros-data-project
4. SIEMPRE incluir redireccionamiento de logs:
   >> /home/pi/dosaros-data-project/logs/nombre.log 2>&1
5. Test manual ANTES de confiar en cron:
   Ejecutar el comando manualmente
6. Esperar a siguiente ejecución programada
7. Revisar logs:
   tail -20 /home/pi/dosaros-data-project/logs/nombre.log
```

---

## 🔍 CÓDIGO DE CALIDAD

### Checklist de Calidad

- [ ] Tiene docstrings todas las funciones
- [ ] Variables tienen nombres descriptivos
- [ ] No hay código comentado (DELETE, no comentar)
- [ ] Imports están al inicio
- [ ] Manejo de errores con try/except donde corresponde
- [ ] Logs cuando algo importante ocurre
- [ ] PYTHONPATH configurado si corre en Pi
- [ ] No hardcodear valores (usar .env)
- [ ] Sin print() en producción (usar logging)
- [ ] SQL parametrizado (usar ?)

### Template de función bien hecha

```python
def procesar_avatar(team_name: str) -> dict:
    """
    Procesa un avatar para un equipo específico.
    
    Args:
        team_name (str): Nombre del equipo (ej: "Los Angeles Lakers")
        
    Returns:
        dict: {
            'team': str,
            'prompt': str,
            'avatar_url': str,
            'logo_url': str
        }
        
    Raises:
        ValueError: Si el equipo no existe
        sqlite3.Error: Si hay error en BBDD
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Validar entrada
        if not team_name or not isinstance(team_name, str):
            raise ValueError(f"team_name inválido: {team_name}")
        
        logger.info(f"Procesando avatar para {team_name}")
        
        # Buscar en BBDD
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute(
            'SELECT * FROM avatar_prompts WHERE team_name = ?',
            (team_name,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise ValueError(f"Equipo no encontrado: {team_name}")
        
        logger.info(f"Avatar procesado exitosamente para {team_name}")
        
        return {
            'team': result[1],
            'prompt': result[6],
            'avatar_url': result[4],
            'logo_url': result[5]
        }
        
    except Exception as e:
        logger.error(f"Error procesando avatar: {e}")
        raise
```

---

## 🧪 TESTING

### Niveles de Test

```
NIVEL 1: Test local en Windows (rápido)
├─ Verificar imports
├─ Verificar sintaxis
└─ Test funciones simples

NIVEL 2: Test en Pi sin producción (seguro)
├─ Test con PYTHONPATH correcto
├─ Test con BBDD real
└─ Test cron job manualmente

NIVEL 3: Test en producción (cuidadoso)
├─ Verificar bot responde
├─ Verificar cron logs
└─ Revisar datos en Telegram
```

### Test Script Template

```python
# test_mi_feature.py

import unittest
import sys
sys.path.insert(0, '/home/pi/dosaros-data-project')

class TestMiFeature(unittest.TestCase):
    
    def setUp(self):
        """Preparar antes de cada test"""
        pass
    
    def test_funcion_basica(self):
        """Test caso básico"""
        resultado = mi_funcion("test")
        self.assertIsNotNone(resultado)
    
    def test_funcion_error(self):
        """Test manejo de errores"""
        with self.assertRaises(ValueError):
            mi_funcion(None)
    
    def tearDown(self):
        """Limpiar después de cada test"""
        pass

if __name__ == '__main__':
    unittest.main()
```

---

## 📚 DOCUMENTACIÓN

### Cuándo actualizar docs

- [ ] Cambio en estructura de BBDD → update AVATAR_SYSTEM_DOCS.md
- [ ] Nuevo comando en bot → update BOT_MANUAL.md
- [ ] Cambio en variables .env → update CLAUDE_CODE_CONTEXT.md
- [ ] Nuevo script → agregar a SCRIPTS_REFERENCE.md
- [ ] Breaking change → update CHANGELOG.md

### Template de cambio en CHANGELOG

```markdown
## [VERSION] - YYYY-MM-DD

### Added
- Nueva característica o funcionalidad

### Changed
- Cambio en característica existente

### Fixed
- Bug arreglado

### Removed
- Funcionalidad deprecada

### Notes
- Notas adicionales sobre el cambio
```

---

## 🚀 DESPLIEGUE A PRODUCCIÓN

### Checklist Final

- [ ] Código testeado localmente
- [ ] Commit messages claros
- [ ] GitHub actualizado (git push)
- [ ] Pi sincronizado (git pull)
- [ ] Si cambió bot: reiniciado en tmux
- [ ] Logs verificados para errores
- [ ] Funcionalidad testeada en Telegram
- [ ] Documentación actualizada
- [ ] Changelog actualizado (si es versión)

### Rollback de Emergencia

Si algo falla en producción:

```bash
# 1. Identificar problema
tail -50 logs/*.log

# 2. Revertir cambio último
git revert HEAD
git push
git pull (en Pi)

# 3. Si cambió bot, reiniciar
tmux kill-session -t bot_consultas
# ... reiniciar

# 4. Verificar restauración
ps aux | grep bot_consultas
# Probar en Telegram

# 5. Postmortem
# - Qué falló
# - Por qué no se vio en testing
# - Cómo prevenirlo
```

---

## 💬 COMUNICACIÓN CON ROBE

### Formato para reportar estado

```
Cambio: [Descripción corta]
Status: ✅ Completado / ⏳ En progreso / ❌ Fallido
Detalles:
- Qué se cambió
- Dónde corre (Windows/Pi)
- Test status
- Si requiere acción manual

Ejemplo:
Cambio: Agregar comando /avatar_metrics
Status: ✅ Completado
Detalles:
- Nuevo comando que devuelve estadísticas
- Corre en bot_consultas.py
- Testeado en Telegram
- Requiere reinicio del bot (ya hecho)
```

---

**Versión:** 1.0  
**Última actualización:** 2026-03-29  
**Audiencia:** Claude Code + Robe (desarrollo)
