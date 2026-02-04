import json
import urllib.request
import urllib.error

# Standardowy punkt końcowy dla modeli Chat (GPT-4o, GPT-5 itd.)
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

def extract_text_from_response(result):
    """
    Wyciąga tekst tłumaczenia z odpowiedzi API.
    Obsługuje standardowy format OpenAI oraz formaty rozszerzone.
    """
    # Standardowa struktura OpenAI Chat Completions
    if "choices" in result and len(result["choices"]) > 0:
        choice = result["choices"][0]
        if "message" in choice and "content" in choice["message"]:
            return choice["message"]["content"].strip()
    
    # Fallback dla formatów 'output' (np. specyficzne proxy lub przyszłe API)
    if "output" in result:
        for item in result["output"]:
            if "content" in item and isinstance(item["content"], list):
                for part in item["content"]:
                    if "text" in part: return part["text"]
            if "text" in item: return item["text"]

    return None

def translate_text(api_key, text, system_prompt, model):
    """
    Wysyła zapytanie do OpenAI i zwraca przetłumaczony tekst.
    """
    # Budowa payloadu zgodnie ze standardem Chat Completions
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.3, # Niższa temperatura = bardziej spójne tłumaczenie
        "top_p": 1.0
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OPENAI_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    try:
        # Zwiększony timeout (300s) jest dobry dla dużych paczek napisów
        with urllib.request.urlopen(req, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"Błąd HTTP {e.code}: {error_body}")
    except Exception as e:
        raise RuntimeError(f"Błąd połączenia z API: {str(e)}")

    text_out = extract_text_from_response(result)

    if not text_out:
        raise RuntimeError(
            "Nie udało się odczytać tekstu z odpowiedzi OpenAI. "
            "Sprawdź format odpowiedzi lub stan konta API."
        )

    return text_out