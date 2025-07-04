from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/api/rag", methods=["POST"])
def rag():
    data = request.get_json()
    # Extrait du texte du fichier ou URL, à traiter avec embeddings ici
    query = data.get("query")
    return jsonify({"response": f"Tu m'as demandé : {query} (réponse factice à remplacer)"})

@app.route("/")
def index():
    return "API RAG is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
