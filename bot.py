import os
from google import genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# GitHub Secrets থেকে API Key গ্রহণ
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Gemini Client সেটআপ
client = genai.Client(api_key=GEMINI_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"হ্যালো {user_name}! আমি Gemini AI বট। আমাকে যেকোনো প্রশ্ন করতে পারেন।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # gemini-3.6-flash মডেল ব্যবহার করা হচ্ছে
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=update.message.text,
        )
        reply = response.text
    except Exception as e:
        reply = f"⚠️ সমস্যা ধরা পড়েছে:\n{str(e)}"

    await update.message.reply_text(reply)

def main():
    if not TELEGRAM_TOKEN:
        print("TELEGRAM_BOT_TOKEN পাওয়া যায়নি। প্রোগ্রাম বন্ধ হচ্ছে।")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Gemini AI বট চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
