import os
from google import genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# GitHub Secrets থেকে মান গ্রহণ
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if ADMIN_ID:
    ADMIN_ID = int(ADMIN_ID)

# Gemini Client সেটআপ
client = genai.Client(api_key=GEMINI_KEY)

# ইউজার আইডি সেভ করার জন্য ফাইল
USER_DATA_FILE = "users.txt"

def get_subscribed_users():
    if not os.path.exists(USER_DATA_FILE):
        return set()
    with open(USER_DATA_FILE, "r") as f:
        return {int(line.strip()) for line in f if line.strip().isdigit()}

def add_new_user(user_id):
    users = get_subscribed_users()
    if user_id not in users:
        with open(USER_DATA_FILE, "a") as f:
            f.write(f"{user_id}\n")

# /start কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_new_user(user.id)
    await update.message.reply_text(f"হ্যালো {user.first_name}! আমি Gemini AI বট। আমাকে যেকোনো প্রশ্ন করতে পারেন।")

# /broadcast কমান্ড (শুধুমাত্র আপনার জন্য)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ADMIN_ID or update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ এই কমান্ডটি শুধুমাত্র অ্যাডমিনের জন্য।")
        return

    if not context.args:
        await update.message.reply_text("⚠️ নোটিশ লিখুন। যেমন: `/broadcast আপনার বার্তা`", parse_mode="Markdown")
        return

    notice_text = " ".join(context.args)
    final_notice = f"📢 **অফিসিয়াল নোটিশ:**\n\n{notice_text}"
    
    all_users = get_subscribed_users()
    if not all_users:
        await update.message.reply_text("⚠️ কোনো ইউজার পাওয়া যায়নি।")
        return

    status_msg = await update.message.reply_text(f"⏳ নোটিশ পাঠানো হচ্ছে...")
    success, fail = 0, 0

    for user_id in all_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=final_notice, parse_mode="Markdown")
            success += 1
        except Exception:
            fail += 1

    await context.bot.edit_message_text(
        chat_id=ADMIN_ID,
        message_id=status_msg.message_id,
        text=f"✅ ব্রডকাস্ট সম্পন্ন!\n\nসফল: {success}\nব্যর্থ: {fail}"
    )

# AI উত্তর দেওয়ার ফাংশন
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_new_user(update.effective_user.id)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=update.message.text,
        )
        reply = response.text
    except Exception as e:
        reply = f"⚠️ সমস্যা ধরা পড়েছে:\n{str(e)}"

    await update.message.reply_text(reply)

def main():
    if not TELEGRAM_TOKEN:
        print("TELEGRAM_BOT_TOKEN পাওয়া যায়নি।")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Gemini AI বট চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
