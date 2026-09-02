# XURALIFE — Jamoa boshqaruv boti

Sizning Excel rejangizdagi barcha asosiy funksiyalar shu botda amalga oshirilgan:

- **Haftalik rejalashtirish** — admin (PM) yangi vazifa yaratadi va xodimga biriktiradi, xodimga avtomatik xabar boradi
- **Kunlik eslatma** — har kuni belgilangan vaqtda faol vazifasi bor xodimlarga avtomatik eslatma keladi
- **Ish jarayoni** — xodim bosqichni tanlaydi (Modellashtirish / Teksturalash / Yoritish / Post-prodakshn), skrinshot va izoh yuboradi
- **AI tahlil** — izoh PM uchun qisqartiriladi (OpenAI kaliti kiritilsa ishlaydi, bo'lmasa xom izoh yuboriladi)
- **PM kunlik xulosa** — kun oxirida barcha xodimlarning bugungi hisobotlari jamlanib PM'ga yuboriladi

## 1. O'rnatish

```bash
pip install -r requirements.txt
```

## 2. Sozlash

`config.py` faylini oching va quyidagilarni tekshiring:

- `TOKEN` — BotFather bergan token (allaqachon kiritilgan)
- `ADMIN_IDS` — sizning Telegram ID raqamingiz ro'yxati (hozir `5842151066` turibdi — bu siz bo'lsangiz shunday qoldiring, boshqa PM/admin qo'shsangiz vergul bilan yozing)
- `REMINDER_TIME` / `SUMMARY_TIME` — eslatma va xulosa qaysi soatda yuborilishini belgilaydi
- `OPENAI_API_KEY` — ixtiyoriy. Kiritsangiz, xodim izohlari PM uchun avtomatik qisqartiriladi

## 3. Ishga tushirish

```bash
python bot.py
```

Terminalda "XURALIFE boti muvaffaqiyatli ishga tushdi!" yozuvi chiqsa — bot ishlayapti.

## 4. Qanday foydalanish

1. **Siz (admin)** botga `/start` bosasiz → "🆕 Yangi vazifa", "📊 Bugungi xulosa", "👥 Xodimlar ro'yxati" tugmalari chiqadi
2. **Har bir xodim** ham botga `/start` bosishi kerak — shundagina ular tizimda "ko'rinadi" va siz ularga vazifa biriktira olasiz
3. Vazifa yaratganda sizdan nomi, tavsifi, dedlayn so'raladi, so'ng xodimni tanlaysiz — unga avtomatik xabar boradi
4. Xodim har kuni ertalab (REMINDER_TIME'da) eslatma oladi va "📝 Hisobot topshirish" orqali vazifasini tanlab, bosqich + skrinshot + izoh yuboradi
5. Har bir hisobot darhol sizga (barcha ADMIN_IDS'ga) skrinshot bilan birga keladi
6. Kun oxirida (SUMMARY_TIME'da) barcha kunlik hisobotlar jamlanib sizga yuboriladi — buni "📊 Bugungi xulosa" tugmasi orqali istalgan vaqtda ham chaqirish mumkin

## 5. Fayl tuzilishi

```
xuralife_bot/
├── bot.py            → asosiy bot logikasi (handlerlar, scheduler)
├── database.py       → SQLite bilan ishlash (xodimlar, vazifalar, hisobotlar)
├── ai_analysis.py     → OpenAI orqali izohlarni qisqartirish
├── config.py          → barcha sozlamalar shu yerda
└── requirements.txt
```

Bot birinchi marta ishga tushganda `xuralife_bot.db` nomli SQLite fayl avtomatik yaratiladi — hech qanday qo'shimcha o'rnatish shart emas.

## 6. Keyingi bosqichlar (Excel faylingizdagi "Qo'shimcha imkoniyatlar")

Poydevor tayyor, shu asosda quyidagilarni qo'shish oson bo'ladi:

- **KPI/bonus tizimi** — `reports` jadvaliga vaqtida/kechikkan degan maydon qo'shib, oylik reyting hisoblash
- **"Qaynoq" xabarnomalar** — dedlaynga 2-3 soat qolganda alohida scheduler job qo'shish
- **Vaqt nazorati** — har bir bosqichga sarflangan vaqtni hisoblash uchun `reports` jadvaliga timestamp farqini qo'shish
- **Mijozlar uchun tasdiqlash oynasi** va **Telegram Web App (TWA) boshqaruv paneli** — bular alohida katta modullar, xohlasangiz keyingi bosqichda alohida quramiz

## 7. Botni doim ishlab turishi uchun

Kompyuteringizni yoqib qo'yish shart emas — botni arzon VPS (masalan, Timeweb, DigitalOcean) yoki Railway/Render kabi xizmatlarga joylashtirib, 24/7 ishlaydigan qilish mumkin. Shu bosqichda yordam kerak bo'lsa, ayting — deploy qilishda ham yordam beraman.
