import json
from dotenv import load_dotenv
from openai import OpenAI
from tools import chercher_produit, suivre_commande, recommander, creer_retour
from rag import chercher_dans_documents          # 🆕 on importe la recherche RAG

load_dotenv()
client = OpenAI()
MODELE = "gpt-4o-mini"


# ===== 1. Les fiches des outils (pour que le LLM sache quoi utiliser) =====
outils = [
    {
        "type": "function",
        "function": {
            "name": "chercher_produit",
            "description": "Cherche les produits de ShopNova dont le nom contient un mot (ex. 'casque', 'souris').",
            "parameters": {
                "type": "object",
                "properties": {
                    "recherche": {"type": "string", "description": "Le mot à chercher."}
                },
                "required": ["recherche"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suivre_commande",
            "description": "Donne le statut et les détails d'une commande à partir de son numéro (ex. 'CMD1003').",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero": {"type": "string", "description": "Le numéro de commande, ex. CMD1003."}
                },
                "required": ["numero"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recommander",
            "description": "Recommande des produits en stock d'une catégorie, sans dépasser un budget. "
                           "Catégories : Informatique, Audio, Téléphonie, Maison, Gaming.",
            "parameters": {
                "type": "object",
                "properties": {
                    "categorie": {"type": "string", "description": "La catégorie de produits."},
                    "budget_max": {"type": "number", "description": "Le budget maximum en euros."}
                },
                "required": ["categorie", "budget_max"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "creer_retour",
            "description": "Crée une demande de retour pour une commande livrée.",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero": {"type": "string", "description": "Le numéro de commande."},
                    "motif": {"type": "string", "description": "La raison du retour."}
                },
                "required": ["numero", "motif"]
            }
        }
    },
    {   # 🆕 l'outil RAG
        "type": "function",
        "function": {
            "name": "chercher_dans_documents",
            "description": "Cherche dans les documents officiels de ShopNova (politique de retour, livraison, "
                           "garantie, FAQ : paiement, annulation, contact...). À utiliser pour toute question "
                           "sur les règles, délais, frais ou conditions de la boutique.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "La question du client, reformulée clairement."}
                },
                "required": ["question"]
            }
        }
    }
]


# ===== 2. L'annuaire : nom de l'outil → fonction Python =====
fonctions = {
    "chercher_produit": chercher_produit,
    "suivre_commande": suivre_commande,
    "recommander": recommander,
    "creer_retour": creer_retour,
    "chercher_dans_documents": chercher_dans_documents,   # 🆕
}


def executer_outil(nom, arguments):
    """Exécute l'outil demandé par le LLM et renvoie le résultat (ou une erreur)."""
    if nom not in fonctions:
        return {"erreur": f"Outil inconnu : {nom}"}
    try:
        return fonctions[nom](**arguments)
    except Exception as e:
        return {"erreur": f"L'outil {nom} a échoué : {e}"}


# ===== 3. Le prompt système (les règles de l'agent) =====
messages = [
    {"role": "system", "content": (
        "Tu es l'assistant de la boutique en ligne ShopNova. "
        "Tu réponds en français, poliment et de façon concise. "
        "Règles : "
        "1. Chaque information doit venir d'un outil. N'invente jamais. "
        "2. Pour les produits et les commandes, utilise les outils produits/commandes. "
        "3. Pour les règles de la boutique (retours, livraison, garantie, paiement...), "     # 🆕
        "utilise chercher_dans_documents et indique la source (ex. 'd'après notre politique de retour'). "  # 🆕
        "4. Si un outil renvoie une erreur ou rien, explique-le simplement au client. "
        "5. Pour suivre une commande ou faire un retour, demande le numéro de commande s'il manque. "
        "6. Si la question n'a rien à voir avec la boutique, dis poliment que tu ne peux aider que pour ShopNova."
    )}
]


# ===== 4. La boucle de conversation =====
print("ShopNova : Bonjour ! Comment puis-je vous aider ? (tapez 'quitter' pour arrêter)")

while True:
    question = input("Vous : ")
    if question.lower() == "quitter":
        break
    messages.append({"role": "user", "content": question})

    # ===== 5. La boucle d'agent =====
    while True:
        reponse = client.chat.completions.create(model=MODELE, messages=messages, tools=outils)
        message_ia = reponse.choices[0].message

        # Pas d'outil demandé → c'est la réponse finale
        if not message_ia.tool_calls:
            print(f"ShopNova : {message_ia.content}")
            messages.append({"role": "assistant", "content": message_ia.content})
            break

        # Le LLM demande un ou plusieurs outils → on les exécute
        messages.append(message_ia)
        for appel in message_ia.tool_calls:
            nom = appel.function.name
            arguments = json.loads(appel.function.arguments)
            print(f"   🛠️ {nom}({arguments})")

            resultat = executer_outil(nom, arguments)

            messages.append({
                "role": "tool",
                "tool_call_id": appel.id,
                "content": json.dumps(resultat, ensure_ascii=False)
            })