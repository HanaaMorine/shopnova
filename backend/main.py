# ===== Les imports =====
from fastapi import FastAPI                  # pour créer l'API
from pydantic import BaseModel, Field        # pour décrire la forme des données (les "formulaires")
from agent import repondre, PROMPT_SYSTEME   # notre agent et ses règles

# ===== Créer l'API =====
app = FastAPI(title="ShopNova API", description="Agent IA de support client (outils + RAG)")


# ===== Route 1 : vérifier que l'API fonctionne =====
@app.get("/health")                          # quand quelqu'un visite /health (GET = lire)...
def verifier_sante():
    return {"statut": "ok"}                  # ...on répond "ok"


# ===== Pydantic : les "formulaires" =====
class DemandeChat(BaseModel):
    """Ce que le client ENVOIE à l'API."""
    # Identifiant de la conversation : texte, obligatoire (...), pas vide (min_length=1)
    session_id: str = Field(..., min_length=1, description="Identifiant de la conversation")
    # Message du client : texte, obligatoire, entre 1 et 1000 caractères
    message: str = Field(..., min_length=1, max_length=1000, description="Le message du client")
    # → si ces règles ne sont pas respectées, FastAPI renvoie automatiquement une erreur 422


class ReponseChat(BaseModel):
    """Ce que l'API RENVOIE."""
    reponse: str                  # le texte de la réponse de l'agent
    outils_utilises: list[str]    # la liste des outils utilisés (une liste de textes)


# ===== La mémoire des conversations =====
# Un dictionnaire : session_id → la liste des messages de cette conversation
# Exemple : {"client1": [message1, message2...], "client2": [...]}
conversations = {}


# ===== Route 2 : discuter avec l'agent =====
@app.post("/chat", response_model=ReponseChat)   # POST = envoyer des données ; la réponse suit ReponseChat
def chat(demande: DemandeChat):                   # FastAPI vérifie la demande avec DemandeChat (Pydantic)
    # 1. Si c'est une nouvelle conversation, on la crée avec le prompt système
    if demande.session_id not in conversations:
        conversations[demande.session_id] = [{"role": "system", "content": PROMPT_SYSTEME}]

    # 2. On récupère l'historique de CETTE conversation
    messages = conversations[demande.session_id]

    # 3. On ajoute le message du client à l'historique
    messages.append({"role": "user", "content": demande.message})

    # 4. L'agent répond (avec ses outils et son RAG, comme dans le terminal)
    texte, outils_utilises = repondre(messages)

    # 5. On renvoie la réponse, dans la forme prévue par ReponseChat
    return ReponseChat(reponse=texte, outils_utilises=outils_utilises)