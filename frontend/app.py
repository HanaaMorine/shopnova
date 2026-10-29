import uuid
import requests
import streamlit as st

# ===== L'adresse de notre API FastAPI =====
URL_API = "http://127.0.0.1:8000/chat"

# ===== Le haut de la page =====
st.set_page_config(page_title="ShopNova", page_icon="🛒")
st.title("🛒 Assistant ShopNova")
st.caption("Agent IA avec outils et RAG — données de démonstration")

# ===== La mémoire de la page =====
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())   # un identifiant unique pour cette conversation
    st.session_state.affichage = []                     # les messages à afficher à l'écran

# ===== Afficher l'historique =====
for msg in st.session_state.affichage:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("outils"):
            with st.expander("🛠️ Outils utilisés"):
                for outil in msg["outils"]:
                    st.code(outil)

# ===== Quand le client écrit un message =====
question = st.chat_input("Posez votre question...")
if question:
    # 1. Afficher la question
    st.session_state.affichage.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    # 2. Envoyer la question à l'API (au lieu d'appeler l'agent directement)
    with st.chat_message("assistant"):
        with st.spinner("L'agent réfléchit..."):
            try:
                reponse_api = requests.post(
                    URL_API,
                    json={"session_id": st.session_state.session_id, "message": question},
                    timeout=60
                )
                reponse_api.raise_for_status()          # erreur si le code n'est pas 200
                donnees = reponse_api.json()            # la réponse JSON → dictionnaire Python
                texte = donnees["reponse"]
                outils_utilises = donnees["outils_utilises"]
            except requests.exceptions.RequestException as e:
                texte = f"⚠️ Impossible de contacter l'API : {e}"
                outils_utilises = []

        st.write(texte)
        if outils_utilises:
            with st.expander("🛠️ Outils utilisés"):
                for outil in outils_utilises:
                    st.code(outil)

    # 3. Garder la réponse dans l'historique d'affichage
    st.session_state.affichage.append({"role": "assistant", "content": texte, "outils": outils_utilises})