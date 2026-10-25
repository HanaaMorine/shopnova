import sys
from pathlib import Path
import streamlit as st

# Pour pouvoir importer les fichiers du dossier backend
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))
from agent import repondre, PROMPT_SYSTEME

# ===== Le haut de la page =====
st.set_page_config(page_title="ShopNova", page_icon="🛒")
st.title("🛒 Assistant ShopNova")
st.caption("Agent IA avec outils et RAG — données de démonstration")

# ===== La mémoire de la conversation (gardée entre chaque message) =====
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": PROMPT_SYSTEME}]   # pour le LLM
    st.session_state.affichage = []                                                # pour l'écran

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
    # 1. Afficher la question du client
    st.session_state.affichage.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    # 2. Demander la réponse à l'agent
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("assistant"):
        with st.spinner("L'agent réfléchit..."):
            texte, outils_utilises = repondre(st.session_state.messages)
        st.write(texte)
        if outils_utilises:
            with st.expander("🛠️ Outils utilisés"):
                for outil in outils_utilises:
                    st.code(outil)

    # 3. Garder la réponse dans l'historique d'affichage
    st.session_state.affichage.append({"role": "assistant", "content": texte, "outils": outils_utilises})