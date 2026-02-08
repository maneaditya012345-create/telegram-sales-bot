import qrcode
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, MessageHandler,
    ChatMemberHandler, ContextTypes, filters
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

# ==================

# In-memory storage (use DB for large scale)
approved_users = set()
joined_users = set()
banned_users = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("💳 BUY Premium", callback_data="buy"),
        InlineKeyboardButton("🎬 DEMO & Proofs", callback_data="demo")
    ]]

    await update.message.reply_text(
        f"👋 *Welcome!*\n\n"
        f"🚀 *{PRODUCT_NAME}*\n"
        f"💰 Price: ₹{AMOUNT}\n\n"
        f"Choose an option 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    qr_text = f"upi://pay?pa={UPI_ID}&pn=DigitalStore&am={AMOUNT}&cu=INR"
    qr = qrcode.make(qr_text)
    qr_file = "payment_qr.png"
    qr.save(qr_file)

    context.user_data["awaiting_payment"] = True

    await update.callback_query.message.reply_photo(
        photo=open(qr_file, "rb"),
        caption=(
            f"💎 *{PRODUCT_NAME}*\n\n"
            f"💰 Amount: ₹{AMOUNT}\n"
            f"📲 UPI ID: `{UPI_ID}`\n\n"
            f"📸 Send payment screenshot here."
        ),
        parse_mode="Markdown"
    )


async def demo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        f"🎬 *Demos & Proofs*\n\n👉 {DEMO_GROUP_LINK}",
        disable_web_page_preview=True,
        parse_mode="Markdown"
    )


async def receive_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_payment"):
        return

    user_id = update.message.from_user.id

    keyboard = [[
        InlineKeyboardButton(
            "✅ Approve Payment",
            callback_data=f"approve_{user_id}"
        )
    ]]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=(
            f"💰 *Payment Screenshot*\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"📦 Product: *{PRODUCT_NAME}*\n"
            f"💵 Amount: ₹{AMOUNT}"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        "✅ Screenshot sent. Wait for approval."
    )


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.callback_query.data.split("_")[1])

    approved_users.add(user_id)

    invite = await context.bot.create_chat_invite_link(
        chat_id=PRODUCT_GROUP_ID,
        member_limit=1
    )

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            f"🎉 *Payment Approved!*\n\n"
            f"🔐 *One-Time Group Access Link:*\n"
            f"{invite.invite_link}\n\n"
            f"⚠️ Leaving the group permanently bans re-entry."
        ),
        parse_mode="Markdown"
    )

    await update.callback_query.message.reply_text(
        "✅ Approved & invite link sent."
    )


async def monitor_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.chat_member.chat
    user = update.chat_member.from_user
    new_status = update.chat_member.new_chat_member.status
    old_status = update.chat_member.old_chat_member.status

    if chat.id != PRODUCT_GROUP_ID:
        return

    user_id = user.id

    # User joined
    if new_status == ChatMember.MEMBER:
        if user_id in banned_users:
            await context.bot.ban_chat_member(PRODUCT_GROUP_ID, user_id)
            return

        joined_users.add(user_id)

    # User left
    if old_status == ChatMember.MEMBER and new_status in [ChatMember.LEFT, ChatMember.KICKED]:
        banned_users.add(user_id)
        await context.bot.ban_chat_member(PRODUCT_GROUP_ID, user_id)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buy, pattern="buy"))
    app.add_handler(CallbackQueryHandler(demo, pattern="demo"))
    app.add_handler(CallbackQueryHandler(approve, pattern="approve_"))
    app.add_handler(MessageHandler(filters.PHOTO, receive_payment))
    app.add_handler(ChatMemberHandler(monitor_group, ChatMemberHandler.CHAT_MEMBER))

    print("🤖 Auto-Ban Protected Sales Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()


