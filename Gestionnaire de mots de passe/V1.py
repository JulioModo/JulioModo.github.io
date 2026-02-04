# Import des bibliothèques
import secrets

# Mise en place des constantes
letters = 'abcdefghijklmnopqrstuvwxyz'
caps = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
numbers = '0123456789'
specials = '&(-_éàç)~#{[|`^@]}*µù%!§:/;.,?'

# Demande de la longueur du mot de passe
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

# Création du mot de passe avec ask_length()
def create_password():
    length = ask_length()
    chars = letters + caps + numbers + specials
    return "".join(secrets.choice(chars) for _ in range(length))
  
