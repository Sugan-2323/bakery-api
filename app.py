from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
import psycopg2

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE ----------------
# conn = pyodbc.connect(
#     "DRIVER={SQL Server};SERVER=LAPTOP-FL8R7OGR\\SQLEXPRESS;DATABASE=BakeryDB;Trusted_Connection=yes;"
# )
# cursor = conn.cursor()

conn = psycopg2.connect(
    host="db.qnydxtdgwnwrdwxqlqxp.supabase.co",
    database="postgres",
    user="postgres",
    password="suganbvss@@2003",
    port="5432"
)

cursor = conn.cursor()

# ---------------- GET PRODUCTS ----------------
@app.route('/products', methods=['GET'])
def get_products():
    cursor.execute("SELECT * FROM Products")
    rows = cursor.fetchall()

    products = []
    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": float(row[2])
        })

    return jsonify(products)

# ---------------- ADD PRODUCT ----------------
@app.route('/products', methods=['POST'])
def add_product():
    data = request.json

    cursor.execute(
    "INSERT INTO Products (Name, Price) VALUES (%s, %s)",
    (name, price)
    )
    conn.commit()

    return jsonify({"message": "Product added"})

# ---------------- UPDATE PRODUCT ----------------
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.json

    cursor.execute(
    "UPDATE Products SET Name=%s, Price=%s WHERE Id=%s",
    (name, price, id)
    )
    conn.commit()

    return jsonify({"message": "Updated"})

# ---------------- DELETE PRODUCT ----------------
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    cursor.execute(
    "DELETE FROM Products WHERE Id=%s",
    (id,)
    )
    conn.commit()

    return jsonify({"message": "Deleted"})

# ---------------- SAVE BILL (WITH GST) ----------------
@app.route('/save-bill', methods=['POST'])
def save_bill():
    data = request.json
    items = data.get('items')

    subtotal = 0

    # CALCULATE SUBTOTAL
    for item in items:
        subtotal += item['qty'] * item['price']

    # GST CALCULATION
    gst_percent = 5
    gst_amount = (subtotal * gst_percent) / 100
    final_total = subtotal + gst_amount

    try:
        # INSERT BILL
        cursor.execute(
            "INSERT INTO Bills (TotalAmount) OUTPUT INSERTED.BillId VALUES (?)",
            final_total
        )
        bill_id = cursor.fetchone()[0]

        # INSERT ITEMS
        for item in items:
            cursor.execute(
                "INSERT INTO BillItems (BillId, ProductId, Quantity, Price) VALUES (?, ?, ?, ?)",
                bill_id,
                item['productId'],
                item['qty'],
                item['price']
            )

        conn.commit()

        return jsonify({
            "message": "Bill Saved",
            "billId": bill_id,
            "subtotal": subtotal,
            "gst": gst_amount,
            "total": final_total
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"message": "Error saving bill"}), 500

# ---------------- DASHBOARD: TOTAL SALES ----------------
@app.route('/dashboard/total-sales', methods=['GET'])
def total_sales():
    cursor.execute("SELECT ISNULL(SUM(TotalAmount), 0) FROM Bills")
    result = cursor.fetchone()[0]

    return jsonify({"totalSales": float(result)})

# ---------------- DASHBOARD: TODAY SALES ----------------
@app.route('/dashboard/today-sales', methods=['GET'])
def today_sales():
    cursor.execute("""
        SELECT ISNULL(SUM(TotalAmount), 0)
        FROM Bills
        WHERE CONVERT(DATE, BillDate) = CONVERT(DATE, GETDATE())
    """)
    result = cursor.fetchone()[0]

    return jsonify({"todaySales": float(result)})

# ---------------- DASHBOARD: TOP PRODUCT ----------------
@app.route('/dashboard/top-product', methods=['GET'])
def top_product():
    cursor.execute("""
        SELECT TOP 1 P.Name, SUM(BI.Quantity) AS TotalQty
        FROM BillItems BI
        JOIN Products P ON BI.ProductId = P.Id
        GROUP BY P.Name
        ORDER BY TotalQty DESC
    """)

    row = cursor.fetchone()

    if row:
        return jsonify({
            "product": row[0],
            "quantity": row[1]
        })

    return jsonify({"product": "-", "quantity": 0})

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)