from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# DATABASE CONNECTION
conn = psycopg2.connect(os.environ.get("postgresql://postgres:suganbvss%40%402003@db.gypxuaxzlxmpecvitxja.supabase.co:5432/postgres"), 
                        sslmode='require'
)
cursor = conn.cursor()

# GET PRODUCTS
@app.route('/products', methods=['GET'])
def get_products():
    cursor.execute("SELECT * FROM Products")
    rows = cursor.fetchall()
    products = [{"id": r[0], "name": r[1], "price": float(r[2])} for r in rows]
    return jsonify(products)

# ADD PRODUCT
@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    cursor.execute("INSERT INTO Products (Name, Price) VALUES (%s, %s)", (data['name'], data['price']))
    conn.commit()
    return jsonify({"message": "Product added"})

# UPDATE PRODUCT
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.json
    cursor.execute("UPDATE Products SET Name=%s, Price=%s WHERE Id=%s", (data['name'], data['price'], id))
    conn.commit()
    return jsonify({"message": "Updated"})

# DELETE PRODUCT
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    cursor.execute("DELETE FROM Products WHERE Id=%s", (id,))
    conn.commit()
    return jsonify({"message": "Deleted"})

# SAVE BILL
@app.route('/save-bill', methods=['POST'])
def save_bill():
    data = request.json
    items = data.get('items')
    subtotal = sum(i['qty'] * i['price'] for i in items)
    gst_amount = (subtotal * 5) / 100
    final_total = subtotal + gst_amount

    try:
        cursor.execute("INSERT INTO Bills (TotalAmount) VALUES (%s) RETURNING BillId", (final_total,))
        bill_id = cursor.fetchone()[0]
        for item in items:
            cursor.execute(
                "INSERT INTO BillItems (BillId, ProductId, Quantity, Price) VALUES (%s, %s, %s, %s)",
                (bill_id, item['productId'], item['qty'], item['price'])
            )
        conn.commit()
        return jsonify({"message": "Bill Saved", "billId": bill_id, "total": final_total})
    except Exception as e:
        conn.rollback()
        print("ERROR:", e)
        return jsonify({"message": "Error saving bill"}), 500

# DASHBOARD - TOTAL SALES
@app.route('/dashboard/total-sales', methods=['GET'])
def total_sales():
    cursor.execute("SELECT COALESCE(SUM(TotalAmount), 0) FROM Bills")
    result = cursor.fetchone()[0]
    return jsonify({"totalSales": float(result)})

# DASHBOARD - TODAY SALES
@app.route('/dashboard/today-sales', methods=['GET'])
def today_sales():
    cursor.execute("SELECT COALESCE(SUM(TotalAmount), 0) FROM Bills WHERE DATE(BillDate) = CURRENT_DATE")
    result = cursor.fetchone()[0]
    return jsonify({"todaySales": float(result)})

# DASHBOARD - TOP PRODUCT
@app.route('/dashboard/top-product', methods=['GET'])
def top_product():
    cursor.execute("""
        SELECT P.Name, SUM(BI.Quantity) AS TotalQty
        FROM BillItems BI
        JOIN Products P ON BI.ProductId = P.Id
        GROUP BY P.Name
        ORDER BY TotalQty DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    if row:
        return jsonify({"product": row[0], "quantity": row[1]})
    return jsonify({"product": "-", "quantity": 0})

if __name__ == '__main__':
    app.run(debug=True)