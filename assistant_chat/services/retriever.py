from django.utils import timezone
from events.models import Event
from semantic_search.services.embeddings import embed_text
from semantic_search.services.ranker import cosine_top_k


def retrieve_events(
    query: str,
    only_future: bool = True,
    k: int = 8,
    min_score: float = 0.25
):
    """
    Recupera esdeveniments rellevants a partir d'una consulta de text utilitzant embeddings
    i similitud cosinus.

    Procés:
    1. Converteix la query en un vector (embedding)
    2. Obté els esdeveniments de la base de dades
    3. Filtra opcionalment els esdeveniments futurs
    4. Selecciona només aquells amb embeddings vàlids i compatibles
    5. Calcula la similitud cosinus i ordena els resultats
    6. Aplica un llindar mínim de score
    7. Retorna els k millors resultats

    Args:
        query (str): Text de cerca introduït per l'usuari
        only_future (bool): Si és True, només retorna esdeveniments futurs
        k (int): Nombre màxim de resultats finals a retornar
        min_score (float): Llindar mínim de similitud per considerar un resultat vàlid

    Returns:
        list[tuple[Event, float]]: Llista d'esdeveniments amb el seu score de similitud
    """

    # Genera l'embedding de la query
    qVec = embed_text(query)

    # Si no s'ha pogut generar l'embedding (error o text buit), retornem buit
    if not qVec:
        return []

    # Obtenim tots els esdeveniments
    qSet = Event.objects.all()

    # Filtre opcional per només esdeveniments futurs
    if only_future:
        qSet = qSet.filter(scheduled_date__gte=timezone.now())

    items = []

    # Iterem sobre els esdeveniments per preparar-los per al càlcul de similitud
    for evt in qSet:
        # Obtenim l'embedding de l'event (si existeix)
        emb = getattr(evt, "embedding", None)

        # Validem que:
        # - sigui una llista
        # - tingui la mateixa dimensió que la query
        if isinstance(emb, list) and len(emb) == len(qVec):
            items.append((evt, emb))

    # Calculem més resultats dels necessaris per compensar el filtratge posterior
    initial_k = max(k * 3, 20)

    # Obtenim els millors candidats segons similitud cosinus
    ranked = cosine_top_k(qVec, items, k=initial_k)

    # Eliminem resultats amb score baix (soroll)
    ranked = [
        (evt, score)
        for (evt, score) in ranked
        if score >= min_score
    ]

    # Retornem només els k millors resultats finals
    return ranked[:k]