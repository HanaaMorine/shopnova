import json


with open("data/catalogue.json", "r", encoding="utf-8") as fichier:
    catalogue = json.load(fichier)


def chercher_produit(recherche):
    resultats = []
    for produit in catalogue:
        if recherche.lower() in produit["nom"].lower():
            resultats.append(produit)
    return resultats


print(chercher_produit("casque"))