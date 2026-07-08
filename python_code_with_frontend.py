import io
import cv2
import numpy as np
import pymysql
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


# -----------------------------------------------------------------------------
# 1. DATABASE CONNECTION (Using st.cache_resource to persist the connection pool)
# -----------------------------------------------------------------------------
@st.cache_resource
def init_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Atom*1987",
        database="final_project_retail_jan_2026",
        autocommit=True
    )


try:
    conn_obj = init_connection()
    cur_obj = conn_obj.cursor()
except Exception as e:
    st.error(f"Database Connection Failed: {e}")
    st.stop()


# -----------------------------------------------------------------------------
# 2. DATABASE HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def data_entry_cust_details(full_name, address, ph_number):
    sql = "INSERT INTO cust_details (cust_full_name, cust_address, cust_ph_number) VALUES (%s, %s, %s)"
    try:
        cur_obj.execute(sql, (full_name, address, ph_number))
        return True
    except pymysql.Error as e:
        st.error(f"Error inserting customer: {e}")
        return False


def data_retrieve_cust_details(ph_number):
    query = "SELECT * FROM cust_details WHERE cust_ph_number = %s"
    try:
        cur_obj.execute(query, (ph_number,))
        return cur_obj.fetchone()
    except pymysql.Error as e:
        st.error(f"Error retrieving customer: {e}")
        return None


def data_retrieve_product_details(product_id):
    query = "SELECT * FROM product_details WHERE p_id = %s"
    try:
        cur_obj.execute(query, (product_id,))
        return cur_obj.fetchone()
    except pymysql.Error as e:
        st.error(f"Error retrieving product: {e}")
        return None


def data_retrieve_audit_table():
    query = "SELECT MAX(bill_id) FROM audit_table"
    try:
        cur_obj.execute(query)
        return cur_obj.fetchone()
    except pymysql.Error as e:
        st.error(f"Error retrieving bill ID: {e}")
        return (None,)


def data_entry_BILL_DETAILS_TABLE(BILL_ID, C_ID, C_NAME, P_ID, P_NAME, P_PRICE, p_quantity):
    sql = """INSERT INTO BILL_DETAILS_TABLE(BILL_ID, C_ID, C_NAME, P_ID, P_NAME, P_PRICE, p_quantity) 
             VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    try:
        cur_obj.execute(sql, (BILL_ID, C_ID, C_NAME, P_ID, P_NAME, P_PRICE, p_quantity))
    except pymysql.Error as e:
        st.error(f"Error logging bill item: {e}")


def data_entry_audit_table(cust_id, cust_name, total_bill_amount):
    sql = "INSERT INTO audit_table(customer_id, customer_name, total_bill_amount) VALUES (%s, %s, %s)"
    try:
        cur_obj.execute(sql, (cust_id, cust_name, total_bill_amount))
    except pymysql.Error as e:
        st.error(f"Error completing transaction: {e}")


# -----------------------------------------------------------------------------
# 3. PDF GENERATION FUNCTION (Outputs to Bytes instead of saving to local disk)
# -----------------------------------------------------------------------------
def generate_pdf_bill(bill_id, cust_id, cust_name, bill_items, total_amount):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("RETAIL BILLING SYSTEM", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Bill ID : {bill_id}", styles['Normal']))
    elements.append(Paragraph(f"Customer ID : {cust_id}", styles['Normal']))
    elements.append(Paragraph(f"Customer Name : {cust_name}", styles['Normal']))
    elements.append(Spacer(1, 12))

    table_data = [["Product ID", "Product Name", "Qty", "Price", "Amount"]]
    for item in bill_items:
        table_data.append(item)

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER')
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Total Amount : Rs. {total_amount}</b>", styles['Heading2']))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# -----------------------------------------------------------------------------
# 4. STREAMLIT APP UI AND SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Retail Billing System", page_icon="🛒", layout="centered")
st.title("🛒 Retail Billing System")

if 'bill_items' not in st.session_state:
    st.session_state.bill_items = []
if 'total_amount' not in st.session_state:
    st.session_state.total_amount = 0.0
if 'cust_details' not in st.session_state:
    st.session_state.cust_details = None
if 'current_bill_id' not in st.session_state:
    st.session_state.current_bill_id = None
if 'checkout_complete' not in st.session_state:
    st.session_state.checkout_complete = False

# Step 1: Customer Lookup / Registration
if st.session_state.cust_details is None:
    st.subheader("Customer Authentication")
    ph_number = st.text_input("Enter Customer Phone Number:", max_chars=15).strip()

    if st.button("Proceed"):
        if ph_number:
            customer = data_retrieve_cust_details(ph_number)
            if customer:
                st.session_state.cust_details = {
                    'id': customer[0],
                    'name': customer[1],
                    'phone': ph_number
                }
                st.success(f"Welcome back, {customer[1]}!")
                st.rerun()
            else:
                st.session_state.register_mode = True
                st.session_state.pending_phone = ph_number
        else:
            st.warning("Please enter a phone number.")

    if st.session_state.get('register_mode', False):
        st.info("New customer detected. Please register:")
        full_name = st.text_input("Full Name:").strip().upper()
        address = st.text_input("Address:").strip().upper()

        if st.button("Register & Start Billing"):
            if full_name and address:
                if data_entry_cust_details(full_name, address, st.session_state.pending_phone):
                    customer = data_retrieve_cust_details(st.session_state.pending_phone)
                    if customer:
                        st.session_state.cust_details = {
                            'id': customer[0],
                            'name': customer[1],
                            'phone': st.session_state.pending_phone
                        }
                        st.success("Registration Successful!")
                        st.rerun()
            else:
                st.error("Please fill out all fields.")
    st.stop()

# -----------------------------------------------------------------------------
# Step 2: Core Billing System UI
# -----------------------------------------------------------------------------
cust = st.session_state.cust_details

# Calculate/assign running Bill ID
if st.session_state.current_bill_id is None:
    latest_bill_id = data_retrieve_audit_table()
    st.session_state.current_bill_id = 1 if latest_bill_id[0] is None else latest_bill_id[0] + 1

# Sidebar customer overview
st.sidebar.markdown(f"### 👤 Customer Profile")
st.sidebar.text(f"ID: {cust['id']}\nName: {cust['name']}\nPhone: {cust['phone']}")
st.sidebar.markdown(f"### 📑 Active Bill ID: **{st.session_state.current_bill_id}**")

if not st.session_state.checkout_complete:
    st.subheader("Add Products to Cart")

    # Input options toggler
    input_method = st.radio("Choose Input Method:", ("Scan QR Code", "Manual Input"), horizontal=True)
    scanned_pid = ""

    if input_method == "Scan QR Code":
        img_file = st.camera_input("Hold QR code up to your webcam and take a photo")
        if img_file is not None:
            # Convert image to OpenCV format
            bytes_data = img_file.getvalue()
            opencv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

            # Decode using OpenCV QR detector
            detector = cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(opencv_img)

            if data:
                scanned_pid = data.split("-")[0]
                st.success(f"Decoded Product ID: **{scanned_pid}**")
            else:
                st.error("Could not find a valid QR Code in image. Try re-aligning.")

    # Shared product lookup form
    with st.form("product_form", clear_on_submit=True):
        p_id = st.text_input("Product ID", value=scanned_pid if scanned_pid else "").strip()
        qty = st.number_input("Quantity", min_value=1, step=1, value=1)
        add_item = st.form_submit_button("Add Item to Cart")

    if add_item and p_id:
        p_details = data_retrieve_product_details(p_id)
        if p_details:
            p_name = p_details[1]
            p_price = float(p_details[-2])  # Using matches from your index logic
            amount = qty * p_price

            # Add item to session cart state
            st.session_state.bill_items.append([p_id, p_name, qty, p_price, amount])
            st.session_state.total_amount += amount

            # Insert record immediately into database table
            data_entry_BILL_DETAILS_TABLE(
                st.session_state.current_bill_id, cust['id'], cust['name'],
                p_id, p_name, p_details[2], qty
            )
            st.toast(f"Added {p_name} x{qty}!")
        else:
            st.error("Product ID not found in database.")

    # Display running shopping cart
    if st.session_state.bill_items:
        st.write("### Current Cart")
        st.table(st.session_state.bill_items)
        st.write(f"### Running Total: **Rs. {st.session_state.total_amount:.2f}**")

        # Checkout Actions
        if st.button("Proceed to Checkout & Finalize Bill", type="primary"):
            # Commit metadata to database audit records
            data_entry_audit_table(cust['id'], cust['name'], st.session_state.total_amount)
            st.session_state.checkout_complete = True
            st.rerun()

# -----------------------------------------------------------------------------
# Step 3: Checkout Completion and Document Printing
# -----------------------------------------------------------------------------
else:
    st.balloons()
    st.success("🎉 Transaction Completed Successfully!")

    st.write(f"### Total Paid: Rs. {st.session_state.total_amount:.2f}")
    st.table(st.session_state.bill_items)

    # Generate ReportLab compilation over memory buffer
    pdf_buffer = generate_pdf_bill(
        st.session_state.current_bill_id,
        cust['id'],
        cust['name'],
        st.session_state.bill_items,
        st.session_state.total_amount
    )

    st.download_button(
        label="📥 Download PDF Bill",
        data=pdf_buffer,
        file_name=f"Bill_{st.session_state.current_bill_id}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    if st.button("Start New Transaction"):
        st.session_state.clear()
        st.rerun()

