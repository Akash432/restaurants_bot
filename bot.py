import os
import random
import asyncio 
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from fpdf import FPDF
from datetime import datetime
 # add this at the top if missing



BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN not set in environment variables!")

DATA_DIR = "bills"
os.makedirs(DATA_DIR, exist_ok=True)

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
    pdf.cell(0, 10, "Delivery Address: Room 1007, Kapil Towers, Hyderabad", ln=True)
    pdf.cell(0, 10, f"Restaurant: {restaurant}", ln=True)
    pdf.cell(0, 10, f"Delivery Partner: {delivery}", ln=True)
    pdf.ln(5)

    subtotal = 0
    for item, price in items:
        subtotal += price

    gst = round(subtotal * 0.05, 2)
    delivery_fee = 55
    platform_fee = 10
    donation = 3
    total = subtotal + gst + platform_fee + donation

    pdf.cell(0, 10, f"Subtotal: ₹{subtotal}", ln=True)
    pdf.cell(0, 10, f"GST: ₹{gst}", ln=True)
    pdf.cell(0, 10, f"Platform Fee: ₹{platform_fee}", ln=True)
    pdf.cell(0, 10, f"Donation: ₹{donation}", ln=True)
    pdf.cell(0, 10, f"Total: ₹{total}", ln=True)

    pdf.output(filepath)
    return filepath

async def bill_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date_input = context.args[0]
    except IndexError:
        await update.message.reply_text("Please use: /bill DD-MM-YYYY")
        return

    meals = ["Breakfast", "Lunch", "Dinner"]
    paths = [create_bill(meal, date_input) for meal in meals]

    await update.message.reply_text(f"📦 Generating bills for {date_input}...")
    for path in paths:
        await update.message.reply_document(open(path, "rb"))

# ✅ TELEGRAM BOT FUNCTION

def run_bot():
    print("✅ Starting Telegram bot...")

    async def run():
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("bill", bill_command))
        await app.initialize()
        await app.start()
        print("✅ Bot is polling (thread safe)...")
        await app.updater.start_polling()
        # Removed idle — thread handles it
        # await app.idle()  # no need

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())
 
# ✅ FLASK SERVER TO KEEP RENDER ALIVE
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Restaurant Bill Bot is Running!"

# ✅ COMBINED LAUNCH
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    print(f"✅ Flask app running on port {port}")
    app.run(host="0.0.0.0", port=port)
