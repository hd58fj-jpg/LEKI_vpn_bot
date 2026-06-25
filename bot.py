import telebot
import os
import sqlite3
from datetime import datetime, timedelta

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# --- DB ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    trial_end TEXT
)
""")
conn.commit()


# --- START ---
@bot.message_handler(commands=["start"])
def start(message):
    kb = telebot.types.InlineKeyboardMarkup()

    kb.add(
        telebot.types.InlineKeyboardButton("🎁 5 дней бесплатно", callback_data="trial")
    )

    kb.add(
        telebot.types.InlineKeyboardButton("💎 Тарифы", callback_data="price")
    )

    bot.send_message(
        message.chat.id,
        "🔥 LEKI VPN\n\n⚡ Быстрый VPN\n🔒 Приватность\n🚀 Без рекламы",
        reply_markup=kb
    )


# --- BUTTONS ---
@bot.callback_query_handler(func=lambda c: True)
def buttons(call):

    user_id = call.message.chat.id

    if call.data == "trial":

        cur.execute("SELECT trial_end FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()

        now = datetime.now()

        # если уже есть подписка
        if row and datetime.fromisoformat(row[0]) > now:
            bot.send_message(user_id, "⛔ Уже активирован пробный период")
            return

        end = now + timedelta(days=5)

        cur.execute(
            "INSERT OR REPLACE INTO users (user_id, trial_end) VALUES (?, ?)",
            (user_id, end.isoformat())
        )
        conn.commit()

        bot.send_message(
            user_id,
            f"✅ VPN активирован\n\n⏳ До: {end.strftime('%Y-%m-%d %H:%M')}\n🔑 Ключ: скоро добавим"
        )


    elif call.data == "price":
        bot.send_message(
            user_id,
            "💎 LEKI VPN\n\n1 месяц — 199₽\n3 месяца — 499₽"
        )


bot.infinity_polling()
