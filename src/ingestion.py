import os
from pathlib import Path
from dotenv import load_dotenv
from src.embeddings import EmbeddingManager
from src.database import VectorDB

load_dotenv()

class DataIngestor:
    def __init__(self):
        self.embedder = EmbeddingManager()
        self.db = VectorDB()
        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.chunk_size = int(os.getenv("CHUNK_SIZE", 500))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 50))

    def _split_text(self, text: str) -> list[str]:
        """
        Divide el texto en trozos (chunks) con solapamiento.
        """
        chunks = []
        # Implementación básica de sliding window
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i : i + self.chunk_size]
            chunks.append(chunk)
        return chunks

    def process_directory(self):
        """Escanea la carpeta data/ y procesa archivos .txt"""
        if not self.data_dir.exists():
            print(f"❌ Error: El directorio {self.data_dir} no existe.")
            return

        all_chunks = []
        all_metadata = []

        print(f"📂 Escaneando archivos en {self.data_dir}...")
        
        for file_path in self.data_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                chunks = self._split_text(content)
                
                for i, chunk in enumerate(chunks):
                    all_chunks.append(chunk)
                    all_metadata.append({
                        "source": file_path.name,
                        "chunk_id": i,
                        "length": len(chunk)
                    })
                
                print(f"✔️ Procesado: {file_path.name} ({len(chunks)} chunks)")

            except Exception as e:
                print(f"⚠️ Error procesando {file_path.name}: {e}")

        if all_chunks:
            print(f"🧠 Generando embeddings para {len(all_chunks)} trozos...")
            embeddings = self.embedder.get_embeddings(all_chunks)
            
            print("💾 Guardando en pgvector...")
            self.db.insert_documents(all_chunks, embeddings, all_metadata)
            print("🚀 Ingesta completada con éxito.")
        else:
            print("📭 No se encontraron archivos nuevos para procesar.")

if __name__ == "__main__":
    ingestor = DataIngestor()
    ingestor.process_directory()