import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime
from fpdf import FPDF

# ====== CONFIG ======
BOT_TOKEN = "PASTE_YOUR_NEW_TOKEN_HERE"  # Replace this
DATA_DIR = "bills"  # Folder to store generated PDFs
os.makedirs(DATA_DIR, exist_ok=True)

# ====== SAMPLE DATA ======
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

# ====== PDF Generator ======
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

# ====== Telegram Command ======
async def bill_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date_input = context.args[0]  # from /bill 10-07-2025
    except IndexError:
        await update.message.reply_text("Please use: /bill DD-MM-YYYY")
        return

    paths = []
    for meal in ["Breakfast", "Lunch", "Dinner"]:
        pdf_path = create_bill(meal, date_input)
        paths.append(pdf_path)

    for path in paths:
        await update.message.reply_document(open(path, "rb"))

# ====== Run Bot ======
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("bill", bill_command))

if __name__ == "__main__":
    app.run_polling()
