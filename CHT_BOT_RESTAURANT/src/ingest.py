import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from embeddings import get_embeddings


def ingest_document():
    """
    Scanne le dossier 'documents' à la racine du projet et ingère
    tous les fichiers PDF trouvés dans la vector_db ChromaDB.
    """
    documents_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "documents")
    
    if not os.path.exists(documents_dir):
        print(f"❌ Dossier '{documents_dir}' introuvable.")
        return

    # Scanner tous les PDF dans le dossier documents
    pdf_files = glob.glob(os.path.join(documents_dir, "**", "*.pdf"), recursive=True)
    
    if not pdf_files:
        print(f"❌ Aucun fichier PDF trouvé dans '{documents_dir}'.")
        return

    print(f"📄 {len(pdf_files)} fichier(s) PDF trouvé(s):")
    
    all_docs = []
    for pdf_path in pdf_files:
        print(f"   → {os.path.basename(pdf_path)}")
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            all_docs.extend(documents)
            print(f"     ✅ {len(documents)} page(s) chargée(s)")
        except Exception as e:
            print(f"     ❌ Erreur: {e}")

    if not all_docs:
        print("❌ Aucun document chargé.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    docs = splitter.split_documents(all_docs)
    print(f"\n📦 {len(docs)} chunks créés")

    embeddings = get_embeddings()

    vector_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vector_db")
    
    vectordb = Chroma.from_documents(
        docs,
        embedding=embeddings,
        persist_directory=vector_db_path
    )

    vectordb.persist()

    print(f"✅ {len(docs)} documents ajoutés à ChromaDB ({vector_db_path})")


if __name__ == "__main__":
    ingest_document()