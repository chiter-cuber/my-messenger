from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_NAME = 'chat.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            text TEXT NOT NULL,
            chat_id TEXT NOT NULL,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/messages')
def get_messages():
    chat_id = request.args.get('chat_id', 'general')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT username, text FROM messages WHERE chat_id=? ORDER BY ts LIMIT 50', (chat_id,))
    rows = c.fetchall()
    conn.close()
    return jsonify([{"username": r[0], "text": r[1]} for r in rows])

@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    user = data.get('username', 'Unknown')
    text = data.get('text', '')
    chat = data.get('chat_id', 'general')

    if not text.strip():
        return jsonify({"status": "error", "msg": "Пустое сообщение"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO messages (username, text, chat_id) VALUES (?, ?, ?)', (user, text, chat))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
