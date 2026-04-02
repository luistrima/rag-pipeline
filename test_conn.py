import os
import sys
import psycopg
from dotenv import load_dotenv

# 1. Cargar configuración centralizada
load_dotenv()

def test_connection():
    """Prueba la conexión y prepara el esquema inicial."""
    
    # Construir la DSN (Data Source Name) desde el entorno
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

    print(f"Intentando conectar a: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}...")

    try:
        # 2. Uso de 'with' para asegurar que la conexión se cierre sola (Context Manager)
        # autocommit=True es útil para tareas de administración como CREATE DATABASE/EXTENSION
        with psycopg.connect(db_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                
                # 3. Verificación de versión
                cur.execute("SELECT version();")
                print(f"PostgreSQL: {cur.fetchone()[0]}")

                # 4. Asegurar extensión pgvector
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                print("Extensión 'vector' verificada.")

                # 5. Esquema con dimensiones realistas para 'all-MiniLM-L6-v2' (384)
                print("Preparando tablas...")
                cur.execute("""
                    DROP TABLE IF EXISTS docs CASCADE;
                    CREATE TABLE docs (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        embedding vector(384)
                    );
                """)
                
                # 6. Crear índice HNSW (Optimizado para búsqueda semántica)
                # m=16, ef_construction=64 son valores estándar para empezar
                cur.execute("CREATE INDEX docs_hnsw_idx ON docs USING hnsw (embedding vector_cosine_ops);")
                print("Tabla e índice HNSW creados.")

                # 7. Test de inserción con dimensiones correctas
                # Creamos un vector dummy de 384 dimensiones
                dummy_vector = [0.1] * 384
                cur.execute("INSERT INTO docs (content, embedding) VALUES (%s, %s);", 
                           ("Test de conexión exitosa", dummy_vector))
                
                cur.execute("SELECT COUNT(*) FROM docs;")
                print(f"Verificación final: {cur.fetchone()[0]} fila(s) insertada(s).")

        print("DB preparada correctamente.")

    except Exception as e:
        print(f"Error crítico de base de datos:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    test_connection()