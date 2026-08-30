import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# GitHub Secrets থেকে API Key গ্রহণ
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

ai_client = OpenAI(api_key=OPENAI_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো! আমি GitHub Actions থেকে চলা AI বট। বলুন কীভাবে সাহায্য করতে পারি?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "তুমি একটি সাহায্যকারী টেলিগ্রাম বট। সংক্ষেপে উত্তর দাও।"},
                {"role": "user", "content": update.message.text}
            ]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = "কোনো একটি সমস্যা হয়েছে।"

    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("GitHub Actions-এ বট চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
