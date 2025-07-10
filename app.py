from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import psycopg2
import os
import requests
import pandas as pd
from NewD90 import ssRNA  # Make sure NewD90.py is in the same directory

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# PostgreSQL database URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL)

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_pw))
            conn.commit()
            cur.close()
            conn.close()
            flash("Registration successful! Please login.")
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            flash("Email already exists.")
        except Exception as e:
            flash(f"Database error: {e}")
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row and check_password_hash(row[0], password):
            session['user'] = email
            flash("Login successful!")
            return redirect(url_for('analysis'))
        else:
            flash("Invalid email or password.")
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Analysis form page
@app.route('/analysis')
def analysis():
    if 'user' not in session:
        flash("Please login to access analysis.")
        return redirect(url_for('login'))
    return render_template('analysis.html')

# AJAX D90 calculation
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        if request.content_type.startswith('multipart/form-data'):
            file = request.files.get("file")
            if not file:
                return jsonify({"error": "No file uploaded"}), 400
            content = file.read().decode('utf-8').strip().splitlines()
            df = pd.DataFrame({'BaseCount': content})
            gsize = sum(len(seq.strip()) for seq in content)
            result = ssRNA(df, gsize)
            return jsonify({"result": f"{float(result.iloc[0]):.6f}"})

        elif request.is_json:
            data = request.get_json()
            url = data.get("url")
            if not url:
                return jsonify({"error": "URL is required"}), 400
            response = requests.get(url)
            response.raise_for_status()
            lines = response.text.strip().splitlines()
            df = pd.DataFrame({'BaseCount': lines})
            gsize = sum(len(seq.strip()) for seq in lines)
            result = ssRNA(df, gsize)
            return jsonify({"result": f"{float(result.iloc[0]):.6f}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"error": "Unsupported request type"}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
