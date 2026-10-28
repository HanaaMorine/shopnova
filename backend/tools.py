import json
from datetime import date


# ---------- Chargement des données ----------
with open("data/catalogue.json", "r", encoding="utf-8") as fichier:
    catalogue = json.load(fichier)

with open("data/commandes.json", "r", encoding="utf-8") as fichier:
    commandes = json.load(fichier)

retours = []
DELAI_RETOUR_JOURS = 30   # 🆕 la règle de la politique de retour


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

    # Vérification 1 : la commande existe ?
    if commande == None:
        return {"erreur": "Commande introuvable."}

    # Vérification 2 : la commande est livrée ?
    if commande["statut"] != "livrée":
        return {"erreur": f"Retour impossible : la commande est {commande['statut']}."}

    # 🆕 Vérification 3 (garde-fou) : le retour est demandé dans les 30 jours après la livraison ?
    date_livraison = date.fromisoformat(commande["date_livraison"])   # "2026-10-05" → une vraie date
    jours_depuis_livraison = (date.today() - date_livraison).days      # nombre de jours écoulés
    if jours_depuis_livraison > DELAI_RETOUR_JOURS:
        return {"erreur": f"Retour impossible : la commande a été livrée il y a {jours_depuis_livraison} jours "
                          f"(délai maximum : {DELAI_RETOUR_JOURS} jours)."}

    # Tout est bon : on crée la fiche de retour
    retour = {
        "numero_commande": numero,
        "motif": motif,
        "date_demande": date.today().isoformat(),
        "statut": "en attente"
    }
    retours.append(retour)
    return retour


# ---------- Tests ----------
if __name__ == "__main__":
    print(creer_retour("CMD1001", "Le son grésille"))     # ✅ livrée il y a ~23 jours → accepté
    print(creer_retour("CMD1007", "Je n'en veux plus"))    # ❌ livrée il y a ~35 jours → refusé
    print(creer_retour("CMD1003", "Je n'en veux plus"))    # ❌ pas encore livrée
    print(creer_retour("CMD9999", "Test"))                 # ❌ introuvable