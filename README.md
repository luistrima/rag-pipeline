# Professional RAG Pipeline: BBC News Semantic Search

Este proyecto es una implementación de nivel producción de un sistema de **Generación Aumentada por Recuperación (RAG)**. El objetivo es permitir la búsqueda semántica inteligente sobre un conjunto de datos de noticias de la BBC, utilizando una arquitectura moderna basada en vectores y procesamiento de lenguaje natural (NLP).

Diseñado con un enfoque en **Product Engineering**, este sistema demuestra cómo integrar bases de datos vectoriales en infraestructuras existentes de manera eficiente y escalable.

---

## Stack Tecnológico

* **Lenguaje:** Python 3.13 (Uso de `pathlib`, `typing` y contextos modernos).
* **Vector Database:** PostgreSQL con la extensión `pgvector`.
* **Machine Learning:** `sentence-transformers` (Modelo: `all-MiniLM-L6-v2`).
* **Orquestación de Datos:** Hugging Face `datasets` (BBC News).
* **Frontend:** Streamlit (Interfaz reactiva con filtrado dinámico).
* **Infraestructura:** Docker & Docker Compose (Contenedores aislados).

---

## Arquitectura y Decisiones Técnicas

### 1. Capa de Persistencia (PostgreSQL + pgvector)
En lugar de utilizar servicios SaaS propietarios, se optó por una solución *on-premise* dentro de PostgreSQL para garantizar la soberanía de los datos.
* **Índice HNSW:** Se configuró un índice *Hierarchical Navigable Small World* para búsquedas de similitud en tiempo sub-lineal, permitiendo escalar a miles de documentos sin pérdida de performance.
* **Filtrado Híbrido:** El sistema combina operadores vectoriales (`<=>`) con filtros relacionales sobre columnas `JSONB`, permitiendo segmentar por categorías (Tech, Politics, Sport) directamente en el motor de base de datos.

### 2. Pipeline de Ingesta (ETL)
Diseñado bajo principios de **Data Engineering** para asegurar la integridad y velocidad de carga:
* **Chunking Estratégico:** Fragmentación de noticias con un *overlap* de 50 caracteres para preservar la continuidad semántica.
* **Bulk Loading:** Uso del protocolo binario `COPY` de PostgreSQL, lo que reduce el tiempo de inserción en un 90% comparado con sentencias `INSERT` tradicionales.

### 3. Generación de Embeddings Local
El modelo se ejecuta localmente, lo que ofrece:
* **Baja Latencia:** Sin llamadas a APIs externas (OpenAI/Anthropic).
* **Coste Cero:** Escalabilidad infinita sin coste por token.
* **Privacidad:** Los datos nunca salen de la infraestructura del contenedor.

---

## Instalación y Despliegue

### Requisitos Previos
* Docker & Docker Compose.
* Python 3.10 o superior.

### Pasos para Ejecutar
1. **Clonar y Acceder:**
```bash
git clone [https://github.com/luistrima/rag-pipeline](https://github.com/luistrima/rag-pipelinet)
cd rag-pipeline
```
2. **Levantar Infraestructura:**
```bash
docker-compose up -d
```
3. **Instalar Dependencias:**
```bash
pip install -r requirements.txt
```

4. **Ejecutar Ingesta de datos (BBC News)**
```bash
python -m scripts.ingest_bbc
```

5. **Iniciar el Dashboard**
```bash
treamlit run app.py
```

## Funcionalidades del Dashboard
* Búsqueda por Concepto: Encuentra noticias relacionadas aunque no compartan las mismas palabras exactas.

* Filtro por Categoría: Selector dinámico para refinar búsquedas en sectores específicos (Business, Tech, etc.).

* Métricas de Confianza: Visualización del porcentaje de similitud semántica para cada resultado.

* Interfaz Wide-Layout: Optimizada para lectura de fragmentos de texto extensos.

## Autor

Luis Geovanny Triviño Macías
