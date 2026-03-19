from django.shortcuts import render
from django.utils import timezone
from events.models import Event
from .services.embeddings import embed_text, model_name
from .services.ranker import cosine_top_k


def _event_text(e: Event) -> str:
    """
    Construeix un text agregat amb els camps més rellevants de l'event.

    Aquest text s'utilitza en altres parts del projecte per generar embeddings
    o mostrar informació semàntica completa.
    """
    parts = [
        e.title or "",
        e.description or "",
        e.category or "",
        e.tags or "",
    ]
    # Uneix només els camps no buits amb un delimitador "|"
    return " | ".join([p.strip() for p in parts if p and p.strip()])


def semantic_search(request):
    """
    Vista de cerca semàntica:

    1. Obté la query de l'usuari via GET.
    2. Genera embedding de la query amb el model carregat.
    3. Recupera events de la BD (opcionalment només futurs).
    4. Filtra events amb embeddings vàlids.
    5. Ordena per similitud cosinus i retorna els top-20.
    6. Renderitza la plantilla amb els resultats i metadades.
    """

    # Obté la query i elimina espais al principi i final
    q = (request.GET.get("q") or "").strip()

    # Boolean per decidir si només mostrar events futurs
    # True → només events amb scheduled_date >= avui
    only_future = request.GET.get("future", "1") == "1"

    results = []

    if q:
        # Genera embedding del text de la query
        q_vec = embed_text(q)

        # Consulta base: tots els events
        qs = Event.objects.all()

        # Si només volem futurs, filtrem per data >= ara
        if only_future:
            qs = qs.filter(scheduled_date__gte=timezone.now())

        items = []

        # Construcció de la llista d'events amb embeddings vàlids
        for e in qs:
            emb = getattr(e, "embedding", None)
            # Només afegeix embeddings que siguin llistes no buides
            if isinstance(emb, list) and len(emb) > 0:
                items.append((e, emb))

        # Ranking semàntic amb similitud cosinus (top 20)
        ranked = cosine_top_k(q_vec, items, k=20)
        results = ranked

    # Context per passar a la plantilla
    context = {
        "query": q,                        # Query de l'usuari
        "results": results,                # Llista d'events ordenats per similitud
        "only_future": only_future,        # Indica si s'ha filtrat per futurs
        "embedding_model": model_name(),   # Nom del model d'embeddings (debug / informació)
    }

    # Renderitza la plantilla amb context
    return render(request, "semantic_search/search.html", context)