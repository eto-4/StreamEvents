import numpy as np


def cosine_top_k(query_vec: list[float], items: list[tuple[object, list[float]]], k: int = 20):
    """
    Calcula la similitud cosinus (mitjançant dot product) entre un vector de query
    i una llista d'embeddings.

    items: [(event_obj, embedding_list), ...]
    
    Retorna:
        [(event_obj, score), ...] ordenat de més a menys similitud
    """

    # Si la query està buida → no hi ha res a comparar
    if not query_vec:
        return []

    # Convertim a numpy per operacions vectorials eficients
    q = np.array(query_vec, dtype=np.float32)

    # Evita problemes amb vectors nuls
    if np.linalg.norm(q) == 0:
        return []

    scored = []

    for obj, emb in items:
        # Ignorar embeddings buits
        if not emb:
            continue

        v = np.array(emb, dtype=np.float32)

        # Validacions:
        # - mateixa dimensió
        # - vector no nul
        if v.shape != q.shape or np.linalg.norm(v) == 0:
            continue

        # Com que els embeddings estan normalitzats:
        # dot product == similitud cosinus
        score = float(np.dot(q, v))

        scored.append((obj, score))

    # Ordenar descendent per score (més similar primer)
    scored.sort(key=lambda x: x[1], reverse=True)

    # Retornar només els top-k
    return scored[:k]