from flask import Flask, request, jsonify
import requests
import tempfile
import fitz  # PyMuPDF
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

app = Flask(__name__)

# Initialise le client Qdrant
qdrant = QdrantClient(
    url="https://f1242dac-7cf9-4440-8714-33de13d20341.us-west-2-0.aws.cloud.qdrant.io",  # ← remplace par ton vrai lien
    api_key="Qdrant_b9e59f42-e02b-4348-a8df-bf80c6ecb9b4"       # ← remplace par ta vraie clé
)

try:
    qdrant.get_collection("pdf-manuals")
except:
    qdrant.recreate_collection(
        collection_name="pdf-manuals",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )

embeddings = OpenAIEmbeddings()

@app.route('/process_pdfs', methods=['POST'])
def process_pdfs():
    data = request.get_json()
    links = data.get("pdf_links", [])

    for item in links:
        pdf_url = item["url"]
        name = item["name"]

        try:
            # Télécharger le fichier PDF
            response = requests.get(pdf_url)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name

            # Extraction du texte avec PyMuPDF
            text = ""
            with fitz.open(tmp_path) as doc:
                for page in doc:
                    text += page.get_text()

            # Suppression du fichier temporaire
            os.remove(tmp_path)

            # Découper le texte
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            docs = splitter.create_documents([text])

            # Insertion dans Qdrant
            Qdrant.from_documents(
                documents=docs,
                embedding=embeddings,
                url="https://your-qdrant-endpoint",  # ← même lien ici
                prefer_grpc=False,
                collection_name="pdf-manuals"        # ← ou ce que tu veux
            )

        except Exception as e:
            print(f"Erreur pour {name} : {e}")

    return jsonify({"status": "done", "processed": len(links)})

