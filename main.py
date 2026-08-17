import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
from decimal import Decimal

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "SanjuSD@1861",
    "database": "ecommerce_food"
}

def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print("\nDatabase connection error:", e)
        print("Check MySQL is running and update DB_CONFIG in main.py.")
        return None

def execute_query(query, params=None, fetch=False):
    con = get_connection()
    if not con:
        return None
    cur = con.cursor(dictionary=True)
    try:
        cur.execute(query, params or ())
        if fetch:
            return cur.fetchall()
        con.commit()
        return cur.lastrowid
    except Error as e:
        con.rollback()
        print("Database error:", e)
        return None
    finally:
        cur.close()
        con.close()

def execute_update(query, params=None):
    con = get_connection()
    if not con:
        return False
    cur = con.cursor()
    try:
        cur.execute(query, params or ())
        con.commit()
        return True
    except Error as e:
        con.rollback()
        print("Database error:", e)
        return False
    finally:
        cur.close()
        con.close()

def pause():
    input("\nPress Enter to continue...")

def read_int(prompt, minimum=None):
    while True:
        try:
            x = int(input(prompt))
            if minimum is not None and x < minimum:
                print(f"Enter a value >= {minimum}.")
                continue
            return x
        except ValueError:
            print("Enter a valid integer.")

def read_float(prompt, minimum=None):
    while True:
        try:
            x = float(input(prompt))
            if minimum is not None and x < minimum:
                print(f"Enter a value >= {minimum}.")
                continue
            return x
        except ValueError:
            print("Enter a valid number.")

def money(x):
    return f"Rs.{float(x):,.2f}"

# ---------------- ADMIN ----------------

def admin_login():
    print("\n" + "=" * 70)
    print("ADMIN LOGIN")
    print("=" * 70)
    email = input("Admin Email: ").strip()
    password = input("Password: ").strip()
    rows = execute_query(
        "SELECT id,name FROM users WHERE email=%s AND password=%s AND role='admin'",
        (email, password), True)
    if rows:
        print("Welcome Admin,", rows[0]["name"])
        admin_menu()
    else:
        print("Invalid admin credentials.")
        pause()

def admin_menu():
    while True:
        print("\n" + "=" * 70)
        print("ADMIN MENU")
        print("=" * 70)
        print("1. Add Product")
        print("2. View Products")
        print("3. Update Product")
        print("4. Delete Product")
        print("5. View Users")
        print("6. View User Orders")
        print("7. Update Order Status")
        print("8. Sales Forecasting")
        print("9. Logout")
        c = input("Enter choice: ").strip()
        if c == "1": add_product()
        elif c == "2": view_products()
        elif c == "3": update_product()
        elif c == "4": delete_product()
        elif c == "5": view_users()
        elif c == "6": view_all_orders()
        elif c == "7": update_order_status()
        elif c == "8": forecasting_menu()
        elif c == "9": break
        else: print("Invalid choice.")

def add_product():
    name = input("Product name: ").strip()
    category = input("Category: ").strip()
    desc = input("Description: ").strip()
    price = read_float("Price: ", 0)
    stock = read_int("Stock: ", 0)
    r = execute_query(
        "INSERT INTO products(name,category,description,price,stock) VALUES(%s,%s,%s,%s,%s)",
        (name,category,desc,price,stock))
    print("Product added." if r is not None else "Failed.")
    pause()

def view_products():
    rows = execute_query(
        "SELECT id,name,category,price,stock FROM products ORDER BY id", fetch=True)
    print("\n" + "=" * 80)
    print("PRODUCTS")
    print("=" * 80)
    if not rows:
        print("No products.")
    else:
        print(f"{'ID':<5}{'Product':<28}{'Category':<18}{'Price':>12}{'Stock':>10}")
        print("-" * 80)
        for r in rows:
            print(f"{r['id']:<5}{r['name'][:27]:<28}{r['category'][:17]:<18}{money(r['price']):>12}{r['stock']:>10}")
    pause()

def update_product():
    rows = execute_query("SELECT id,name,price,stock FROM products ORDER BY id", fetch=True)
    if not rows:
        print("No products."); pause(); return
    for r in rows:
        print(f"{r['id']}. {r['name']} | {money(r['price'])} | Stock {r['stock']}")
    pid = read_int("Product ID: ", 1)
    old = execute_query("SELECT * FROM products WHERE id=%s", (pid,), True)
    if not old:
        print("Product not found."); pause(); return
    o = old[0]
    name = input(f"Name [{o['name']}]: ").strip() or o["name"]
    cat = input(f"Category [{o['category']}]: ").strip() or o["category"]
    desc = input(f"Description [{o['description']}]: ").strip() or o["description"]
    pi = input(f"Price [{o['price']}]: ").strip()
    si = input(f"Stock [{o['stock']}]: ").strip()
    try:
        price = float(pi) if pi else float(o["price"])
        stock = int(si) if si else int(o["stock"])
    except ValueError:
        print("Invalid value."); pause(); return
    ok = execute_update(
        "UPDATE products SET name=%s,category=%s,description=%s,price=%s,stock=%s WHERE id=%s",
        (name,cat,desc,price,stock,pid))
    print("Updated." if ok else "Update failed."); pause()

def delete_product():
    pid = read_int("Product ID: ", 1)
    row = execute_query("SELECT name FROM products WHERE id=%s", (pid,), True)
    if not row:
        print("Product not found."); pause(); return
    if input(f"Delete {row[0]['name']}? (Y/N): ").upper() != "Y":
        return
    ok = execute_update("DELETE FROM products WHERE id=%s", (pid,))
    print("Deleted." if ok else "Delete failed."); pause()

def view_users():
    rows = execute_query(
        "SELECT id, name, email, role, created_at FROM users ORDER BY id",
        fetch=True
    )
    print("\n" + "=" * 90)
    print("USERS")
    print("=" * 90)
    if not rows:
        print("No users found.")
        pause()
        return
    print(f"{'ID':<5}{'Name':<20}{'Email':<30}{'Role':<10}{'Created At'}")
    print("-" * 90)
    for r in rows:
        created = r["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"{r['id']:<5}"
            f"{r['name'][:19]:<20}"
            f"{r['email'][:29]:<30}"
            f"{r['role']:<10}"
            f"{created}"
        )
    print("=" * 90)
    pause()
    
def view_all_orders():
    rows = execute_query("""
        SELECT o.id,u.name user_name,u.email,o.total_amount,o.status,o.created_at
        FROM orders o JOIN users u ON o.user_id=u.id ORDER BY o.id DESC
    """, fetch=True)
    print("\nALL ORDERS")
    if not rows: print("No orders.")
    for r in rows or []:
        print(f"Order {r['id']} | {r['user_name']} | {money(r['total_amount'])} | {r['status']} | {r['created_at']}")
    pause()

def update_order_status():
    oid = read_int("Order ID: ", 1)
    row = execute_query("SELECT id FROM orders WHERE id=%s", (oid,), True)
    if not row:
        print("Order not found."); pause(); return
    statuses = ["Placed","Confirmed","Packed","Shipped","Delivered","Cancelled"]
    for i,s in enumerate(statuses,1): print(i,s)
    c = read_int("Choose status: ",1)
    if c > len(statuses): print("Invalid."); pause(); return
    ok = execute_update("UPDATE orders SET status=%s WHERE id=%s", (statuses[c-1],oid))
    print("Status updated." if ok else "Failed."); pause()

# ---------------- USER ----------------

def user_register():
    print("\nUSER REGISTRATION")
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    if not name or not email or not password:
        print("All fields required."); pause(); return
    if execute_query("SELECT id FROM users WHERE email=%s",(email,),True):
        print("Email already registered."); pause(); return
    r = execute_query(
        "INSERT INTO users(name,email,password,role) VALUES(%s,%s,%s,'user')",
        (name,email,password))
    print("Registration successful." if r is not None else "Registration failed.")
    pause()

def user_login():
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    rows = execute_query(
        "SELECT id,name FROM users WHERE email=%s AND password=%s AND role='user'",
        (email,password), True)
    if rows:
        user_menu(rows[0]["id"], rows[0]["name"])
    else:
        print("Invalid credentials."); pause()

def user_menu(uid,name):
    while True:
        print("\n" + "="*70)
        print("USER MENU -",name)
        print("="*70)
        print("1. View Products")
        print("2. Add Product to Cart")
        print("3. View Cart")
        print("4. Update Cart")
        print("5. Remove Product from Cart")
        print("6. Place Order")
        print("7. Track Order")
        print("8. View Order History")
        print("9. Logout")
        c=input("Enter choice: ").strip()
        if c=="1": view_products()
        elif c=="2": add_to_cart(uid)
        elif c=="3": view_cart(uid)
        elif c=="4": update_cart(uid)
        elif c=="5": remove_cart(uid)
        elif c=="6": place_order(uid)
        elif c=="7": track_order(uid)
        elif c=="8": order_history(uid)
        elif c=="9": break
        else: print("Invalid choice.")

def cart_rows(uid):
    return execute_query("""
        SELECT c.id,c.product_id,p.name,p.price,c.quantity,
               p.price*c.quantity subtotal,p.stock
        FROM cart c JOIN products p ON c.product_id=p.id
        WHERE c.user_id=%s ORDER BY c.id
    """,(uid,),True)

def add_to_cart(uid):
    view_products()
    pid=read_int("Product ID: ",1)
    qty=read_int("Quantity: ",1)
    p=execute_query("SELECT stock FROM products WHERE id=%s",(pid,),True)
    if not p: print("Product not found."); pause(); return
    old=execute_query("SELECT quantity FROM cart WHERE user_id=%s AND product_id=%s",(uid,pid),True)
    newqty=qty+(old[0]["quantity"] if old else 0)
    if newqty>p[0]["stock"]: print("Insufficient stock."); pause(); return
    if old:
        ok=execute_update("UPDATE cart SET quantity=%s WHERE user_id=%s AND product_id=%s",(newqty,uid,pid))
    else:
        ok=execute_update("INSERT INTO cart(user_id,product_id,quantity) VALUES(%s,%s,%s)",(uid,pid,qty))
    print("Added to cart." if ok else "Failed."); pause()

def view_cart(uid):
    rows=cart_rows(uid)
    print("\nMY CART")
    if not rows: print("Cart is empty."); pause(); return
    total=0
    for r in rows:
        total += float(r["subtotal"])
        print(f"Cart {r['id']} | {r['name']} | Qty {r['quantity']} | {money(r['subtotal'])}")
    print("Total:",money(total)); pause()

def update_cart(uid):
    rows=cart_rows(uid)
    if not rows: print("Cart empty."); pause(); return
    for r in rows: print(f"Cart {r['id']} | {r['name']} | Qty {r['quantity']} | Stock {r['stock']}")
    cid=read_int("Cart ID: ",1); qty=read_int("New quantity: ",1)
    item=execute_query("SELECT product_id FROM cart WHERE id=%s AND user_id=%s",(cid,uid),True)
    if not item: print("Cart item not found."); pause(); return
    stock=execute_query("SELECT stock FROM products WHERE id=%s",(item[0]["product_id"],),True)[0]["stock"]
    if qty>stock: print("Quantity exceeds stock."); pause(); return
    ok=execute_update("UPDATE cart SET quantity=%s WHERE id=%s AND user_id=%s",(qty,cid,uid))
    print("Updated." if ok else "Failed."); pause()

def remove_cart(uid):
    rows=cart_rows(uid)
    if not rows: print("Cart empty."); pause(); return
    for r in rows: print(f"{r['id']}. {r['name']}")
    cid=read_int("Cart ID: ",1)
    ok=execute_update("DELETE FROM cart WHERE id=%s AND user_id=%s",(cid,uid))
    print("Removed." if ok else "Failed."); pause()

def place_order(uid):
    rows=cart_rows(uid)
    if not rows: print("Cart empty."); pause(); return
    total=sum(float(r["subtotal"]) for r in rows)
    print("Total:",money(total))
    if input("Confirm? (Y/N): ").upper()!="Y": return
    con=get_connection()
    if not con: pause(); return
    cur=con.cursor()
    try:
        for r in rows:
            cur.execute("SELECT stock FROM products WHERE id=%s FOR UPDATE",(r["product_id"],))
            if cur.fetchone()[0] < r["quantity"]:
                raise Exception("Insufficient stock for "+r["name"])
        cur.execute("INSERT INTO orders(user_id,total_amount,status) VALUES(%s,%s,'Placed')",(uid,total))
        oid=cur.lastrowid
        for r in rows:
            cur.execute("INSERT INTO order_items(order_id,product_id,quantity,price) VALUES(%s,%s,%s,%s)",
                        (oid,r["product_id"],r["quantity"],r["price"]))
            cur.execute("UPDATE products SET stock=stock-%s WHERE id=%s",(r["quantity"],r["product_id"]))
        cur.execute("DELETE FROM cart WHERE user_id=%s",(uid,))
        current_month=date.today().replace(day=1)
        cur.execute("""
            INSERT INTO sales_history(sale_month,total_sales) VALUES(%s,%s)
            ON DUPLICATE KEY UPDATE total_sales=total_sales+VALUES(total_sales)
        """,(current_month,total))
        con.commit()
        print("Order placed! Order ID:",oid)
    except Exception as e:
        con.rollback(); print("Order failed:",e)
    finally:
        cur.close(); con.close()
    pause()

def track_order(uid):
    oid=read_int("Order ID: ",1)
    rows=execute_query("SELECT id,total_amount,status,created_at FROM orders WHERE id=%s AND user_id=%s",(oid,uid),True)
    if not rows: print("Order not found."); pause(); return
    print(rows[0]); pause()

def order_history(uid):
    rows=execute_query("SELECT id,total_amount,status,created_at FROM orders WHERE user_id=%s ORDER BY id DESC",(uid,),True)
    print("\nORDER HISTORY")
    for r in rows or []:
        print(f"Order {r['id']} | {money(r['total_amount'])} | {r['status']} | {r['created_at']}")
    pause()

# ---------------- FORECASTING ----------------

def forecasting_menu():
    while True:
        print("\nSALES FORECASTING")
        print("1. View Historical Sales")
        print("2. Add / Update Historical Sales")
        print("3. Generate 12-Month Forecast")
        print("4. Back")
        c=input("Enter choice: ").strip()
        if c=="1": view_sales_history()
        elif c=="2": add_sales()
        elif c=="3": generate_forecast()
        elif c=="4": break
        else: print("Invalid choice.")

def view_sales_history():
    rows=execute_query("SELECT sale_month,total_sales FROM sales_history ORDER BY sale_month",fetch=True)
    print("\nHISTORICAL SALES")
    for r in rows or []: print(r["sale_month"],"->",money(r["total_sales"]))
    pause()

def add_sales():
    text=input("Month (YYYY-MM-01): ").strip()
    try:
        d=datetime.strptime(text,"%Y-%m-%d").date()
        if d.day!=1: raise ValueError
    except ValueError:
        print("Use format YYYY-MM-01."); pause(); return
    sales=read_float("Total sales: ",0)
    con=get_connection()
    if not con: pause(); return
    cur=con.cursor()
    try:
        cur.execute("""
            INSERT INTO sales_history(sale_month,total_sales) VALUES(%s,%s)
            ON DUPLICATE KEY UPDATE total_sales=VALUES(total_sales)
        """,(d,sales))
        con.commit(); print("Sales saved.")
    except Error as e:
        con.rollback(); print("Database error:",e)
    finally:
        cur.close(); con.close()
    pause()

def average(values):
    return sum(values)/len(values) if values else 0

def next_month(d):
    if d.month==12:
        return date(d.year+1,1,1)
    return date(d.year,d.month+1,1)

def generate_forecast():
    rows=execute_query("SELECT sale_month,total_sales FROM sales_history ORDER BY sale_month",fetch=True)
    if not rows or len(rows)<3:
        print("At least 3 months of sales data are required."); pause(); return

    sales=[float(r["total_sales"]) for r in rows]
    growth=[]
    for i in range(1,len(sales)):
        if sales[i-1] != 0:
            g=(sales[i]-sales[i-1])/sales[i-1]*100
            if -50 <= g <= 50:
                growth.append(g)

    avg_growth=average(growth)
    recent=average(sales[-3:])
    forecast=sales[-1]*0.6+recent*0.4
    month=rows[-1]["sale_month"]
    total=0

    print("\n" + "="*75)
    print("12-MONTH SALES FORECAST")
    print("="*75)
    print("Historical records:",len(rows))
    print("Latest actual:",money(sales[-1]))
    print("Recent 3-month average:",money(recent))
    print(f"Average monthly growth: {avg_growth:.2f}%")
    print("\nMethod: recent sales average + historical average growth")
    print("-"*75)

    for i in range(12):
        month=next_month(month)
        forecast=max(0,forecast*(1+avg_growth/100))
        total+=forecast
        print(f"{month} -> {money(forecast)}")

    print("-"*75)
    print("Expected next 12-month sales:",money(total))
    print("="*75)
    print("This is a simple statistical forecast. It uses only Python calculations and MySQL data.")
    pause()

# ---------------- MAIN ----------------

def main():
    while True:
        print("\n" + "="*70)
        print("E-COMMERCE FOOD PRODUCTS SALES FORECASTING SYSTEM")
        print("="*70)
        print("1. Admin Login")
        print("2. User Registration")
        print("3. User Login")
        print("4. View Products")
        print("5. Exit")
        c=input("Enter choice: ").strip()
        if c=="1": admin_login()
        elif c=="2": user_register()
        elif c=="3": user_login()
        elif c=="4": view_products()
        elif c=="5":
            print("Thank you.")
            break
        else: print("Invalid choice.")

if __name__=="__main__":
    main()
