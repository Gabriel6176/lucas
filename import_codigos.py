import pandas as pd
import sqlite3

# Ruta del archivo Excel y la base de datos
excel_file = "nomenclador.xlsx"  # Ruta del archivo Excel
sheet_name = "nomenclador"  # Hoja del Excel
database_file = "db.sqlite3"  # Ruta del archivo SQLite3

try:
    # Leer el archivo Excel
    print("Leyendo el archivo Excel...")
    df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols="C:K", header=0)
    df.columns = ["codigo", "descripcion", "honorarios", "ayudante", "gastos", "anestesia", "total", "servicio", "practica"]

    # Convertir valores nulos a None
    print("Convirtiendo valores nulos...")
    df = df.where(pd.notnull(df), None)

    # Convertir columnas numéricas a tipo float o 0 (en caso de error)
    for col in ["honorarios", "ayudante", "gastos", "anestesia", "total"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Conectar a la base de datos SQLite
    print(f"Conectando a la base de datos {database_file}...")
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Borrar todos los registros existentes en la tabla facturacion_prestacion
    print("Limpiando tabla facturacion_prestacion...")
    cursor.execute("DELETE FROM facturacion_prestacion")

    # Reiniciar el contador de IDs en la tabla facturacion_prestacion
    print("Reiniciando el contador de IDs...")
    cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'facturacion_prestacion'")

    # Insertar los datos del DataFrame en la tabla
    print("Insertando nuevos datos...")
    df.to_sql("facturacion_prestacion", conn, if_exists="append", index=False)

    print("Datos importados correctamente. Contador reiniciado.")

except Exception as e:
    print(f"Error durante la importación: {e}")

finally:
    # Cerrar la conexión a la base de datos
    if conn:
        conn.close()




