
import sqlite3
import time
from threading import Thread
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_NAME = "ledger.db"

# --- Database Setup (UNCHANGED) ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT, balance REAL, role TEXT)''')
    
    users = [
        (1, 'alice', 100.0, 'user'),
        (2, 'bob', 50.0, 'user'),
        (3, 'admin', 9999.0, 'admin'),
        (4, 'charlie', 10.0, 'user')
    ]
    
    c.executemany(
        "INSERT OR IGNORE INTO users (id, username, balance, role) VALUES (?, ?, ?, ?)",
        users
    )
    conn.commit()
    conn.close()

init_db()
# ----------------------------------


# ---------- SECURITY FIX ----------
@app.route('/search', methods=['GET'])
def search_users():
    """
    Search for a user by username.
    Usage: GET /search?q=alice
    """
    query = request.args.get('q')

    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        # PARAMETERIZED QUERY (SQL Injection fixed)
        cursor.execute(
            "SELECT id, username, role FROM users WHERE username = ?",
            (query.strip(),)
        )
        results = cursor.fetchall()
        conn.close()

        data = [{"id": r[0], "username": r[1], "role": r[2]} for r in results]
        return jsonify(data)

    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500


# ---------- BACKGROUND TRANSACTION ----------
def process_transaction_bg(user_id, amount):
    """
    Runs in background thread to avoid blocking API
    """
    time.sleep(3)  # Simulated banking core delay

    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()

    try:
        conn.execute("BEGIN")

        cursor.execute(
            "UPDATE users SET balance = balance - ? WHERE id = ?",
            (amount, user_id)
        )

        if cursor.rowcount == 0:
            raise Exception("User not found")

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Transaction failed: {e}")

    finally:
        conn.close()


# ---------- PERFORMANCE FIX ----------
@app.route('/transaction', methods=['POST'])
def process_transaction():
    """
    Deducts money from a user's balance.
    Body: {"user_id": 1, "amount": 25.0}
    """
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')

    if user_id is None or amount is None:
        return jsonify({"error": "Invalid input"}), 400

    # Start background thread
    Thread(
        target=process_transaction_bg,
        args=(user_id, amount),
        daemon=True
    ).start()

    # Immediate response (API remains responsive)
    return jsonify({"status": "processing", "deducted": amount})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
