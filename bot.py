import os
import sqlite3
from threading import Thread          
from flask import Flask             
from dotenv import load_dotenv
from openai import OpenAI

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ADMIN_ID = 6092280685

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY topilmadi")


app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "Bot ishlayapti!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host="0.0.0.0", port=port)

def keep_alive():
    Thread(target=run_web).start()

def save_user(user):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users
    (telegram_id, username, first_name)
    VALUES (?, ?, ?)
    """, (
        user.id,
        user.username,
        user.first_name
    ))

    conn.commit()
    conn.close()


def log_usage(user_id, feature):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO usage_logs
        (telegram_id, feature)
        VALUES (?, ?)
        """,
        (user_id, feature)
    )

    conn.commit()
    conn.close()


user_histories = {}




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    save_user(update.effective_user)

    await update.message.reply_text(
        "🤖 Salom!\n\n"
        "Men AI yordamchi botman.\n"
        "Savolingizni yuboring."
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in user_histories:
        user_histories[user_id] = []

    await update.message.reply_text(
        "🗑 Suhbat xotirasi tozalandi."
    )

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = " ".join(context.args)

    if not text:
        await update.message.reply_text(
            "Foydalanish:\n/post mavzu"
        )
        return

    log_usage(update.effective_user.id, "post")
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=[
            {
                "role": "system",
                "content": """
                Sen professional Telegram post yozuvchisan.

                Telegram kanal uchun:
                - Qiziqarli
                - O'qishga oson
                - Emoji bilan
                - Tayyor post yoz
                """
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    result = response.choices[0].message.content

    await update.message.reply_text(result)



async def hashtag(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = " ".join(context.args)

    if not text:
        await update.message.reply_text(
            "Foydalanish:\n/hashtag mavzu"
        )
        return

    log_usage(update.effective_user.id, "hashtag")
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=[
            {
                "role": "system",
                "content": "Berilgan mavzu uchun 15 ta hashtag yarat. Faqat hashtaglarni chiqar."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    result = response.choices[0].message.content

    await update.message.reply_text(result)

async def rewrite(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = " ".join(context.args)

    if not text:
        await update.message.reply_text(
            "Foydalanish:\n/rewrite matn"
        )
        return

    log_usage(update.effective_user.id, "rewrite")
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=[
            {
                "role": "system",
                "content": "Berilgan matnni professional va qiziqarli qilib qayta yoz."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    result = response.choices[0].message.content

    await update.message.reply_text(result)

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = " ".join(context.args)

    if not text:
        await update.message.reply_text(
            "Foydalanish:\n/name mavzu"
        )
        return

    log_usage(update.effective_user.id, "name")
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=[
            {
                "role": "system",
                "content": """
Telegram kanal, biznes, startup va brendlar uchun
10 ta kreativ nom yarat.
"""
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    result = response.choices[0].message.content

    await update.message.reply_text(result)

async def logo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = " ".join(context.args)

    if not text:
        await update.message.reply_text(
            "Foydalanish:\n/logo loyiha nomi"
        )
        return

    log_usage(update.effective_user.id, "logo")
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
        messages=[
            {
                "role": "system",
                "content": """
Professional logo yaratish uchun
Midjourney, Flux va ChatGPT Images ga mos
inglizcha prompt yarat.
"""
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    result = response.choices[0].message.content

    await update.message.reply_text(result)


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM usage_logs WHERE feature='post'")
    posts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM usage_logs WHERE feature='rewrite'")
    rewrites = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM usage_logs WHERE feature='hashtag'")
    hashtags = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM usage_logs WHERE feature='name'")
    names = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM usage_logs WHERE feature='logo'")
    logos = cursor.fetchone()[0]

    conn.close()

    await update.message.reply_text(
        f"""
👥 Foydalanuvchilar: {users}

📊 Statistika

📝 Post: {posts}
♻️ Rewrite: {rewrites}
#️⃣ Hashtag: {hashtags}
🏷 Name: {names}
🎨 Logo: {logos}
"""
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """
🤖 AI Assistant

Buyruqlar:

/start - Botni ishga tushirish
/help - Yordam
/about - Bot haqida
/clear - Xotirani tozalash

📝 Kontent:

/post - Telegram post yaratish
/rewrite - Matnni qayta yozish
/hashtag - Hashtag yaratish

🎨 Generatorlar:

/name - Kanal yoki brend nomi
/logo - Logo prompt generatori

📊 Statistika:

/admin - Admin panel

Misollar:

/post Sun'iy intellekt haqida post yoz

/rewrite Bugun yangi CCNA darsini yukladik

/hashtag Telegram marketing

/name Network Engineering

/logo NetMaster

Oddiy savollar ham berishingiz mumkin.
"""
    )
    
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """
👨‍💻 Yaratuvchi: Boburbek

🤖 Loyiha: AI Assistant

Funksiyalar:
• AI Chat
• Post Generator
• Hashtag Generator
• Rewrite
• Logo Prompt Generator
• Nom Generator

📢 Telegram:
@bbb00zx

🚀 Versiya: v1.0
"""
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """
❌ Noma'lum buyruq.

Mavjud buyruqlar:

/start - Botni ishga tushirish
/help - Yordam
/about - Bot haqida
/clear - Xotirani tozalash

/post - Post yaratish
/rewrite - Matnni qayta yozish
/hashtag - Hashtag yaratish
/name - Nom generatori
/logo - Logo prompt generatori

Misol:
/post Sun'iy intellekt haqida post yoz
"""
    )


async def handle_message(update: Update,
                         context: ContextTypes.DEFAULT_TYPE):

    try:
        user_id = update.effective_user.id
        username = update.effective_user.username
        user_text = update.message.text

        print(f"{username}: {user_text}")

        if user_id not in user_histories:
            user_histories[user_id] = []

        history = user_histories[user_id]

        history.append({
            "role": "user",
            "content": user_text
        })

        response = client.chat.completions.create(
    model="openai/gpt-oss-120b:free",
    messages=[
    {
        "role": "system",
        "content": """
Sen AI Assistant Telegram botisan.

Sening vazifang:
- O'zbek tilida javob berish.
- Foydalanuvchiga yordam berish.
- Aniq va foydali javob berish.
- Keraksiz uzun javoblardan qochish.

Sen quyidagi funksiyalarni bajara olasan:
- AI Chat
- Post Generator
- Rewrite
- Hashtag Generator
- Logo Prompt Generator
- Rasm Prompt Generator
- Kanal/Brend nom generatori

Agar foydalanuvchi:
'Sen kimsan?'
'Nima qila olasan?'
'Buyruqlaring qanday?'

deb so'rasa, o'zingni tanishtir va funksiyalaringni tushuntir.

Agar foydalanuvchi:
'Kim yaratgan?'
'Yaratuvching kim?'

deb so'rsa:

'Bu bot Boburbek tomonidan yaratilgan Telegram AI Assistant loyihasidir.'

deb javob ber.

Har doim o'zbek tilida javob ber.
"""
    },
    *history[-10:]
]
)

        answer = response.choices[0].message.content

        history.append({
            "role": "assistant",
            "content": answer
        })

        await update.message.reply_text(answer)

    except Exception as e:
        print(e)

        await update.message.reply_text(
            f"❌ Xatolik:\n{str(e)}"
        )

if __name__ == "__main__":
    keep_alive()
    main()

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("post", post))
    app.add_handler(CommandHandler("hashtag", hashtag))
    app.add_handler(CommandHandler("rewrite", rewrite))
    app.add_handler(CommandHandler("name", name))
    app.add_handler(CommandHandler("logo", logo))
    app.add_handler(CommandHandler("about", about))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    app.add_handler(
    MessageHandler(filters.COMMAND, unknown)
)

    print("🚀 Bot ishga tushdi...")

    app.run_polling()


if __name__ == "__main__":
    init_db()
    keep_alive()
    main()
