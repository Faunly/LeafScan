from os import getenv

from dotenv import load_dotenv
from gigachat import GigaChat

load_dotenv()
auth_key = getenv("GIGACHAT_AUTH_KEY")

if not auth_key:
    print("ВНИМАНИЕ: GIGACHAT_AUTH_KEY не найден. Рекомендации будут отключены.")

giga = None

if auth_key:
    try:
        giga = GigaChat(
            credentials=auth_key,
            ca_bundle_file='certs/rus.crt', 
            model="GigaChat"
        )
        print("GigaChat Client успешно инициализирован.")
    except Exception as e:
        print(f"Ошибка инициализации GigaChat: {e}")
        giga = None


def get_recommendations(disease_name):
    if giga is None:
        return "Рекомендации временно недоступны (проблема с API ключом или сертификатом)."

    SYSTEM_INSTRUCTION_TEXT = (
        "Ты — высококвалифицированный, этичный агроном и фитопатолог, специализирующийся на органическом и безопасном садоводстве. "
        "Твоя задача — дать только 3 четкие, пошаговые и научно обоснованные рекомендации по борьбе с указанной болезнью. "
        "Правила: Используй только проверенные, безопасные методы. Ответ должен быть нумерованным списком из 3 пунктов. Никаких дополнительных пояснений или комментариев не допускается."
        "Выведи рекомендации в виде структурированного списка. Не используй символы форматирования Markdown (звездочки, решетки)."
    )
    
    USER_PROMPT_TEXT = (
        f"Обнаружена следующая проблема: **{disease_name}**. "
        f"Сгенерируй 3 конкретные рекомендации по уходу, следуя заданным правилам."
    )
    
    full_prompt = f"{SYSTEM_INSTRUCTION_TEXT}\n\n{USER_PROMPT_TEXT}"

    try:
        response = giga.chat(full_prompt)
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Не удалось загрузить рекомендации: {e}"
