
# bot.py - Telegram bot that sends 3 restaurant bills as PDFs

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os, random
from generate_bill import create_bill

BOT_TOKEN = "PASTE_YOUR_TOKEN_HERE"

async def bill_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date_input = context.args[0]
    except IndexError:
        await update.message.reply_text("Usage: /bill DD-MM-YYYY")
        return

    bills = []
    for meal in ["Breakfast", "Lunch", "Dinner"]:
        bill = create_bill(meal, date_input)
        bills.append(bill)

    for bill in bills:
        await update.message.reply_document(open(bill, "rb"))

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("bill", bill_command))
    app.run_polling()
