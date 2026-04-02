-- 1. Habilitar la extensión de vectores
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Crear la tabla principal para las noticias
-- Usamos BIGSERIAL para el ID y JSONB para los metadatos de BBC News (categoría, autor, etc.)
CREATE TABLE IF NOT EXISTS docs (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(384),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Crear el índice HNSW (Optimizado para búsqueda semántica de alto rendimiento)
-- Importante: Usamos vector_cosine_ops porque los modelos de SentenceTransformers 
-- están diseñados para similitud coseno.
CREATE INDEX IF NOT EXISTS docs_hnsw_idx ON docs 
USING hnsw (embedding vector_cosine_ops);

-- 4. Función de búsqueda semántica (RPC - Remote Procedure Call)
-- Esta función encapsula la lógica para que tu Python solo tenga que enviar el vector.
CREATE OR REPLACE FUNCTION match_documents (
  query_embedding vector(384),
  match_threshold float,
  match_count int
)
RETURNS TABLE (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    docs.id,
    docs.content,
    docs.metadata,
    1 - (docs.embedding <=> query_embedding) AS similarity
  FROM docs
  WHERE 1 - (docs.embedding <=> query_embedding) > match_threshold
  ORDER BY docs.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;