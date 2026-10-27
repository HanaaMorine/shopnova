# ===== Les imports =====
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Pour pouvoir importer les fichiers du dossier backend
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))
from agent import repondre, PROMPT_SYSTEME      # notre agent

from langchain_openai import ChatOpenAI          # ✏️ le LLM "correcteur" (OpenAI au lieu de Groq)
from langchain_openai import OpenAIEmbeddings    # les embeddings (pour comparer des textes)
from ragas import evaluate, EvaluationDataset, RunConfig
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import Faithfulness, AnswerCorrectness

load_dotenv()


# ===== 1. Lire nos questions de test =====
with open("tests/cas_rag.json", "r", encoding="utf-8") as fichier:
    cas_de_test = json.load(fichier)


# ===== 2. Récupérer les chunks que l'agent a lus =====
def extraire_contextes(messages):
    """Cherche dans l'historique les résultats de l'outil RAG (les chunks lus par l'agent)."""
    contextes = []
    for message in messages:
        if isinstance(message, dict) and message.get("role") == "tool":
            try:
                resultat = json.loads(message["content"])
            except json.JSONDecodeError:
                continue
            if isinstance(resultat, list):                 # le RAG renvoie une liste de chunks
                for chunk in resultat:
                    if isinstance(chunk, dict) and "texte" in chunk:
                        contextes.append(chunk["texte"])
    return contextes


# ===== 3. Faire répondre l'agent à chaque question =====
echantillons = []
for cas in cas_de_test:
    print(f"❓ {cas['user_input']}")
    messages = [
        {"role": "system", "content": PROMPT_SYSTEME},
        {"role": "user", "content": cas["user_input"]}
    ]
    reponse, outils_utilises = repondre(messages)          # l'agent répond
    print(f"   🛠️ {outils_utilises}")
    print(f"   🤖 {reponse}\n")

    # Les 4 ingrédients de RAGAS
    echantillons.append({
        "user_input": cas["user_input"],                    # la question
        "retrieved_contexts": extraire_contextes(messages), # les chunks lus
        "response": reponse,                                # la réponse de l'agent
        "reference": cas["reference"]                       # la bonne réponse attendue
    })


# ===== 4. Préparer le correcteur =====
juge = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", temperature=0))   # ✏️ OpenAI comme juge
embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(model="text-embedding-3-small"))


# ===== 5. Lancer l'évaluation =====
dataset = EvaluationDataset.from_list(echantillons)
resultat = evaluate(
    dataset=dataset,
    metrics=[Faithfulness(), AnswerCorrectness()],
    llm=juge,
    embeddings=embeddings,
    run_config=RunConfig(max_workers=4, timeout=180)   # ✏️ 4 tâches en parallèle (plus rapide)
)


# ===== 6. Afficher et sauvegarder les résultats =====
print("\n📊 Scores moyens :", resultat)
tableau = resultat.to_pandas()
print(tableau[["user_input", "faithfulness", "answer_correctness"]])
tableau.to_csv("tests/resultats_ragas.csv", index=False)
print("\n✅ Résultats sauvegardés dans tests/resultats_ragas.csv")