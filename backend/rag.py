# ===== Les imports (les outils dont on a besoin) =====
import shutil                     # pour supprimer un dossier
from pathlib import Path          # pour manipuler les chemins de fichiers
from dotenv import load_dotenv    # pour lire la clé API dans le fichier .env
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter  # pour découper
from langchain_openai import OpenAIEmbeddings   # pour transformer un texte en vecteur
from langchain_chroma import Chroma             # la base de données vectorielle

load_dotenv()   # on charge la clé API

# ===== Les réglages =====
DOSSIER_DOCUMENTS = Path("data/documents")   # où sont nos documents .md
DOSSIER_CHROMA = "data/chroma_db"            # où on va sauvegarder la base vectorielle

# Le modèle qui transforme un texte en vecteur (une liste de nombres)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


# ===== ÉTAPE 1 : découper les documents en chunks =====
def charger_et_decouper():
    # Découpeur 1 : coupe le texte à chaque titre (# et ##)
    decoupeur_titres = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "document"), ("##", "section")]
    )
    # Découpeur 2 : si un morceau est trop long (plus de 500 caractères), on le recoupe
    # avec 50 caractères en commun entre 2 morceaux pour ne pas perdre le sens
    decoupeur_taille = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    chunks = []                                          # la liste de tous les chunks
    for chemin in DOSSIER_DOCUMENTS.glob("*.md"):        # pour chaque fichier .md du dossier
        texte = chemin.read_text(encoding="utf-8")       # on lit le texte du fichier
        morceaux = decoupeur_titres.split_text(texte)    # on coupe aux titres
        morceaux = decoupeur_taille.split_documents(morceaux)  # on recoupe les morceaux trop longs
        for morceau in morceaux:
            morceau.metadata["source"] = chemin.name     # on note le nom du fichier d'origine
        chunks.extend(morceaux)                          # on ajoute ces morceaux à la liste
    return chunks                                        # on renvoie tous les chunks


# ===== ÉTAPE 2 : transformer en vecteurs et ranger dans ChromaDB =====
def construire_base():
    if Path(DOSSIER_CHROMA).exists():     # si une ancienne base existe déjà...
        shutil.rmtree(DOSSIER_CHROMA)     # ...on la supprime (pour éviter les doublons)
    chunks = charger_et_decouper()        # on récupère les chunks
    # Pour chaque chunk : on calcule son vecteur et on le range dans ChromaDB
    Chroma.from_documents(chunks, embeddings, persist_directory=DOSSIER_CHROMA)
    print(f"✅ Base vectorielle créée avec {len(chunks)} chunks.")


# ===== ÉTAPE 3 : chercher les chunks les plus proches d'une question =====
def chercher_dans_documents(question, k=3):
    # On ouvre la base vectorielle sauvegardée
    base = Chroma(persist_directory=DOSSIER_CHROMA, embedding_function=embeddings)
    # On cherche les k chunks les plus proches de la question (k = 3 par défaut)
    resultats = base.similarity_search_with_score(question, k=k)

    reponses = []                         # la liste des résultats à renvoyer
    for chunk, score in resultats:        # pour chaque chunk trouvé (avec sa distance)
        reponses.append({
            "source": chunk.metadata.get("source"),    # le fichier d'origine
            "section": chunk.metadata.get("section"),  # le titre de la partie
            "texte": chunk.page_content,               # le texte du chunk
            "distance": round(score, 3)                # plus c'est petit, plus c'est proche
        })
    return reponses                       # on renvoie la liste (utile pour l'agent plus tard)


# ===== TESTS (s'exécutent seulement si on lance ce fichier) =====
if __name__ == "__main__":
    construire_base()                     # on crée la base

    question = "J'ai combien de jours pour renvoyer un produit ?"
    print(f"\n❓ {question}\n")
    for r in chercher_dans_documents(question):     # pour chaque chunk trouvé
        print(f"📄 {r['source']} | {r['section']} | distance : {r['distance']}")
        print(r["texte"][:150], "...")               # on affiche les 150 premiers caractères
        print("-" * 40)                              # une ligne de séparation