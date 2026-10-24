import json
from dotenv import load_dotenv
from openai import OpenAI
from tools import chercher_produit

load_dotenv()
client = OpenAI()

# La fiche de l'outil chercher_produit
outils = [
    {
        "type": "function",
        "function": {
            "name": "chercher_produit",
            "description": "Cherche les produits de la boutique ShopNova dont le nom contient un mot.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recherche": {
                        "type": "string",
                        "description": "Le mot à chercher, par exemple 'casque' ou 'souris'."
                    }
                },
                "required": ["recherche"]
            }
        }
    }
]

messages = [
    {"role": "system", "content": "Tu es l'assistant de ShopNova. Utilise tes outils pour répondre, n'invente rien."},
    {"role": "user", "content": "Avez-vous des casques ?"}
]

# 1er appel : le LLM décide s'il a besoin d'un outil
reponse = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=outils
)
message_ia = reponse.choices[0].message

# Le LLM a-t-il demandé un outil ?
if message_ia.tool_calls:
    appel = message_ia.tool_calls[0]
    arguments = json.loads(appel.function.arguments)
    print(f"🛠️ L'agent appelle {appel.function.name} avec {arguments}")

    # On exécute VRAIMENT la fonction Python
    resultat = chercher_produit(arguments["recherche"])

    # On ajoute à l'historique : la demande du LLM + le résultat de l'outil
    messages.append(message_ia)
    messages.append({
        "role": "tool",
        "tool_call_id": appel.id,
        "content": json.dumps(resultat, ensure_ascii=False)
    })

    # 2e appel : le LLM répond avec les vraies données
    reponse = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=outils
    )

print(f"ShopNova : {reponse.choices[0].message.content}")