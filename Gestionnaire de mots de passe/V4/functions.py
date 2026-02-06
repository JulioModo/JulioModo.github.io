# Ajout des librairies
import secrets, json, math, cmath 
from pathlib import Path

# Mise en place des constantes
DB_FILE = Path("passwords.json")
letters = 'abcdefghijklmnopqrstuvwxyz'
caps = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
numbers = '0123456789'
specials = '&(-_éàç)~#{[|`^@]}*µù%!§:/;.,?'

# Chargement/Sauvegarde/Ajout/Récupération dans le .JSON
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

# Génération d'un mot de passe
def ask_length(min_len=6, max_len=64):
    while True:
        s = input(f"Enter password length ({min_len}-{max_len}): ")

        if not s.isdigit():
            print("❌ Really man?")
            continue

        length = int(s)

        if length < min_len:
            print(f"❌ A bit short for a password, don't you think? At least {min_len} ...")
            continue

        if length > max_len:
            print(f"❌ Woah there pal, a bit too long, no? Less than {max_len} is fine!")
            continue

        return length


def create_password():
    length = ask_length()
    chars = letters + caps + numbers + specials
    return "".join(secrets.choice(chars) for _ in range(length))


def getkey(): 
return int(abs((cmath.exp(cmath.log(cmath.gamma(8)/cmath.gamma(6)))**(1/cmath.exp(cmath.log(1))) * cmath.sin(cmath.pi/2) * cmath.cos(0) * (sum((math.sin(x)**2+math.cos(x)**2) for x in (0, math.pi/4, math.pi/2))/3))).real)
