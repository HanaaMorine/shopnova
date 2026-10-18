"""
database.py
Crée la base de données SQLite de ShopNova et importe les données de démonstration.

Utilisation (depuis la racine du projet) :
    python backend/database.py
"""

import json
import sqlite3
from pathlib import Path

# Chemins des fichiers, calculés à partir de l'emplacement de ce script
# (comme ça, le script marche quel que soit le dossier d'où on le lance)
DOSSIER_PROJET = Path(__file__).resolve().parent.parent
DOSSIER_DATA = DOSSIER_PROJET / "data"
CHEMIN_BASE = DOSSIER_DATA / "shopnova.db"


def get_connexion():
    """Ouvre une connexion à la base et renvoie-la."""
    connexion = sqlite3.connect(CHEMIN_BASE)
    connexion.row_factory = sqlite3.Row          # lire les lignes comme des dictionnaires
    connexion.execute("PRAGMA foreign_keys = ON")  # activer les clés étrangères
    return connexion


def creer_tables(connexion):
    """Crée les 3 tables si elles n'existent pas encore."""
    curseur = connexion.cursor()

    curseur.execute("""
    CREATE TABLE IF NOT EXISTS produits (
        id TEXT PRIMARY KEY,
        nom TEXT NOT NULL,
        categorie TEXT NOT NULL,
        prix REAL NOT NULL,
        stock INTEGER NOT NULL,
        description TEXT
    )
    """)

    curseur.execute("""
    CREATE TABLE IF NOT EXISTS commandes (
        numero TEXT PRIMARY KEY,
        client TEXT NOT NULL,
        id_produit TEXT NOT NULL,
        quantite INTEGER NOT NULL,
        date_commande TEXT NOT NULL,
        statut TEXT NOT NULL,
        date_livraison TEXT,
        ville TEXT,
        FOREIGN KEY (id_produit) REFERENCES produits(id)
    )
    """)

    curseur.execute("""
    CREATE TABLE IF NOT EXISTS retours (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_commande TEXT NOT NULL,
        motif TEXT NOT NULL,
        date_demande TEXT NOT NULL,
        statut TEXT NOT NULL DEFAULT 'en attente',
        FOREIGN KEY (numero_commande) REFERENCES commandes(numero)
    )
    """)

    connexion.commit()


def lire_json(nom_fichier):
    """Lit un fichier JSON du dossier data et renvoie son contenu."""
    with open(DOSSIER_DATA / nom_fichier, "r", encoding="utf-8") as fichier:
        return json.load(fichier)


def importer_donnees(connexion):
    """Importe les produits et les commandes depuis les fichiers JSON."""
    curseur = connexion.cursor()

    # 1. Les produits (à importer en premier, car les commandes y font référence)
    produits = lire_json("catalogue.json")
    for produit in produits:
        curseur.execute(
            """INSERT OR REPLACE INTO produits (id, nom, categorie, prix, stock, description)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (produit["id"], produit["nom"], produit["categorie"],
             produit["prix"], produit["stock"], produit["description"]),
        )

    # 2. Les commandes
    commandes = lire_json("commandes.json")
    for commande in commandes:
        curseur.execute(
            """INSERT OR REPLACE INTO commandes
               (numero, client, id_produit, quantite, date_commande, statut, date_livraison, ville)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (commande["numero"], commande["client"], commande["id_produit"],
             commande["quantite"], commande["date_commande"], commande["statut"],
             commande["date_livraison"], commande["ville"]),
        )

    connexion.commit()
    print(f"{len(produits)} produits et {len(commandes)} commandes importés.")


# Ce bloc ne s'exécute que si on lance ce fichier directement
# (pas quand un autre fichier fait "import database")
if __name__ == "__main__":
    connexion = get_connexion()
    creer_tables(connexion)
    importer_donnees(connexion)
    connexion.close()
    print(f"Base créée : {CHEMIN_BASE}")