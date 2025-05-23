from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for sessions

# MySQL Config
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="inventory_db3"
)
cursor = db.cursor()

@app.route('/')
def home():
    logged_in = 'user_id' in session
    return render_template('index.html', logged_in=logged_in, username=session.get('username'))

@app.route('/login_register', methods=['GET', 'POST'])
def login_register():
    if request.method == 'POST':
        if 'register' in request.form:
            # Registration logic
            username = request.form['username']
            password = request.form['password']
            hashed_password = generate_password_hash(password)

            try:
                query = "INSERT INTO users (username, password) VALUES (%s, %s)"
                cursor.execute(query, (username, hashed_password))
                db.commit()
                flash("Registration successful! Please log in.", "success")
            except mysql.connector.Error as err:
                flash("Username already exists.", "danger")

        elif 'login' in request.form:
            # Login logic
            username = request.form['username']
            password = request.form['password']

            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user[2], password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                flash("Login successful!", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid username or password.", "danger")

    return render_template('login_register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session:
        flash("You must be logged in to add a product.", "warning")
        return redirect(url_for('login_register'))

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        supplier = request.form['supplier']

        query = "INSERT INTO products (name, category, quantity, price, supplier) VALUES (%s, %s, %s, %s, %s)"
        values = (name, category, quantity, price, supplier)
        cursor.execute(query, values)
        db.commit()

        flash("Product added successfully!", "success")
        return redirect(url_for('view_inventory'))

    return render_template('add_product.html')

@app.route('/inventory')
def view_inventory():
    if 'user_id' not in session:
        flash("You must be logged in to view the inventory.", "warning")
        return redirect(url_for('login_register'))

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template('view_inventory.html', products=products)

@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    if 'user_id' not in session:
        flash("You must be logged in to perform this action.", "warning")
        return redirect(url_for('login_register'))

    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    db.commit()
    flash("Product deleted successfully.", "success")
    return redirect(url_for('view_inventory'))

# ✅ New route for generating report
@app.route('/report')
def generate_report():
    if 'user_id' not in session:
        flash("You must be logged in to view the report.", "warning")
        return redirect(url_for('login_register'))

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template('report.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
