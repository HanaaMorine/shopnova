from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()  # lit le fichier .env ou existe ma clé api
client=OpenAI() #crée la connexion openAI

reponse=client.chat.completions.create(  #on envoie la demande
    model="gpt-4o-mini",
    messages=[
        {"role":"user","content":"Bonjour!Explique-moi le RAG en une phrase."}
    ]

)
print(reponse.choices[0].message.content)  #on affiche le texte de la réponse