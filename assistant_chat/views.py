import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .services.retriever import retrieve_events
from .services.prompts import build_prompt
from .services.llm_ollama import generate


def chat_page(request):
    """
    Vista que serveix la pàgina web del xat de l'assistent.
    
    Args:
        request (HttpRequest): Objecte de la petició HTTP
    
    Returns:
        HttpResponse: Pàgina HTML del xat
    """
    return render(request, "assistant_chat/chat.html")


@csrf_exempt
def chat_api(request):
    """
    API per al xat que rep missatges de l'usuari i retorna respostes generades
    pel model LLM basat en els esdeveniments disponibles.

    Procés:
    1. Verifica que la petició sigui POST
    2. Parseja el JSON rebut
    3. Recupera els esdeveniments rellevants amb retrieve_events
    4. Genera el prompt amb build_prompt
    5. Obté la resposta del model amb generate
    6. Valida i filtra la resposta
    7. Retorna JSON amb la resposta i esdeveniments recomanats

    Args:
        request (HttpRequest): Petició POST amb un JSON {"message": "...", "only_future": bool}

    Returns:
        JsonResponse: Resposta amb clau "answer", "follow_up" i "events"
    """

    # Només acceptem POST
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    # Parsejem el cos de la petició
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Extraiem el missatge i opció de només futurs
    msg = (payload.get("message") or "").strip()
    only_future = bool(payload.get("only_future", True))

    # Validació: missatge buit
    if not msg:
        return JsonResponse({"error": "Empty message"}, status=400)

    # Recuperem els esdeveniments més rellevants
    ranked = retrieve_events(msg, only_future=only_future, k=8)

    # Preparem els candidats per enviar al model
    candidates = []
    for evt, score in ranked:
        candidates.append({
            "id": int(evt.pk),
            "title": evt.title,
            "scheduled_date": evt.scheduled_date.isoformat() if evt.scheduled_date else None,
            "category": evt.category,
            "tags": evt.tags or "",
            "url": evt.get_absolute_url(),
            "score": round(float(score), 3),
        })

    # Construïm el prompt per al model
    prompt = build_prompt(msg, candidates)

    # Obtenim la resposta del model
    llm_text = generate(prompt)

    # Control de None — Ollama no disponible o error
    if llm_text is None:
        return JsonResponse({
            "answer": "L'assistent no està disponible en aquest moment. Torna-ho a provar.",
            "follow_up": "",
            "events": candidates[:3],  # mostrem els primers 3 com fallback
        })

    # Intentem parsejar la resposta JSON del model
    try:
        llm_json = json.loads(llm_text)
    except Exception:
        # Si falla, generem fallback
        llm_json = {
            "answer": "No he pogut generar una resposta estructurada. Prova amb una consulta més concreta.",
            "recommended_ids": [c["id"] for c in candidates[:3]],
            "follow_up": ""
        }

    # Filtrar només els IDs que estiguin dins dels candidats reals
    allowed_ids = {c["id"] for c in candidates}
    rec_ids = [i for i in llm_json.get("recommended_ids", []) if i in allowed_ids]

    # Generem la llista de targetes a mostrar
    cards = [c for c in candidates if c["id"] in rec_ids]
    if not cards:
        cards = candidates[:3]  # fallback si el model no recomana cap id vàlid

    # Retorn final com a JSON
    return JsonResponse({
        "answer": llm_json.get("answer", ""),
        "follow_up": llm_json.get("follow_up", ""),
        "events": cards,
    })