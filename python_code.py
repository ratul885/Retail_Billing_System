import pymysql
import QR_CODE_SCAN_JAN
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
conn_obj=pymysql.connect(
    host="localhost",
    user="root",
    password="Atom*1987",
    database="final_project_retail_jan_2026")
cur_obj=conn_obj.cursor()

#Define function data_entry_sql
def data_entry_cust_details(full_name,address,ph_number):
    sql = "INSERT INTO cust_details (cust_full_name, cust_address, cust_ph_number) VALUES (%s, %s, %s)"
    data = (full_name,address,ph_number)

    try:
        cur_obj.execute(sql, data)
        print(" NEW CUSTOMER ENTRY SUCCESSFUL.")
        conn_obj.commit()
    except pymysql.connect.Error as e:
        print("Error INSERTING DATA TO MySQL:", e)
        conn_obj.rollback()
def data_retrieve_cust_details(ph_number):

    query = f"select * from cust_details WHERE cust_ph_number='{ph_number}'"
    #print(query)

    try:
        cur_obj.execute(query)
        result = cur_obj.fetchone()
        conn_obj.commit()
    except pymysql.connect.Error as e:
        print("Error retrieving data from MySQL:", e)
        conn_obj.rollback()

    #print("cust details",result)
    return result
def data_retrieve_product_details(product_id):

    query = f"select * from product_details WHERE p_id='{product_id}'"
    #print(query)

    try:
        cur_obj.execute(query)
        result = cur_obj.fetchone()
        conn_obj.commit()
    except pymysql.connect.Error as e:
        print("Error retrieving data from MySQL:", e)
        conn_obj.rollback()

    #print("cust details",result)
    return result
def generate_pdf_bill(bill_id, cust_id, cust_name, bill_items, total_amount):

    filename = f"Bill_{bill_id}.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("RETAIL BILLING SYSTEM", styles['Title']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Bill ID : {bill_id}", styles['Normal']))
    elements.append(Paragraph(f"Customer ID : {cust_id}", styles['Normal']))
    elements.append(Paragraph(f"Customer Name : {cust_name}", styles['Normal']))
    elements.append(Spacer(1, 12))

    table_data = [
        ["Product ID", "Product Name", "Qty", "Price", "Amount"]
    ]

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

    elements.append(
        Paragraph(
            f"<b>Total Amount : Rs. {total_amount}</b>",
            styles['Heading2']
        )
    )

    doc.build(elements)

    print(f"\nPDF Bill Generated Successfully : {filename}")
def data_entry_audit_table(cust_id,cust_name,total_bill_amount):
    sql = "INSERT INTO audit_table(customer_id, customer_name, total_bill_amount) VALUES (%s, %s, %s)"
    data = (cust_id,cust_name,total_bill_amount)

    try:
        cur_obj.execute(sql, data)
        print(" AUDIT TABLE ENTRY SUCCESSFUL.")
        conn_obj.commit()
    except pymysql.connect.Error as e:
        print("Error INSERTING DATA TO MySQL:", e)
        conn_obj.rollback()
def data_retrieve_audit_table():

    query = f"select max(bill_id) from audit_table"
    #print(query)

    try:
        cur_obj.execute(query)
        result = cur_obj.fetchone()
        conn_obj.commit()
    except pymysql.connect.Error as e:
        print("Error retrieving data from MySQL:", e)
        conn_obj.rollback()

    #print("cust details",result)
    return result
def data_entry_BILL_DETAILS_TABLE(BILL_ID, C_ID, C_NAME, P_ID, P_NAME, P_PRICE, p_quantity):
    sql = "INSERT INTO BILL_DETAILS_TABLE(BILL_ID, C_ID, C_NAME, P_ID, P_NAME, P_PRICE, p_quantity) VALUES (%s, %s, %s,%s,%s,%s,%s)"
    data = (BILL_ID, C_ID, C_NAME, P_ID, P_NAME, P_PRICE, p_quantity)

    try:
        cur_obj.execute(sql, data)
        print(" BILL DETAILS TABLE SUCCESSFUL.")
        conn_obj.commit()
    except pymysql.connect.Error as e:
        print("Error INSERTING DATA TO MySQL:", e)
        conn_obj.rollback()
def billing(ph_number):

    total_bill_amount = 0

    bill_items = []

    latest_bill_id = data_retrieve_audit_table()

    if latest_bill_id[0] is None:
        bill_id = 1
    else:
        bill_id = latest_bill_id[0] + 1

    cust_details = data_retrieve_cust_details(ph_number)

    while True:

        print("\n1. Scan QR Code")
        print("2. Enter Product ID Manually")

        choice = input("Choose option : ")

        if choice == "1":

            print("Scanning QR...")

            scanned_data = QR_CODE_SCAN_JAN.qr_code_scanner()

            try:

                if scanned_data:

                    product_id = scanned_data.split("-")[0]

                    print("Product ID from QR :", product_id)

                else:

                    raise Exception

            except Exception:

                print("QR scan failed.")

                product_id = input(
                    "Enter Product ID manually : "
                ).strip()

        elif choice == "2":

            product_id = input(
                "Enter Product ID : "
            ).strip()

        else:

            print("Invalid choice")

            continue

        product_details_from_db = data_retrieve_product_details(
            product_id
        )

        if product_details_from_db:

            product_price = float(
                product_details_from_db[-2]
            )

            try:

                quantity = int(
                    input(
                        "Enter quantity : "
                    )
                )

            except ValueError:

                print(
                    "Invalid quantity."
                )

                continue

            amount = quantity * product_price

            bill_items.append(
                [
                    product_id,
                    product_details_from_db[1],
                    quantity,
                    product_price,
                    amount
                ]
            )

            data_entry_BILL_DETAILS_TABLE(
                bill_id,
                cust_details[0],
                cust_details[1],
                product_id,
                product_details_from_db[1],
                product_details_from_db[2],
                quantity
            )

            print(
                "Amount for product :",
                amount
            )

            total_bill_amount += amount

            print(
                "Running Total :",
                total_bill_amount
            )

        else:

            print(
                "Product details not found."
            )

        res = input(
            "Enter s to stop or any key to continue : "
        ).strip().lower()

        if res == "s":
            break

    print(
        "\nTotal amount to be paid :",
        total_bill_amount
    )

    cust_id = cust_details[0]
    cust_name = cust_details[1]

    data_entry_audit_table(
        cust_id,
        cust_name,
        total_bill_amount
    )

    generate_pdf_bill(
        bill_id,
        cust_id,
        cust_name,
        bill_items,
        total_bill_amount
    )
#Main logic starts here
ph_number=input("Enter the phone number of customer:")
cust_details_from_db=data_retrieve_cust_details(ph_number)
if cust_details_from_db:
    print("customer details existing...")
    print("Billing can be started now...")
    billing(ph_number)
else:
    print("New customer,please register....")
    full_name=input("Enter the full name of customer:").strip().upper()
    address= input("Enter the address of customer:").strip().upper()
    data_entry_cust_details(full_name,address,ph_number)
    billing(ph_number)
conn_obj.close()