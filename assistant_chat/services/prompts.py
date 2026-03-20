import json


def build_prompt(user_message: str, candidates: list) -> str:
    """
    Construeix el prompt que s'enviarà al model LLM per generar recomanacions
    d'esdeveniments basades en un conjunt de candidats.

    Procés:
    1. Converteix els esdeveniments candidats a format JSON llegible
    2. Defineix instruccions estrictes per limitar el comportament del model
    3. Especifica el format exacte de resposta (JSON)
    4. Inclou el context i la petició de l'usuari

    Args:
        user_message (str): Missatge o consulta de l'usuari
        candidates (list): Llista d'esdeveniments disponibles per recomanar

    Returns:
        str: Prompt complet preparat per enviar al model
    """

    # Convertim els candidats a JSON formatat per facilitar la lectura del model
    ctx = json.dumps(candidates, ensure_ascii=False, indent=2)

    # Construïm el prompt amb instruccions estrictes i context
    return f"""
Ets un assistent que recomana esdeveniments del lloc StreamEvents.

IMPORTANT:
- NOMÉS pots recomanar esdeveniments que apareguin al CONTEXT.
- No inventis esdeveniments, dates, ni URLs.
- Si no hi ha cap esdeveniment adequat, digues-ho i demana aclariments.

Respon en català i en aquest format JSON EXACTE (sense text addicional fora del JSON):
{{
  "answer": "text curt amb recomanació",
  "recommended_ids": [1, 2, 3],
  "follow_up": "pregunta opcional per afinar (o buit)"
}}

CONTEXT (esdeveniments disponibles):
{ctx}

Petició de l'usuari: {user_message}
""".strip()