import requests
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, MODEL_NAME

def ask_llm(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Responde solo con base en el contexto entregado. Si no tienes información, responde: 'No tengo información sobre ese tema en los archivos cargados.'"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        return f"[Error al contactar con DeepSeek API]: {e}"
