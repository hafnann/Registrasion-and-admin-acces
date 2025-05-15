from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')

    # Logins table
    c.execute('''
        CREATE TABLE IF NOT EXISTS logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Route for registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['user']
        password = request.form['pass']
        email = request.form['eml']

        # Store the data in SQLite database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', 
                  (username, password, email))
        conn.commit()
        conn.close()
        
        return redirect(url_for('success'))
    
    return render_template('register.html')

# Success page after registration
@app.route('/success')
def success():
    return "Registration successful! <a href='/login'>Go to Login</a>"

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username and password match the database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()  # Fetch one user if found

        if user:
            # Log the login time
            c.execute('INSERT INTO logins (username) VALUES (?)', (username,))
            conn.commit()

            conn.close()

            # Redirect admin to admin page
            if username == 'admin':
                return redirect(url_for('admin'))

            return redirect(url_for('home'))
        else:
            conn.close()
            return render_template('login.html', error="❌ Invalid username or password. Try again!")
    
    return render_template('login.html')

# Route for home page after login
@app.route('/home')
def home():
    return "✅ Welcome to the Home Page! You are logged in."

# Route for admin to view login history
@app.route('/admin')
def admin():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT username, login_time FROM logins ORDER BY login_time DESC')
    logins = c.fetchall()
    conn.close()
    return render_template('admin.html', logins=logins)

# Run the Flask app
if __name__ == '__main__':
    init_db()  # Initialize the database when app starts
    app.run(debug=True)
