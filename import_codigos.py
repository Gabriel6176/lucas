import pandas as pd
import sqlite3

# Ruta del archivo Excel y la base de datos
excel_file = "Codigos.xlsx"
database_file = "db.sqlite3"

try:
    # Leer el archivo Excel
    df = pd.read_excel(excel_file, sheet_name="INSUMOS", usecols="A:G", skiprows=0)
    df.columns = ["codigo", "descripcion", "precio", "unidad_medida", "formula", "color_id", "tipo_insumo_id"]

    # Convertir valores nulos en el DataFrame a None
    df = df.where(pd.notnull(df), None)

    # Conectar a la base de datos SQLite
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Borrar todos los registros existentes en la tabla presupuestos_insumo
    cursor.execute("DELETE FROM presupuestos_insumo")

    # Reiniciar el contador de IDs en la tabla presupuestos_insumo
    cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'presupuestos_insumo'")

    # Insertar los datos del DataFrame en la tabla, excluyendo el campo `id`
    df.to_sql("presupuestos_insumo", conn, if_exists="append", index=False)

    print("Datos importados correctamente. Contador reiniciado.")

except Exception as e:
    print(f"Error actualizando la tabla: {e}")

finally:
    # Cerrar la conexión a la base de datos
    if conn:
        conn.close()



