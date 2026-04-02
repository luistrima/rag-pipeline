import streamlit as st
from src.database import VectorDB
from src.embeddings import EmbeddingManager

st.set_page_config(page_title="BBC News RAG", page_icon="📰")

@st.cache_resource
def init():
    return EmbeddingManager(), VectorDB()

embedder, db = init()

st.title("📰 BBC News: Buscador Semántico")
st.markdown("Busca noticias históricas usando IA y búsqueda vectorial.")

# Sidebar para filtros y estadísticas
with st.sidebar:
    st.header("Configuración")
    top_k = st.slider("Número de resultados", 1, 10, 5)
    st.divider()
    st.info("Dataset: BBC News (500 docs)")
    # --- BLOQUE DE FILTRO DE CATEGORÍAS ---
    # 1. Obtenemos las categorías únicas de la DB para el menú
    # (Si no quieres complicar database.py, puedes ponerlas a mano)
    categorias_disponibles = ["Todas", "tech", "business", "politics", "entertainment", "sport"]
    
    seleccion = st.selectbox("Filtrar por categoría:", categorias_disponibles)
    
    # Convertimos "Todas" a None para que el SQL funcione correctamente
    categoria_final = None if seleccion == "Todas" else seleccion
    # --------------------------------------

    st.info(f"Dataset: BBC News\nFiltro activo: {seleccion}")

# Input de búsqueda
query = st.text_input("Introduce tu búsqueda:", placeholder="Ej: Crisis in the tech sector or football results")

if query:
    with st.spinner("Analizando semántica..."):
        # 1. Generar vector de la consulta
        query_vector = embedder.get_single_embedding(query)
        
        # 2. Búsqueda en la DB - Enviamos la CATEGORÍA seleccionada a la DB
        results = db.search_similar(query_vector, limit=top_k, category=categoria_final)
        if results:
            for res in results:
                col1, col2 = st.columns([4, 1])
                
                # Extraer info de metadatos
                categoria = res['metadata'].get('category', 'N/A')
                score = round(res['similarity'] * 100, 1)
                
                with col1:
                    with st.expander(f"🔹 {res['content'][:80]}...", expanded=True):
                        st.write(res['content'])
                
                with col2:
                    st.metric("Relevancia", f"{score}%")
                    st.caption(f"Tag: {categoria}")
        else:
            st.error("No se encontraron noticias relacionadas.")

# footer
st.divider()
st.caption("Luis Triviño - Proyecto RAG Pipeline con PostgreSQL")