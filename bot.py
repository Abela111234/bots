import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

# ======================
# CONFIG
# ======================
BOT_TOKEN = "8494561088:AAG5OvJtkXB3-pOvLRljb2DvrHkRx-fYAk0"  # Testing token
ADMIN_PASSWORD = "secret123"
RESULTS_FILE = "results.csv"

# ======================
# Helper Functions
# ======================
def load_results():
    if os.path.exists(RESULTS_FILE):
        return pd.read_csv(RESULTS_FILE)
    else:
        return pd.DataFrame()

async def send_student_result(update: Update, student_id: str):
    df = load_results()
    try:
        student = df[df["ID"] == int(student_id)]
    except:
        student = pd.DataFrame()
    
    if student.empty:
        await update.message.reply_text("❌ No result found. Please check your ID.")
        return
    
    row = student.iloc[0]
        msg = f"📊 Result for {row['Name']} (Grade {row['Grade']})\n\n"

    # All subjects to consider
    subjects = ["English","Math","Amharic","Kembatissa","IT","Physics","Chemistry","Biology",
                "History","Citizenship","Geography","Economics","HPE","Social_Studies",
                "Art","CTE","General_Science","Agriculture","Avrage"]
    
    has_subject = False
    for sub in subjects:
        if sub in df.columns:
            val = row[sub]
            if pd.notna(val) and str(val).strip() != "":
                msg += f"{sub}: {val}\n"
                has_subject = True
    
    if not has_subject:
        msg += "(No subjects yet)\n"
    
    msg += f"📈 Total: {row['Total']}\n"
    msg += f"🏅 Rank: {row['Rank']}"
    
    await update.message.reply_text(msg)

# ======================
# Commands
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to *Saint Anthony Results Bot*!\n\n"
        "➡️ Send your *student ID number* to check your results.",
        parse_mode="Markdown"
    )


async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text(
            "⚠️ Provide admin password. Example: `/upload secret123`", parse_mode="Markdown"
        )
        return
    
    password = context.args[0]
    if password != ADMIN_PASSWORD:
        await update.message.reply_text("❌ Wrong password.")
        return

    if not update.message.document:
        await update.message.reply_text("📎 Please attach a CSV file with the command.")
        return

    file = await update.message.document.get_file()
    await file.download_to_drive(RESULTS_FILE)
    await update.message.reply_text("✅ Results updated successfully!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.isdigit():
        await send_student_result(update, text)
    else:
        await update.message.reply_text("ℹ️ Please enter a valid numeric student ID.")

# ======================
# Main
# ======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("upload", upload))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
