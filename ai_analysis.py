# =========================================
#  XURALIFE BOT — AI TAHLIL MODULI
# =========================================
# Agar config.py ichida OPENAI_API_KEY kiritilgan bo'lsa,
# xodim yozgan izoh OpenAI orqali PM uchun qisqa va tushunarli
# formatga o'tkaziladi. Kalit bo'lmasa, izoh o'zgarishsiz qaytariladi —
# bot baribir to'liq ishlayveradi, faqat bu "aqlli qisqartirish" o'chiq bo'ladi.

from config import OPENAI_API_KEY

_client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        _client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print("OpenAI kutubxonasi ulanmadi (pip install openai bajarilganmi?):", e)
        _client = None


def summarize_comment(stage: str, comment: str) -> str:
    """Xodim izohini PM uchun 1-2 gapga qisqartiradi. Kalit yo'q bo'lsa - xom izohni qaytaradi."""
    if not _client or not comment:
        return comment or "(izoh qoldirilmagan)"

    try:
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen interior dizayn studiyasi uchun ishlaydigan yordamchisan. "
                        "Xodimning ish jarayoni haqidagi izohini Project Manager uchun "
                        "1-2 qisqa jumlada, aniq va professional tarzda o'zbek tilida qayta yoz."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Bosqich: {stage}\nXodim izohi: {comment}",
                },
            ],
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("AI tahlilda xatolik:", e)
        return comment
