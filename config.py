# =========================================
#  XURALIFE BOT — SOZLAMALAR
# =========================================

# 1) BotFather'dan olingan tokeningiz
TOKEN = '8835863005:AAEOvRXjC1f0cEU6tGUAb18cIfj9IP8HV2I'

# 2) Admin / Project Manager'larning Telegram ID raqamlari.
#    Shu ro'yxatdagi odamlar "Yangi vazifa yaratish" va "Kunlik xulosa"
#    tugmalarini ko'radi. Bir nechta admin bo'lsa, vergul bilan qo'shing.
ADMIN_IDS = [8835863005]

# 3) Har kuni ishchilarga eslatma yuboriladigan vaqt (24 soatlik format, server vaqti bo'yicha)
REMINDER_TIME = "09:00"

# 4) Har kuni PM'ga kunlik jamlangan xulosa yuboriladigan vaqt
SUMMARY_TIME = "18:00"

# 5) Eslatma va xulosa qaysi kunlari yuborilishi (0=Dushanba ... 6=Yakshanba)
WORK_DAYS = "mon-sat"   # APScheduler cron formatida (mon-fri, mon-sat, * — har kuni)

# 6) (Ixtiyoriy) AI tahlil uchun OpenAI API kaliti.
#    Bo'sh qoldirsangiz, bot izohni qisqartirmasdan, xom holicha PM'ga yuboradi.
OPENAI_API_KEY = ""

# 7) Ma'lumotlar bazasi fayli (SQLite — o'rnatish talab qilmaydi, tayyor holda ishlaydi)
DB_PATH = "xuralife_bot.db"

# 8) Ish bosqichlari (kerak bo'lsa o'zgartiring yoki qo'shing)
STAGES = ["Modellashtirish", "Teksturalash", "Yoritish", "Post-prodakshn"]
