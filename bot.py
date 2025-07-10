import os
import random
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from fpdf import FPDF
from datetime import datetime

# Get bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN not set in environment variables!")

# Output directory
DATA_DIR = "bills"
os.makedirs(DATA_DIR, exist_ok=True)

# Sample data
restaurants = [
    "Paradise Biryani, Secunderabad",
    "Pista House, Kondapur",
    "Bawarchi, RTC X Road"
]

menu = [
    ("Chicken Biryani", 380),
    ("Paneer Butter Masala", 250),
    ("Butter Naan", 45),
    ("Tandoori Chicken", 390),
    ("Lassi", 70),
    ("Mutton Fry", 470)
]

partners = ["Amaranath Ram", "Suresh M", "Karthik R", "Neha Joshi"]

# =============================
# PDF Generator
# =============================
def create_bill(meal: str, date_str: str) -> str:
    order_id = "7048" + str(random.randint(100000, 999999))
    filename = f"Order_ID_{order_id}.pdf"
    filepath = os.path.join(DATA_DIR, filename)

    restaurant = random.choice(restaurants)
    items = random.sample(menu, k=random.randint(3, 5))
    delivery = random.choice(partners)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Zomato Food Order: Summary and Receipt", ln=True)

    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 10, f"Order ID: {order_id}", ln=True)
    pdf.cell(0, 10, f"Order Time: {meal.title()} on {date_str}", ln=True)
    pdf.cell(0, 10, "Customer: Praveen", ln=True)
    pdf.cell(0, 10, "Delivery Address: Room 1007, Kapil Towers, Financial District, Hyderabad", ln=True)
    pdf.cell(0, 10, f"Restaurant: {restaurant}", ln=True)
    pdf.cell(0, 10, f"Delivery Partner: {delivery}", ln=True)
    pdf.ln(5)

    subtotal = 0
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(120, 10, "Item", 1)
    pdf.cell(30, 10, "Qty", 1)
    pdf.cell(40, 10, "Price (₹)", 1, ln=True)

    pdf.set_font("Arial", '', 12)
    for item, price in items:
        qty = 1
        pdf.cell(120, 10, item, 1)
        pdf.cell(30, 10, str(qty), 1)
        pdf.cell(40, 10, str(price), 1, ln=True)
        subtotal += price * qty

    gst = round(subtotal * 0.05, 2)
    delivery_fee = 55
    platform_fee = 10
    donation = 3
    total = subtotal + gst + delivery_fee + platform_fee + donation - 55  # Free delivery offset

    pdf.ln(5)
    pdf.cell(0, 10, f"Subtotal: ₹{subtotal}", ln=True)
    pdf.cell(0, 10, f"GST (5%): ₹{gst}", ln=True)
    pdf.cell(0, 10, f"Platform Fee: ₹{platform_fee}", ln=True)
    pdf.cell(0, 10, f"Delivery Charge: ₹{delivery_fee} (Free with Gold)", ln=True)
    pdf.cell(0, 10, f"Donation: ₹{donation}", ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Total: ₹{total}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, "Terms & Conditions: https://www.zomato.com/policies/terms-of-service/...\nThis invoice is generated digitally and is valid without signature.\nFSSAI Lic. No. 13620013000795 | Lic. No. 10019064001810")

    pdf.output(filepath)
    return filepath

# =============================
# Telegram Bot Command
# =============================
async def bill_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date_input = context.args[0]
    except IndexError:
        await update.message.reply_text("Please use: /bill DD-MM-YYYY")
        return

    meals = ["Breakfast", "Lunch", "Dinner"]
    paths = [create_bill(meal, date_input) for meal in meals]

    for path in paths:
        await update.message.reply_document(open(path, "rb"))

# =============================
# Run Telegram Bot in Thread
# =============================
def run_telegram_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("bill", bill_command))
    print("✅ Telegram bot started.")
    app.run_polling()

# =============================
# Flask App to Keep Render Happy
# =============================
web_app = Flask(__name__)

@web_app.route('/')
def index():
    return "✅ Restaurant Bill Bot is Running!"

# =============================
# Entry Point
# =============================
if __name__ == "__main__":
    threading.Thread(target=run_telegram_bot).start()
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)
