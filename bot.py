# =========================================
#  XURALIFE — JAMOA BOSHQARUV BOTI
# =========================================
# Ishga tushirish: python bot.py
# Talab qilinadigan kutubxonalar requirements.txt faylida.

import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler

import config
import database as db
from ai_analysis import summarize_comment

bot = telebot.TeleBot(config.TOKEN)

# Har bir chat_id uchun vaqtinchalik holatni saqlaymiz (bosqichma-bosqich savol-javob uchun)
session = {}


def is_admin(telegram_id):
    return telegram_id in config.ADMIN_IDS


def notify_admins(text, photo_file_id=None):
    for admin_id in config.ADMIN_IDS:
        try:
            if photo_file_id:
                bot.send_photo(admin_id, photo_file_id, caption=text, parse_mode='HTML')
            else:
                bot.send_message(admin_id, text, parse_mode='HTML')
        except Exception as e:
            print(f"Admin {admin_id} ga xabar yuborishda xatolik:", e)


# ---------------------------------------------------
# /start — ro'yxatdan o'tish va asosiy menyu
# ---------------------------------------------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    tg_id = message.from_user.id
    admin_flag = is_admin(tg_id)

    db.upsert_employee(
        telegram_id=tg_id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        is_admin=admin_flag,
    )

    show_main_menu(message.chat.id, admin_flag)


def show_main_menu(chat_id, admin_flag):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if admin_flag:
        markup.add(
            types.KeyboardButton("🆕 Yangi vazifa"),
            types.KeyboardButton("📊 Bugungi xulosa"),
        )
        markup.add(types.KeyboardButton("👥 Xodimlar ro'yxati"))
        text = "Assalomu alaykum! XURALIFE boshqaruv paneliga xush kelibsiz, Rahbar."
    else:
        markup.add(
            types.KeyboardButton("📝 Hisobot topshirish"),
            types.KeyboardButton("📋 Mening vazifalarim"),
        )
        text = (
            "Assalomu alaykum! XURALIFE jamoasining ish boshqaruv botiga xush kelibsiz!\n\n"
            "Sizga vazifa biriktirilganda shu yerda xabar olasiz."
        )

    bot.send_message(chat_id, text, reply_markup=markup)


# ---------------------------------------------------
# ADMIN: YANGI VAZIFA YARATISH
# ---------------------------------------------------

@bot.message_handler(func=lambda m: m.text == "🆕 Yangi vazifa" and is_admin(m.from_user.id))
def new_task_start(message):
    session[message.chat.id] = {'mode': 'new_task'}
    bot.send_message(message.chat.id, "Vazifa nomini kiriting (masalan: \"Boboy Restaurant — zal render\"):",
                      reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, new_task_title)


def new_task_title(message):
    session[message.chat.id]['title'] = message.text
    bot.send_message(message.chat.id, "Vazifa haqida qisqacha tavsif yozing:")
    bot.register_next_step_handler(message, new_task_description)


def new_task_description(message):
    session[message.chat.id]['description'] = message.text
    bot.send_message(message.chat.id, "Dedlaynni kiriting (masalan: 05.09.2026 18:00):")
    bot.register_next_step_handler(message, new_task_deadline)


def new_task_deadline(message):
    session[message.chat.id]['deadline'] = message.text

    employees = db.list_employees(exclude_admins=True)
    if not employees:
        bot.send_message(
            message.chat.id,
            "Hozircha bironta xodim botga /start bosmagan. Avval xodimlaringizni botga "
            "ulanishini so'rang (ular botga /start yozishi kifoya), keyin qaytadan urinib ko'ring."
        )
        session.pop(message.chat.id, None)
        return

    markup = types.InlineKeyboardMarkup()
    for emp in employees:
        label = emp['full_name'] or (f"@{emp['username']}" if emp['username'] else f"ID:{emp['telegram_id']}")
        markup.add(types.InlineKeyboardButton(label, callback_data=f"assign_{emp['id']}"))

    bot.send_message(message.chat.id, "Vazifani qaysi xodimga biriktiramiz?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("assign_"))
def new_task_assign(call):
    chat_id = call.message.chat.id
    data = session.get(chat_id)
    if not data:
        bot.answer_callback_query(call.id, "Sessiya eskirgan, qaytadan boshlang.")
        return

    employee_id = int(call.data.split("_")[1])
    task_id = db.add_task(
        title=data['title'],
        description=data['description'],
        deadline=data['deadline'],
        assigned_to=employee_id,
        created_by=call.from_user.id,
    )
    session.pop(chat_id, None)

    employee = db.get_employee_by_id(employee_id)
    bot.edit_message_text(
        f"✅ Vazifa yaratildi va biriktirildi: <b>{data['title']}</b> → {employee['full_name']}",
        chat_id, call.message.message_id, parse_mode='HTML'
    )

    # Xodimga xabar yuborish
    try:
        bot.send_message(
            employee['telegram_id'],
            f"📌 <b>Sizga yangi vazifa biriktirildi!</b>\n\n"
            f"<b>Nomi:</b> {data['title']}\n"
            f"<b>Tavsif:</b> {data['description']}\n"
            f"<b>Dedlayn:</b> {data['deadline']}\n\n"
            f"Ish boshlanganda \"📝 Hisobot topshirish\" tugmasi orqali jarayonni yuboring.",
            parse_mode='HTML'
        )
    except Exception as e:
        print("Xodimga vazifa haqida xabar yuborilmadi:", e)


# ---------------------------------------------------
# ADMIN: XODIMLAR RO'YXATI
# ---------------------------------------------------

@bot.message_handler(func=lambda m: m.text == "👥 Xodimlar ro'yxati" and is_admin(m.from_user.id))
def show_employees(message):
    employees = db.list_employees(exclude_admins=True)
    if not employees:
        bot.send_message(message.chat.id, "Hozircha bironta xodim ro'yxatdan o'tmagan.")
        return

    lines = ["👥 <b>Ro'yxatdagi xodimlar:</b>\n"]
    for emp in employees:
        username = f"@{emp['username']}" if emp['username'] else "username yo'q"
        lines.append(f"• {emp['full_name']} ({username})")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode='HTML')


# ---------------------------------------------------
# ADMIN: BUGUNGI XULOSA (qo'lda ham chaqirish mumkin)
# ---------------------------------------------------

@bot.message_handler(func=lambda m: m.text == "📊 Bugungi xulosa" and is_admin(m.from_user.id))
def manual_summary(message):
    send_daily_summary()


def build_summary_text():
    reports = db.get_today_reports()
    if not reports:
        return "📊 Bugun hech kim hisobot topshirmadi."

    grouped = {}
    for r in reports:
        grouped.setdefault(r['full_name'], []).append(r)

    lines = ["📊 <b>Kunlik xulosa</b>\n"]
    for name, items in grouped.items():
        lines.append(f"👤 <b>{name}</b>")
        for it in items:
            time_part = it['created_at'][11:16]
            lines.append(f"   • [{time_part}] {it['task_title']} — {it['stage']}: {it['comment']}")
        lines.append("")
    return "\n".join(lines)


def send_daily_summary():
    text = build_summary_text()
    notify_admins(text)


# ---------------------------------------------------
# XODIM: MENING VAZIFALARIM
# ---------------------------------------------------

@bot.message_handler(func=lambda m: m.text == "📋 Mening vazifalarim")
def my_tasks(message):
    emp = db.get_employee_by_tg(message.from_user.id)
    if not emp:
        bot.send_message(message.chat.id, "Avval /start bosing.")
        return

    tasks = db.list_active_tasks_for_employee(emp['id'])
    if not tasks:
        bot.send_message(message.chat.id, "Hozircha sizga biriktirilgan faol vazifa yo'q.")
        return

    lines = ["📋 <b>Sizning faol vazifalaringiz:</b>\n"]
    for t in tasks:
        lines.append(f"• <b>{t['title']}</b> (holati: {t['status']}, dedlayn: {t['deadline']})")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode='HTML')


# ---------------------------------------------------
# XODIM: HISOBOT TOPSHIRISH
# ---------------------------------------------------

@bot.message_handler(func=lambda m: m.text == "📝 Hisobot topshirish")
def report_start(message):
    emp = db.get_employee_by_tg(message.from_user.id)
    if not emp:
        bot.send_message(message.chat.id, "Avval /start bosing.")
        return

    tasks = db.list_active_tasks_for_employee(emp['id'])
    if not tasks:
        bot.send_message(message.chat.id, "Sizda hozircha faol vazifa yo'q. Vazifa biriktirilishini kuting.")
        return

    markup = types.InlineKeyboardMarkup()
    for t in tasks:
        markup.add(types.InlineKeyboardButton(t['title'], callback_data=f"report_task_{t['id']}"))
    bot.send_message(message.chat.id, "Qaysi vazifa bo'yicha hisobot berasiz?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("report_task_"))
def report_pick_task(call):
    task_id = int(call.data.split("_")[2])
    session[call.message.chat.id] = {'mode': 'report', 'task_id': task_id}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for stage in config.STAGES:
        markup.add(types.KeyboardButton(stage))

    bot.send_message(call.message.chat.id, "Hozir loyihaning qaysi bosqichidasiz?", reply_markup=markup)
    bot.register_next_step_handler(call.message, report_process_stage)


def report_process_stage(message):
    data = session.get(message.chat.id)
    if not data or data.get('mode') != 'report':
        bot.send_message(message.chat.id, "Avval \"📝 Hisobot topshirish\" tugmasini bosing.")
        return

    data['stage'] = message.text
    bot.send_message(
        message.chat.id,
        f"Ajoyib. Siz '{message.text}' bosqichini tanladingiz.\n"
        f"Iltimos, ish jarayonidan skrinshot yoki render xomakisini (draft) yuboring:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(message, report_process_photo)


def report_process_photo(message):
    data = session.get(message.chat.id)
    if not data or data.get('mode') != 'report':
        return

    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "Iltimos, faqat rasm (skrinshot) yuboring!")
        bot.register_next_step_handler(message, report_process_photo)
        return

    data['photo'] = message.photo[-1].file_id

    if message.caption:
        data['comment'] = message.caption
        finish_report(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Iltimos, rasmga qisqacha izoh yozing (nimalar qilindi?):")
        bot.register_next_step_handler(message, report_process_caption)


def report_process_caption(message):
    data = session.get(message.chat.id)
    if not data or data.get('mode') != 'report':
        return
    data['comment'] = message.text
    finish_report(message.chat.id)


def finish_report(chat_id):
    data = session.pop(chat_id, None)
    if not data:
        return

    emp = db.get_employee_by_tg(chat_id)
    task = db.get_task(data['task_id'])

    db.add_report(
        task_id=data['task_id'],
        employee_id=emp['id'],
        stage=data['stage'],
        comment=data['comment'],
        photo_file_id=data['photo'],
    )

    if task['status'] == 'yangi':
        db.update_task_status(data['task_id'], 'jarayonda')

    bot.send_message(chat_id, "✅ Hisobotingiz qabul qilindi va rahbariyatga yuborildi. Ishingizga omad!")

    # AI yordamida izohni qisqartirish (kalit bo'lmasa - o'zgarishsiz qaytadi)
    short_comment = summarize_comment(data['stage'], data['comment'])

    report_text = (
        f"📊 <b>Yangi hisobot!</b>\n\n"
        f"<b>Xodim:</b> {emp['full_name']}\n"
        f"<b>Vazifa:</b> {task['title']}\n"
        f"<b>Bosqich:</b> {data['stage']}\n"
        f"<b>Izoh:</b> {short_comment}"
    )
    notify_admins(report_text, photo_file_id=data['photo'])

    # Vazifa tugadimi — savol
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Ha, vazifa tugadi", callback_data=f"done_yes_{data['task_id']}"),
        types.InlineKeyboardButton("🔄 Yo'q, davom etyapti", callback_data=f"done_no_{data['task_id']}"),
    )
    bot.send_message(chat_id, "Ushbu vazifa butunlay yakunlandimi?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("done_"))
def report_task_done(call):
    _, decision, task_id = call.data.split("_")
    task_id = int(task_id)
    if decision == "yes":
        db.update_task_status(task_id, 'tugallangan')
        bot.edit_message_text("🎉 Vazifa yakunlangan deb belgilandi. Zo'r ish!",
                               call.message.chat.id, call.message.message_id)
        task = db.get_task(task_id)
        notify_admins(f"🎉 Vazifa yakunlandi: <b>{task['title']}</b>")
    else:
        bot.edit_message_text("Yaxshi, vazifa \"jarayonda\" holatida qoladi.",
                               call.message.chat.id, call.message.message_id)


# ---------------------------------------------------
# KUNLIK AVTOMATIK ESLATMA (ish boshlanishidan oldin)
# ---------------------------------------------------

def send_daily_reminders():
    tasks = db.list_all_active_tasks()
    if not tasks:
        return

    for t in tasks:
        emp = db.get_employee_by_id(t['assigned_to'])
        if not emp:
            continue
        try:
            bot.send_message(
                emp['telegram_id'],
                f"⏰ <b>Xayrli tong!</b> Ish kuni boshlanmoqda.\n\n"
                f"Vazifangiz: <b>{t['title']}</b> (dedlayn: {t['deadline']})\n"
                f"Bugungi jarayon haqida \"📝 Hisobot topshirish\" orqali yozishni unutmang.",
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Eslatma yuborilmadi ({emp['telegram_id']}):", e)


# ---------------------------------------------------
# SCHEDULER — REJALASHTIRILGAN VAZIFALAR
# ---------------------------------------------------

def setup_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Tashkent")

    r_hour, r_minute = map(int, config.REMINDER_TIME.split(":"))
    s_hour, s_minute = map(int, config.SUMMARY_TIME.split(":"))

    scheduler.add_job(
        send_daily_reminders, 'cron',
        day_of_week=config.WORK_DAYS, hour=r_hour, minute=r_minute
    )
    scheduler.add_job(
        send_daily_summary, 'cron',
        day_of_week=config.WORK_DAYS, hour=s_hour, minute=s_minute
    )

    scheduler.start()
    return scheduler


# ---------------------------------------------------
# BOTNI ISHGA TUSHIRISH
# ---------------------------------------------------

if __name__ == '__main__':
    db.init_db()
    setup_scheduler()
    print("XURALIFE boti muvaffaqiyatli ishga tushdi! Terminalni yopmang.")
    bot.infinity_polling()
