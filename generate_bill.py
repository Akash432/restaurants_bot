
# generate_bill.py - PDF bill generator

from fpdf import FPDF
import os, random

os.makedirs("bills", exist_ok=True)
restaurants = ["Paradise Biryani, Hyderabad", "Bawarchi, RTC X Road", "Pista House, Kondapur"]
menu = [("Chicken Biryani", 380), ("Butter Naan", 45), ("Paneer Butter Masala", 250), ("Mutton Fry", 470)]
partners = ["Amaranath Ram", "Suresh M", "Neha Joshi"]

def create_bill(meal, date_str):
    order_id = "7048" + str(random.randint(100000, 999999))
    filepath = f"bills/Order_ID_{order_id}.pdf"
    restaurant = random.choice(restaurants)
    delivery = random.choice(partners)
    items = random.sample(menu, k=4)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Zomato Food Order: Summary and Receipt", ln=True)

    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 10, f"Order ID: {order_id}", ln=True)
    pdf.cell(0, 10, f"Order Time: {meal} on {date_str}", ln=True)
    pdf.cell(0, 10, "Customer: Praveen", ln=True)
    pdf.cell(0, 10, "Delivery Address: Room 1007, Kapil Towers, Hyderabad", ln=True)
    pdf.cell(0, 10, f"Restaurant: {restaurant}", ln=True)
    pdf.cell(0, 10, f"Delivery Partner: {delivery}", ln=True)
    pdf.ln(5)

    total = 0
    for item, price in items:
        pdf.cell(0, 10, f"{item} - ₹{price}", ln=True)
        total += price

    tax = round(total * 0.05, 2)
    final = total + tax + 10 + 3
    pdf.ln(5)
    pdf.cell(0, 10, f"Subtotal: ₹{total}", ln=True)
    pdf.cell(0, 10, f"GST: ₹{tax}", ln=True)
    pdf.cell(0, 10, f"Platform Fee: ₹10", ln=True)
    pdf.cell(0, 10, f"Donation: ₹3", ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Total: ₹{final}", ln=True)
    pdf.output(filepath)
    return filepath
