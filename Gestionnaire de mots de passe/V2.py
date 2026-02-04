# Import des bibliothèques
import json
from pathlib import Path

# Mise en place du chemin de fichier du .JSON de stockage des mots de passe
DB_FILE = Path('local_db.json')

# Chargement du .JSON dans le code
def load_db():
    if not DB_FILE.exists:
        return {}
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Sauvegarde des modifications dans la BDD
def save_db(db: dict):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

# Ajout d'une entrée dans la BDD
def add_entry(service, username, encrypted_password):
    db = load_db()
    db[service] = {
        'username': username,
        'password': encrypted_password
    }
    save_db(db)

# Récupération d'identifiants (MDP et username) en fonction d'un site
def get_entry(service):
    db = load_db()
    return db.get(service)
