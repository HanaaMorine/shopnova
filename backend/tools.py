import json


with open("data/catalogue.json", "r", encoding="utf-8") as fichier:
    catalogue = json.load(fichier)
with open("data/commandes.json","r",encoding="utf-8") as fichier:
    commandes=json.load(fichier)

def chercher_produit(recherche):
    resultats = []
    for produit in catalogue:
        if recherche.lower() in produit["nom"].lower():
            resultats.append(produit)
    return resultats


print(chercher_produit("casque"))

def suivre_commande(numero):
    for commande in commandes:
            if commande["numero"].upper() == numero.upper():  
                return commande
    return None

print(suivre_commande("CMD1003"))
print(suivre_commande("cmd1003"))
print(suivre_commande("CMD9999"))



def recommander(categorie,budget_max):
     resultats=[]
     for produit in catalogue:
          if produit["categorie"].lower()==categorie.lower()  and produit["prix"]<=budget_max and produit["stock"]>0:
                resultats.append(produit)
     return resultats

print(recommander("Audio", 40))
print(recommander("gaming", 30))
print(recommander("Maison", 5))