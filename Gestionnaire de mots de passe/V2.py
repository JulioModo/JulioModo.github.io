import json
from pathlib import Path

DB_FILE = Path('local_db.json')

def load_db():
    if not DB_FILE.exists:
        return {}
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(db: dict):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

def add_entry(service, username, encrypted_password):
    db = load_db()
    db[service] = {
        'username': username,
        'password': encrypted_password
    }
    save_db(db)

def get_entry(service):
    db = load_db()
    return db.get(service)
