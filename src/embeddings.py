import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

class EmbeddingManager:
    def __init__(self):
        # Cargar el nombre del modelo desde el .env
        self.model_name = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        print(f"Loading model: {self.model_name}...")
        # device='cpu' asegura que no falle si no tienes una GPU NVIDIA configurada
        self.model = SentenceTransformer(self.model_name, device='cpu')

    def get_embeddings(self, text_list: list[str]) -> list[list[float]]:
        """
        Convierte una lista de textos en una lista de vectores (embeddings).
        """
        if not text_list:
            return []
        
        # convert_to_numpy=False nos devuelve listas de Python directamente
        embeddings = self.model.encode(text_list, convert_to_numpy=True).tolist()
        return embeddings

    def get_single_embedding(self, text: str) -> list[float]:
        """Útil para procesar la query del usuario en tiempo real."""
        return self.model.encode(text).tolist()