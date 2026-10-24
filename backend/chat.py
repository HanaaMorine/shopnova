from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()  # lit le fichier .env où existe ma clé API
client = OpenAI()  # crée la connexion à OpenAI

messages = [
    {"role": "system", "content": "Tu es l'assistant de la boutique en ligne ShopNova. "
                                  "Tu réponds en français, poliment et en 2 phrases maximum. "
                                  "N'invente jamais d'information sur la boutique."}  # prompt système 🆕 règle anti-hallucination
]
# 🆕 plus de question écrite à la main : c'est le client qui écrit

while True:  # 🆕 on discute en boucle
    question = input("Vous : ")  # 🆕 le client écrit sa question
    if question.lower() == "quitter":  # 🆕 pour arrêter
        break

    messages.append({"role": "user", "content": question})  # 🆕 on ajoute la question à l'historique

    messages_a_envoyer = [messages[0]] + messages[-10:]  # 🆕 prompt système + 10 derniers messages

    reponse = client.chat.completions.create(  # on envoie la demande
        model="gpt-4o-mini",
        messages=messages_a_envoyer
    )
    texte = reponse.choices[0].message.content  # 🆕 on garde le texte dans une variable

    print(f"ShopNova : {texte}")  # on affiche la réponse
    messages.append({"role": "assistant", "content": texte})  # 🆕 on ajoute la réponse à l'historique (mémoire)