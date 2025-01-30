import pandas as pd
import sqlite3

# Ruta del archivo Excel y la base de datos
excel_file = "Codigos.xlsx"  # Ruta del archivo Excel
sheet_name = "INSUMOS"  # Hoja del Excel
database_file = "db.sqlite3"  # Ruta del archivo SQLite3
tabla = 'presupuestos_insumo'

try:
    # Leer el archivo Excel y omitir la primera fila (títulos)
    print("Leyendo el archivo Excel...")
    df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols="A:G", header=0, skiprows=1)
    df.columns = ["codigo", "descripcion", "precio", "unidad_medida", "formula", "color_id", "tipo_insumo_id"]

    # Convertir valores nulos a None
    print("Convirtiendo valores nulos...")
    df = df.where(pd.notnull(df), None)

    # Convertir columnas numéricas a tipo float o 0 (en caso de error)
    print("Convirtiendo columnas numéricas...")
    df["precio"] = pd.to_numeric(df["precio"], errors="coerce").fillna(0)

    # Conectar a la base de datos SQLite
    print(f"Conectando a la base de datos {database_file}...")
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Borrar todos los registros existentes en la tabla
    print(f"Limpiando tabla {tabla}...")
    cursor.execute(f"DELETE FROM {tabla}")

    # Reiniciar el contador de IDs en la tabla
    print(f"Reiniciando el contador de IDs para la tabla {tabla}...")
    cursor.execute(f"UPDATE sqlite_sequence SET seq = 0 WHERE name = '{tabla}'")

    # Insertar los datos del DataFrame en la tabla (sin incluir el campo 'id')
    print("Insertando nuevos datos...")
    df.to_sql(tabla, conn, if_exists="append", index=False)

    print("Datos importados correctamente. Contador reiniciado.")

except Exception as e:
    print(f"Error durante la importación: {e}")

finally:
    # Cerrar la conexión a la base de datos
    if 'conn' in locals():
        conn.close()






