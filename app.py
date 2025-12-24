import streamlit as st
import sqlite3

# --- Database connection ---
conn = sqlite3.connect("restaurant.db")
c = conn.cursor()

# --- Create menu table ---
c.execute("""
CREATE TABLE IF NOT EXISTS menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL
)
""")
conn.commit()

# --- UI ---
st.title("🍽️ Restaurant Management App")
st.write("Add and view menu items")

# --- Add menu item ---
name = st.text_input("Menu name")
price = st.number_input("Price (yen)", min_value=0, step=10)

if st.button("Add menu item"):
    if name:
        c.execute(
            "INSERT INTO menu (name, price) VALUES (?, ?)",
            (name, price)
        )
        conn.commit()
        st.success("Menu item added!")
    else:
        st.error("Please enter a menu name")

# --- Show menu ---
st.subheader("📋 Menu List")

c.execute("SELECT * FROM menu")
menus = c.fetchall()

for menu in menus:
    st.write(f"ID: {menu[0]} | {menu[1]} - ¥{menu[2]}")
# --- Create orders table ---
c.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER,
    quantity INTEGER,
    order_time TEXT,
    FOREIGN KEY(menu_id) REFERENCES menu(id)
)
""")
conn.commit()

# --- Order section ---
st.subheader("🧾 Place Order")

# Get menu list
c.execute("SELECT id, name, price FROM menu")
menu_items = c.fetchall()

if menu_items:
    menu_dict = {f"{m[1]} (¥{m[2]})": m[0] for m in menu_items}

    selected_menu = st.selectbox("Select menu", list(menu_dict.keys()))
    quantity = st.number_input("Quantity", min_value=1, step=1)

    if st.button("Place Order"):
        c.execute(
            "INSERT INTO orders (menu_id, quantity, order_time) VALUES (?, ?, datetime('now'))",
            (menu_dict[selected_menu], quantity)
        )
        conn.commit()
        st.success("Order placed successfully!")
else:
    st.info("No menu items available")

# --- Show orders ---
st.subheader("📦 Order History")

c.execute("""
SELECT orders.id, menu.name, orders.quantity, orders.order_time
FROM orders
JOIN menu ON orders.menu_id = menu.id
""")

orders = c.fetchall()

for o in orders:
    st.write(f"Order #{o[0]} | {o[1]} x {o[2]} | {o[3]}")
# --- Daily sales summary ---
st.subheader("📊 Today's Sales Summary")

c.execute("""
SELECT
    COUNT(orders.id),
    SUM(menu.price * orders.quantity)
FROM orders
JOIN menu ON orders.menu_id = menu.id
WHERE date(orders.order_time) = date('now')
""")

result = c.fetchone()
order_count = result[0] if result[0] else 0
total_sales = result[1] if result[1] else 0

st.write(f"🧾 Total Orders: {order_count}")
st.write(f"💰 Total Sales: ¥{total_sales}")
# --- Sales chart ---
st.subheader("📈 Sales by Menu Item (Today)")

c.execute("""
SELECT menu.name, SUM(menu.price * orders.quantity) AS total_sales
FROM orders
JOIN menu ON orders.menu_id = menu.id
WHERE date(orders.order_time) = date('now')
GROUP BY menu.name
""")

data = c.fetchall()

if data:
    import pandas as pd

    df = pd.DataFrame(data, columns=["Menu", "Sales (¥)"])
    df = df.set_index("Menu")

    st.bar_chart(df)
else:
    st.info("No sales data for today")
