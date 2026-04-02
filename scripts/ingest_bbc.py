import sys
from pathlib import Path
from datasets import load_dataset
from dotenv import load_dotenv

# importar desde la carpeta src/
sys.path.append(str(Path(__file__).parent.parent))
from src.database import VectorDB
from src.embeddings import EmbeddingManager

load_dotenv()

def start_ingestion():
    # 1. Carga, limitamos a 500 para no saturar la CPU/RAM local
    print("Cargando BBC News...")
    dataset = load_dataset("SetFit/bbc-news", split="train[:500]")
    
    # 2. Transformación
    chunks = [row['text'][:600].strip() for row in dataset]
    # Guardamos la categoría real en los metadatos
    metadatas = [{"category": row['label_text'], "source": "bbc"} for row in dataset]
    
    # 3. Procesamiento
    embedder = EmbeddingManager()
    db = VectorDB()
    
    print(f"Generando embeddings para {len(chunks)} noticias...")
    vectors = embedder.get_embeddings(chunks)
    
    # 4. Carga
    db.insert_documents(chunks, vectors, metadatas)
    print("✅ Ingesta completada.")

if __name__ == "__main__":
    start_ingestion()