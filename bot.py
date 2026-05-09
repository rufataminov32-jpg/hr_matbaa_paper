import os
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from database import init_db, get_all_faq, add_faq, delete_faq
from file_reader import pdf_dan_matn, word_dan_matn, excel_dan_matn

# ─── SOZLAMALAR ──────────────────────────────────────────────────────────────

TOKEN    = os.environ["BOT_TOKEN"]   # Railway Variables da o'rnating
ADMIN_ID = int(os.environ["ADMIN_ID"])  # @userinfobot orqali toping

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Conversation states
WAIT_SAVOL, WAIT_JAVOB = range(2)


# ─── YORDAMCHI ───────────────────────────────────────────────────────────────

def is_admin(update: Update) -> bool:
    return update.effective_user.id == ADMIN_ID


def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Savol qo'shish",   callback_data="adm_add")],
        [InlineKeyboardButton("🗑 Savol o'chirish",  callback_data="adm_delete")],
        [InlineKeyboardButton("📋 Barcha savollar",  callback_data="adm_list")],
    ])


# ─── FOYDALANUVCHI ───────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    faq_list = get_all_faq()
    if not faq_list:
        await update.message.reply_text(
            "Hozircha savollar yo'q. Admin tez orada qo'shadi! 🙏"
        )
        return

    keyboard = [
        [InlineKeyboardButton(row[1], callback_data=f"faq_{row[0]}")]
        for row in faq_list
    ]
    await update.message.reply_text(
        "Salom! Quyidagi mavzulardan birini tanlang 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def faq_javob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    faq_id = int(query.data.split("_", 1)[1])
    for row in get_all_faq():
        if row[0] == faq_id:
            keyboard = [[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_start")]]
            await query.edit_message_text(
                f"❓ *{row[1]}*\n\n💬 {row[2]}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return


async def back_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    faq_list = get_all_faq()
    if not faq_list:
        await query.edit_message_text("Hozircha savollar yo'q.")
        return
    keyboard = [
        [InlineKeyboardButton(row[1], callback_data=f"faq_{row[0]}")]
        for row in faq_list
    ]
    await query.edit_message_text(
        "Mavzuni tanlang 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ─── ADMIN PANEL ─────────────────────────────────────────────────────────────

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Sizda ruxsat yo'q.")
        return
    await update.message.reply_text(
        "👨‍💼 *Admin panel*\nNimani qilmoqchisiz?",
        parse_mode="Markdown",
        reply_markup=admin_keyboard(),
    )


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # ── Ro'yxat ──
    if query.data == "adm_list":
        faq_list = get_all_faq()
        if not faq_list:
            await query.edit_message_text("Hozircha savollar yo'q.", reply_markup=admin_keyboard())
            return
        text = "📋 *Barcha savollar:*\n\n"
        for row in faq_list:
            text += f"*[{row[0]}]* {row[1]}\n   ➜ {row[2][:80]}{'...' if len(row[2]) > 80 else ''}\n\n"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_keyboard())

    # ── Qo'shish ──
    elif query.data == "adm_add":
        await query.edit_message_text("✏️ Yangi *savolni* kiriting:\n\n/bekor — bekor qilish", parse_mode="Markdown")
        return WAIT_SAVOL

    # ── O'chirish ro'yxati ──
    elif query.data == "adm_delete":
        faq_list = get_all_faq()
        if not faq_list:
            await query.edit_message_text("O'chiriladigan savol yo'q.", reply_markup=admin_keyboard())
            return
        keyboard = [
            [InlineKeyboardButton(f"❌ [{row[0]}] {row[1][:40]}", callback_data=f"del_{row[0]}")]
            for row in faq_list
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="adm_back")])
        await query.edit_message_text(
            "Qaysi savolni o'chirmoqchisiz?",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # ── O'chirish tasdiqlash ──
    elif query.data.startswith("del_"):
        faq_id = int(query.data.split("_", 1)[1])
        delete_faq(faq_id)
        await query.edit_message_text("✅ Savol o'chirildi!", reply_markup=admin_keyboard())

    # ── Orqaga ──
    elif query.data == "adm_back":
        await query.edit_message_text(
            "👨‍💼 *Admin panel*",
            parse_mode="Markdown",
            reply_markup=admin_keyboard(),
        )


# ─── SAVOL/JAVOB KIRITISH (ConversationHandler) ──────────────────────────────

async def savol_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["yangi_savol"] = update.message.text
    await update.message.reply_text("💬 Endi *javobni* kiriting:\n\n/bekor — bekor qilish", parse_mode="Markdown")
    return WAIT_JAVOB


async def javob_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    savol = context.user_data.pop("yangi_savol", "")
    javob = update.message.text
    add_faq(savol, javob)
    await update.message.reply_text(
        f"✅ *Qo'shildi!*\n\n❓ {savol}\n💬 {javob}",
        parse_mode="Markdown",
        reply_markup=admin_keyboard(),
    )
    return ConversationHandler.END


async def bekor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("yangi_savol", None)
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=admin_keyboard())
    return ConversationHandler.END


# ─── FAYL QABUL QILISH ───────────────────────────────────────────────────────

SUPPORTED_MIME = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


async def fayl_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Sizda ruxsat yo'q.")
        return

    doc = update.message.document
    mime = doc.mime_type or ""
    name = (doc.file_name or "").lower()

    if mime not in SUPPORTED_MIME and not (
        name.endswith(".pdf") or name.endswith(".docx") or name.endswith(".xlsx")
    ):
        await update.message.reply_text("❌ Faqat PDF, Word (.docx) yoki Excel (.xlsx) yuborish mumkin.")
        return

    await update.message.reply_text("⏳ Fayl o'qilmoqda...")

    # Faylni yuklab olish
    tg_file = await doc.get_file()
    tmp_path = f"/tmp/{doc.file_name}"
    await tg_file.download_to_drive(tmp_path)

    # Fayl turini aniqlash
    try:
        if name.endswith(".pdf") or mime == "application/pdf":
            juftlar = pdf_dan_matn(tmp_path)
            fayl_turi = "PDF"
        elif name.endswith(".docx"):
            juftlar = word_dan_matn(tmp_path)
            fayl_turi = "Word"
        elif name.endswith(".xlsx"):
            juftlar = excel_dan_matn(tmp_path)
            fayl_turi = "Excel"
        else:
            juftlar = []
            fayl_turi = "Noma'lum"
    except Exception as e:
        logger.error("Fayl o'qishda xatolik: %s", e)
        await update.message.reply_text(f"❌ Fayl o'qishda xatolik:\n{e}")
        os.remove(tmp_path)
        return

    os.remove(tmp_path)

    if not juftlar:
        await update.message.reply_text("❌ Fayldan hech qanday matn topilmadi.")
        return

    # Preview ko'rsatish
    context.user_data["fayl_juftlar"] = juftlar
    preview = f"📂 *{fayl_turi}* — {len(juftlar)} ta yozuv topildi:\n\n"
    for i, (s, j) in enumerate(juftlar[:4], 1):
        preview += f"{i}. ❓ {s}\n   💬 {j[:70]}{'...' if len(j) > 70 else ''}\n\n"
    if len(juftlar) > 4:
        preview += f"_...va yana {len(juftlar) - 4} ta_\n\n"
    preview += "✅ Barchasini FAQ ga qo'shayinmi?"

    keyboard = [[
        InlineKeyboardButton("✅ Ha, qo'sh", callback_data="fayl_tasdiqlash"),
        InlineKeyboardButton("❌ Yo'q",       callback_data="fayl_bekor"),
    ]]
    await update.message.reply_text(
        preview,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def fayl_tasdiqlash_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "fayl_bekor":
        context.user_data.pop("fayl_juftlar", None)
        await query.edit_message_text("❌ Bekor qilindi.", reply_markup=admin_keyboard())
        return

    juftlar = context.user_data.pop("fayl_juftlar", [])
    if not juftlar:
        await query.edit_message_text("❌ Ma'lumot topilmadi.")
        return

    qoshildi = 0
    for savol, javob in juftlar:
        if savol and javob:
            add_faq(savol, javob)
            qoshildi += 1

    await query.edit_message_text(
        f"✅ *{qoshildi} ta yozuv FAQ ga qo'shildi!*\n\nFoydalanuvchilar /start orqali ko'ra oladi.",
        parse_mode="Markdown",
        reply_markup=admin_keyboard(),
    )


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_callback, pattern="^adm_add$")],
        states={
            WAIT_SAVOL: [MessageHandler(filters.TEXT & ~filters.COMMAND, savol_qabul)],
            WAIT_JAVOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, javob_qabul)],
        },
        fallbacks=[CommandHandler("bekor", bekor)],
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(fayl_tasdiqlash_callback, pattern="^fayl_"))
    app.add_handler(CallbackQueryHandler(faq_javob,                 pattern="^faq_"))
    app.add_handler(CallbackQueryHandler(back_start,                pattern="^back_start$"))
    app.add_handler(CallbackQueryHandler(admin_callback,            pattern="^(adm_|del_)"))
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.Document.ALL, fayl_qabul))
    logger.info("Bot ishga tushdi ✅")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
