from flask import Flask, request, jsonify
import requests
import tempfile
import fitz  # PyMuPDF
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

app = Flask(__name__)

# Initialise le client Qdrant
qdrant = QdrantClient(
    url="https://f1242dac-7cf9-4440-8714-33de13d20341.us-west-2-0.aws.cloud.qdrant.io",
    api_key="Qdrant_b9e59f42-e02b-4348-a8df-bf80c6ecb9b4"
)

# Vérifie si la collection existe, sinon la crée
try:
    if not qdrant.collection_exists("pdf-manuals"):
        qdrant.create_collection(
            collection_name="pdf-manuals",
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )
except Exception as e:
    print(f"⚠️ Erreur lors de l'accès ou de la création de la collection : {e}")

embeddings = OpenAIEmbeddings()

@app.route('/process_pdfs', methods=['POST'])
def process_pdfs():
    data = request.get_json()
    links = data.get("pdf_links", [])

    for item in links:
        pdf_url = item["url"]
        name = item["name"]

        try:
            response = requests.get(pdf_url)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name

            text = ""
            with fitz.open(tmp_path) as doc:
                for page in doc:
                    text += page.get_text()

            os.remove(tmp_path)

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            docs = splitter.create_documents([text])

            Qdrant.from_documents(
                documents=docs,
                embedding=embeddings,
                url="https://f1242dac-7cf9-4440-8714-33de13d20341.us-west-2-0.aws.cloud.qdrant.io",
                api_key="Qdrant_b9e59f42-e02b-4348-a8df-bf80c6ecb9b4",
                prefer_grpc=False,
                collection_name="pdf-manuals"
            )

        except Exception as e:
            print(f"Erreur pour {name} : {e}")

    return jsonify({"status": "done", "processed": len(links)})
