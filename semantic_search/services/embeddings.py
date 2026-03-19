import threading
from sentence_transformers import SentenceTransformer

# Nom del model d'embeddings (multilingüe, lleuger i ràpid)
_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Lock per evitar condicions de carrera en carregar el model en entorns multithread
_lock = threading.Lock()

# Instància global del model (lazy loading)
_model = None


def get_model():
    """
    Retorna una instància singleton del model.

    Utilitza double-checked locking per:
    - Evitar carregar el model múltiples vegades
    - Ser segur en entorns amb múltiples fils
    """
    global _model

    # Primera comprovació (ràpida, sense lock)
    if _model is None:
        # Només un fil entra aquí alhora
        with _lock:
            # Segona comprovació (per si un altre fil ja l'ha carregat)
            if _model is None:
                _model = SentenceTransformer(_MODEL_NAME)

    return _model


def embed_text(text: str) -> list[float]:
    """
    Converteix un text en un embedding (vector numèric).

    - Normalitza el vector (norma = 1) per poder usar directament similitud cosinus amb dot product
    - Retorna una llista de floats per facilitar serialització (JSON, BD, etc.)
    """
    # Normalització bàsica de l'entrada
    text = (text or "").strip()

    # Evita processar textos buits
    if not text:
        return []

    # Obté el model (lazy load)
    model = get_model()

    # encode retorna una llista d'embeddings → [0] perquè només hi ha un text
    vec = model.encode([text], normalize_embeddings=True)[0]

    return vec.tolist()


def model_name() -> str:
    """
    Retorna el nom del model actual (útil per logs o debug).
    """
    return _MODEL_NAME