import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """
    Establece una conexión con la base de datos PostgreSQL utilizando
    variables de entorno. Si no están configuradas, utiliza valores por defecto.
    """
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        database=os.environ.get("DB_NAME", "postgres"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres")
    )

def search_news_by_descriptor(descriptor: str):
    """
    Busca noticias cuyo título o contenido coincida con el descriptor provisto.
    Utiliza consultas parametrizadas para evitar ataques de Inyección SQL.
    """
    conn = get_db_connection()
    try:
        # Usamos RealDictCursor para que los resultados vengan como diccionarios
        # en lugar de tuplas, lo cual facilita mapear los datos a gRPC
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Consulta SQL parametrizada con %s
            query = """
                SELECT news_id, title, user_id, category_id, content, created_at
                FROM news
                WHERE title ILIKE %s OR content ILIKE %s
                ORDER BY created_at DESC;
            """
            
            # Preparamos el patrón de búsqueda (ej. "%deportes%")
            search_pattern = f"%{descriptor}%"
            
            # Ejecutamos pasando los parámetros en una tupla.
            # Psycopg2 se encarga de escapar y sanitizar los inputs de forma segura.
            cur.execute(query, (search_pattern, search_pattern))
            
            # Traemos todas las filas coincidentes
            rows = cur.fetchall()
            return rows
    except Exception as e:
        print(f"Error al buscar noticias en la base de datos: {e}")
        raise e
    finally:
        conn.close()
