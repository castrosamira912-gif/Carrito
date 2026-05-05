from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret'


# Conexión DB
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Crear tabla + datos iniciales
def create_table():
    conn = get_db()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL
        )
    ''')

    # Evitar duplicados
    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]

    if count == 0:
        conn.execute("INSERT INTO products (name, price) VALUES ('Laptop', 1200)")
        conn.execute("INSERT INTO products (name, price) VALUES ('Mouse', 25)")
        conn.execute("INSERT INTO products (name, price) VALUES ('Teclado', 50)")

    conn.commit()


# Página principal
@app.route('/')
def index():
    conn = get_db()
    products = conn.execute('SELECT * FROM products').fetchall()
    return render_template('index.html', products=products)


# Agregar al carrito
@app.route('/add/<int:id>')
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']
    cart.append(id)
    session['cart'] = cart

    return redirect('/')


# Ver carrito
@app.route('/cart')
def cart():
    conn = get_db()
    cart_ids = session.get('cart', [])

    products = []
    total = 0

    for pid in cart_ids:
        product = conn.execute(
            'SELECT * FROM products WHERE id=?', (pid,)
        ).fetchone()

        if product:
            products.append(product)
            total += product['price']

    return render_template('cart.html', products=products, total=total)


# Eliminar producto
@app.route('/remove/<int:index>')
def remove(index):
    cart = session.get('cart', [])

    if index < len(cart):
        cart.pop(index)

    session['cart'] = cart
    return redirect('/cart')

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']

        conn = get_db()
        conn.execute(
            'INSERT INTO products (name, price) VALUES (?, ?)',
            (name, float(price))
        )
        conn.commit()

        return redirect('/')

    return render_template('add_product.html')

# Ejecutar app
if __name__ == '__main__':
    create_table() 
    app.run(debug=True)