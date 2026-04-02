import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables desde la raíz (subimos un nivel desde scripts/)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def run_inspection():
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    
    print("--- REPORTE DE ESTADO DEL RAG ---")
    try:
        with psycopg.connect(db_url, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                # 1. Verificar Extensión
                cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
                if cur.fetchone():
                    print("Extensión pgvector: INSTALADA")
                
                # 2. Conteo de filas y dimensiones
                cur.execute("SELECT count(*) as total FROM docs;")
                res = cur.fetchone()
                total = res['total'] if res else 0
                print(f"Documentos en DB: {total}")

                if total > 0:
                    # 3. Dimensiones
                    cur.execute("SELECT vector_dims(embedding) as dims FROM docs LIMIT 1;")
                    dims = cur.fetchone()['dims']
                    print(f"Dimensiones de vectores: {dims}")

                    # 4. Listado de fuentes
                    print("\n--- FUENTES PROCESADAS ---")
                    cur.execute("SELECT metadata->>'source' as src, count(*) as chunks FROM docs GROUP BY src;")
                    for s in cur.fetchall():
                        print(f"- {s['src']}: {s['chunks']} fragmentos")
                else:
                    print("La tabla está lista pero no tiene datos aún.")

    except Exception as e:
        print(f"Error conectando al contenedor: {e}")

if __name__ == "__main__":
    run_inspection()