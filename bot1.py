Updater
dispatcher
use_context
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ===== CONFIG =====

BOT_TOKEN = "8538591908:AAGUfv0KQeSiwsnFq_mOp_ymFMux2qjz3v4"

ADMIN_ID = 8506084888  # your Telegram numeric ID

UPI_ID = "9505adity@axl"
AMOUNT = "99"
PRODUCT_NAME = "Premium Content"

# PRIVATE PRODUCT GROUP ID (starts with -100)
PRODUCT_GROUP_ID = -1003802148499

DEMO_GROUP_LINK = "https://t.me/+TrtXYXl8gzllYzI1"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💎 BUY Premium", callback_data="buy")],
        [InlineKeyboardButton("🎥 DEMO & Proofs", url=DEMO_GROUP_LINK)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Welcome!\n\n"
        f"🔥 *{PRODUCT_NAME}*\n"
        f"💰 Price: ₹{AMOUNT}\n\n"
        f"Choose an option below 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy":
        await query.message.reply_text(
            f"💳 *Payment Details*\n\n"
            f"UPI ID: `{UPI_ID}`\n"
            f"Amount: ₹{AMOUNT}\n\n"
            f"✅ Pay & send screenshot to admin",
            parse_mode="Markdown"
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot running without Updater...")
    app.run_polling()

if __name__ == "__main__":
    main()
