from dotenv import load_dotenv
from openai import OpenAI

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

reponse = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=outils
)

print(reponse.choices[0].message)