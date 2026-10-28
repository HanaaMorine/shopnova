import json
from datetime import date


# ---------- Chargement des données ----------
with open("data/catalogue.json", "r", encoding="utf-8") as fichier:
    catalogue = json.load(fichier)

with open("data/commandes.json", "r", encoding="utf-8") as fichier:
    commandes = json.load(fichier)

retours = []
DELAI_RETOUR_JOURS = 30
# 🆕 Un seul message, que la commande n'existe pas OU que l'email soit faux
#    (pour ne pas révéler qu'une commande existe à quelqu'un qui n'est pas le client)
MESSAGE_ACCES_REFUSE = "Aucune commande ne correspond à ce numéro et à cet email."


# ---------- Outil 1 ----------
def chercher_produit(recherche):
    resultats = []
    for produit in catalogue:
        if recherche.lower() in produit["nom"].lower():
            resultats.append(produit)
    return resultats


# ---------- Outil 2 ----------
def suivre_commande(numero, email):                      # 🆕 il faut aussi l'email
    for commande in commandes:
        if commande["numero"].upper() == numero.upper():
            # 🆕 Garde-fou : la commande appartient-elle à ce client ?
            if commande["email"].lower() == email.strip().lower():
                return commande
            return {"erreur": MESSAGE_ACCES_REFUSE}       # bon numéro, mauvais email
    return {"erreur": MESSAGE_ACCES_REFUSE}               # numéro inconnu → même message


# ---------- Outil 3 ----------
def recommander(categorie, budget_max):
    resultats = []
    for produit in catalogue:
        if produit["categorie"].lower() == categorie.lower() and produit["prix"] <= budget_max and produit["stock"] > 0:
            resultats.append(produit)
    return resultats


# ---------- Outil 4 ----------
def creer_retour(numero, email, motif):                  # 🆕 il faut aussi l'email
    commande = suivre_commande(numero, email)

    # Vérification 1 : la commande existe ET appartient au client ?
    if "erreur" in commande:                              # 🆕 suivre_commande renvoie maintenant une erreur
        return commande

    # Vérification 2 : la commande est livrée ?
    if commande["statut"] != "livrée":
        return {"erreur": f"Retour impossible : la commande est {commande['statut']}."}

    # Vérification 3 : dans les 30 jours après la livraison ?
    date_livraison = date.fromisoformat(commande["date_livraison"])
    jours_depuis_livraison = (date.today() - date_livraison).days
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
    print(suivre_commande("CMD1003", "emma.dubois@example.com"))    # ✅ bon email → la commande
    print(suivre_commande("CMD1003", "pirate@example.com"))         # ❌ mauvais email → refusé
    print(suivre_commande("CMD9999", "emma.dubois@example.com"))    # ❌ inconnue → MÊME message
    print(creer_retour("CMD1001", "camille.martin@example.com", "Le son grésille"))  # ✅
    print(creer_retour("CMD1001", "pirate@example.com", "Test"))                     # ❌