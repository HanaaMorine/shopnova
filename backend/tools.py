import json
from datetime import date


# ---------- Chargement des données ----------
with open("data/catalogue.json", "r", encoding="utf-8") as fichier:
    catalogue = json.load(fichier)

with open("data/commandes.json", "r", encoding="utf-8") as fichier:
    commandes = json.load(fichier)

retours = []


# ---------- Outil 1 ----------
def chercher_produit(recherche):
    resultats = []
    for produit in catalogue:
        if recherche.lower() in produit["nom"].lower():
            resultats.append(produit)
    return resultats


# ---------- Outil 2 ----------
def suivre_commande(numero):
    for commande in commandes:
        if commande["numero"].upper() == numero.upper():
            return commande
    return None


# ---------- Outil 3 ----------
def recommander(categorie, budget_max):
    resultats = []
    for produit in catalogue:
        if produit["categorie"].lower() == categorie.lower() and produit["prix"] <= budget_max and produit["stock"] > 0:
            resultats.append(produit)
    return resultats


# ---------- Outil 4 ----------
def creer_retour(numero, motif):
    commande = suivre_commande(numero)
    if commande == None:
        return {"erreur": "Commande introuvable."}
    if commande["statut"] != "livrée":
        return {"erreur": f"Retour impossible : la commande est {commande['statut']}."}
    retour = {
        "numero_commande": numero,
        "motif": motif,
        "date_demande": date.today().isoformat(),
        "statut": "en attente"
    }
    retours.append(retour)
    return retour


# ---------- Tests ----------
print(chercher_produit("casque"))

print(suivre_commande("CMD1003"))
print(suivre_commande("cmd1003"))
print(suivre_commande("CMD9999"))

print(recommander("Audio", 40))
print(recommander("gaming", 30))
print(recommander("Maison", 5))

print(creer_retour("CMD1001", "Le son grésille"))
print(creer_retour("CMD1003", "Je ne le veux plus"))
print(creer_retour("CMD9999", "Test"))