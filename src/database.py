import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

class VectorDB:
    def __init__(self):
        """
        Inicializa la conexión usando las variables del archivo .env.
        """
        self.db_url = (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )

    def insert_documents(self, contents: list[str], embeddings: list[list[float]], metadatas: list[dict] = None):
        if metadatas is None:
            metadatas = [{} for _ in contents]

        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                with cur.copy("COPY docs (content, embedding, metadata) FROM STDIN") as copy:
                    for content, emb, meta in zip(contents, embeddings, metadatas):
                        import json
                        
                        # LA CORRECCIÓN: Convertir el vector a string formato Postgres
                        # Ejemplo: de [0.1, 0.2] a '[0.1, 0.2]'
                        vector_str = f"[{','.join(map(str, emb))}]"
                        
                        # Escribimos la fila con el vector ya formateado
                        copy.write_row((content, vector_str, json.dumps(meta)))
                conn.commit()
        print(f"{len(contents)} documentos insertados con éxito.")

    def search_similar(self, query_embedding, limit=5, category=None):
        # Convertimos el vector a string (como ya hicimos)
        vector_str = f"[{','.join(map(str, query_embedding))}]"

        # Lógica dinámica: si no hay categoría, no aplicamos filtro
        # Esto es más seguro que el NULL de SQL en algunos entornos
        where_clause = "1=1"
        params = [vector_str]

        if category:
            where_clause = "metadata->>'category' = %s"
            params.append(str(category))
        
        params.extend([vector_str, limit])

        query = f"""
            SELECT 
                content, 
                metadata, 
                1 - (embedding <=> %s::vector) AS similarity
            FROM docs
            WHERE {where_clause}
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """
        
        with psycopg.connect(self.db_url, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def get_connection(self):
        """Método de utilidad para scripts de inspección o tests manuales."""
        return psycopg.connect(self.db_url)