from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

DOSSIER_DOCUMENTS = Path("data/documents")


def charger_et_decouper():
    """Lit les documents Markdown et les découpe en chunks."""
    # Découpeur 1 : coupe aux titres (# et ##)
    decoupeur_titres = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "document"), ("##", "section")]
    )
    # Découpeur 2 : recoupe les parties trop longues (500 caractères max, 50 de chevauchement)
    decoupeur_taille = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    chunks = []
    for chemin in DOSSIER_DOCUMENTS.glob("*.md"):         # chaque fichier .md du dossier
        texte = chemin.read_text(encoding="utf-8")
        morceaux = decoupeur_titres.split_text(texte)      # 1. découpe aux titres
        morceaux = decoupeur_taille.split_documents(morceaux)  # 2. recoupe si trop long
        for morceau in morceaux:
            morceau.metadata["source"] = chemin.name       # on note de quel fichier vient le chunk
        chunks.extend(morceaux)
    return chunks


if __name__ == "__main__":
    chunks = charger_et_decouper()
    print(f"Nombre de chunks : {len(chunks)}\n")
    for chunk in chunks[:3]:                               # on affiche les 3 premiers
        print(chunk.metadata)
        print(chunk.page_content)
        print("-" * 40)