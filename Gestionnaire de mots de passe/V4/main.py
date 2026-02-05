# Récupération des fonctions mises dans 'functions.py' pour simplifier le code
from functions import *

# Informe l'utilisateur du chargement du .JSON
print("Chargement de la base de données et/ou création si elle est non-existante.")
try:
	load_db()
except NameError:
	print("""Erreur: Vous n'avez pas installé le second fichier néssécaire, nommé 'functions.py', l'avez vous peut être installé au mauvais endroit? Dans tous les cas, vérifiez que ce script est bel et bien dans le même dossier que 'functions.py' avant de le ré-éxécuter.""")
	break

# Gestion des choix utilisateurs a travers différents menus texte
choice = int(input("""Bienvenue sur votre gestionnaire de mot de passe! Que souhaitez vous faire?
1 - Ajouter un mot de passe
2 - Consulter un mot de passe
3 - Modifier un mot de passe
4 - Supprimer un mot de passe
(Répondez par 1, 2, 3 ou 4!)"""))
if choice == 1:
    new_password = int(input("""Avez vous déja un mot de passe pour ce site?
    1 - Oui
    2 - Non"""))
    website = input("""Pour quel site web enregistrez vous ce mot de passe?
	(Conseil: mettez soit l'URL (github.com) ou le nom du site (Github))""")
	username = input("""Quel est votre nom d'utilisateur sur la plateforme?""")
	if new_password == 1:
		password = input("Quel est votre mot de passe?")
	   add_entry(website, username, password)
