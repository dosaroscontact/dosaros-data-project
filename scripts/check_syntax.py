import py_compile
import glob
import sys

def main():
    files = glob.glob('src/**/*.py', recursive=True)
    if not files:
        print('No se encontraron archivos .py en src/')
        return

    errors = 0
    for f in files:
        try:
            py_compile.compile(f, doraise=True)
            print('OK ', f)
        except py_compile.PyCompileError as e:
            errors += 1
            print('ERR', f, '->', e)

    if errors:
        print(f"Terminado con {errors} errores de sintaxis.")
        sys.exit(1)
    else:
        print('Todas las comprobaciones de sintaxis pasaron correctamente.')

if __name__ == '__main__':
    main()
