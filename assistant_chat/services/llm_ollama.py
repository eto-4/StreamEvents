# assistant_chat > Services > llm_ollama.py

import requests

# URL del servei local d'Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"

# Model que s'utilitzarà per generar respostes
OLLAMA_MODEL = "llama3.1:8b"


def generate(prompt: str) -> str:
    """
    Envia un prompt a Ollama i retorna la resposta generada pel model.

    Procés:
    1. Construeix el payload amb els paràmetres del model
    2. Fa una petició HTTP POST al servei d'Ollama
    3. Valida la resposta i la converteix a JSON
    4. Extreu el text generat
    5. Retorna el text netejat

    Args:
        prompt (str): Text d'entrada que es vol enviar al model

    Returns:
        str | None: Text generat pel model o None si hi ha error
    """

    # Construcció del payload amb configuració del model
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,  # Es demana resposta completa (no streaming)
        "options": {
            "temperature": 0.2,  # Control de creativitat (baix = més determinista)
            "top_p": 0.9,        # Sampling nucleus
            "num_ctx": 2048      # Mida màxima del context
        }
    }

    try:
        # Enviem la petició al servidor d'Ollama
        resp = requests.post(OLLAMA_URL, json=payload, timeout=60)

        # Llança excepció si el codi HTTP indica error
        resp.raise_for_status()

        # Convertim la resposta a JSON
        data = resp.json()

    except (requests.RequestException, ValueError):
        # Error de xarxa o resposta no vàlida
        return None

    # Extraiem el text generat pel model
    text = data.get("response")

    # Si no hi ha resposta, retornem None
    if not text:
        return None

    # Retornem el text netejat (sense espais extres)
    return text.strip()