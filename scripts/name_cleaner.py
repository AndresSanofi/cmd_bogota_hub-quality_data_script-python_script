"""
Modulo: name_cleaner.py
Descripcion: Transformacion de columnas Name 1 con normalizacion de mayusculas y abreviaciones configurables.
Autor: Andres Felipe YANEZ VILLARRAGA
Email: AndresFelipe.YANEZVILLARRAGA@sanofi.com
Fecha Creacion: 2026-05-14
Ultima Modificacion: 2026-05-14
Version: 1.0.0
"""

import sys
from pathlib import Path

# Agregar carpeta scripts al path para importar _core
sys.path.insert(0, str(Path(__file__).parent))
from _core import fix_name, load_file, save_file


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# Palabras clave para detectar columnas de nombre.
# Si su archivo tiene una columna con otro nombre, agréguela aquí.
# ─────────────────────────────────────────────────────────────────────────────

NAME_COLUMN_KEYWORDS = [
    'name 1',    # SAP Name 1
    'name',      # Name, Name 1, Name 2, Name 3, Name 4
    'nombre',    # Nombre
    'account',   # Account Name, Account
]


# ─────────────────────────────────────────────────────────────────────────────

def find_name_columns(df):
    """Detecta columnas cuyo nombre contenga alguna de las palabras clave."""
    found = []
    for col in df.columns:
        col_lower = col.lower().strip()
        if any(kw in col_lower for kw in NAME_COLUMN_KEYWORDS):
            found.append(col)
    return found


def apply_to_dataframe(df, selected_columns=None):
    target_columns = selected_columns or find_name_columns(df)

    if not target_columns:
        return df, {
            'success': False,
            'message': 'No se encontraron columnas de nombre.',
            'columns': [],
            'changes': 0,
        }

    total_changes = 0
    for col in target_columns:
        original = df[col].copy()
        df[col] = df[col].apply(fix_name)
        total_changes += (original.fillna('') != df[col].fillna('')).sum()

    return df, {
        'success': True,
        'message': '',
        'columns': target_columns,
        'changes': int(total_changes),
    }


def run(input_path, output_path, selected_columns=None):
    """
    Aplica corrección de nombres al archivo input_path
    y guarda el resultado en output_path.

    Returns:
        True si se procesó correctamente, False si no se encontraron columnas.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    print(f"\n[Corrección de Nombres]")
    print(f"  Leyendo: {input_path.name}")

    df = load_file(input_path)
    df, result = apply_to_dataframe(df, selected_columns=selected_columns)

    if not result['success']:
        print("  AVISO: No se encontraron columnas de Name 1.")
        print(f"  Columnas disponibles: {list(df.columns)}")
        print("  Para agregar su columna, edite NAME_COLUMN_KEYWORDS en scripts/name_cleaner.py")
        return False

    print(f"  Columnas encontradas: {result['columns']}")
    print(f"  Total corregido: {result['changes']} celda(s)")

    save_file(df, output_path)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Ejecución directa: python scripts/name_cleaner.py
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    input_dir = base_dir / 'input'
    output_dir = base_dir / 'output'

    # Buscar archivo en input/
    extensions = ['*.xlsx', '*.xlsb', '*.csv']
    files = []
    for ext in extensions:
        files.extend(input_dir.glob(ext))

    if not files:
        print("\nERROR: No hay archivos en la carpeta 'input'.")
        print("Por favor coloque un archivo .xlsx, .xlsb o .csv en esa carpeta.")
        input("\nPresione Enter para salir...")
        sys.exit(1)

    if len(files) > 1:
        print(f"\nSe encontraron {len(files)} archivos en 'input'. Se procesará el primero:")
        for i, f in enumerate(files):
            print(f"  {i+1}. {f.name}")

    input_file = files[0]
    output_file = output_dir / (input_file.stem + '_nombres_corregidos.xlsx')

    success = run(input_file, output_file)

    if success:
        print(f"\nArchivo guardado en: output/{output_file.name}")
    input("\nPresione Enter para salir...")
