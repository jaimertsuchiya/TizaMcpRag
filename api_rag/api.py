from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama

app = FastAPI()

embedding = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://ollama:11434"
)
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding
)

llm = ChatOllama(
    model="gemma3:latest", 
    temperature=0,
    base_url="http://ollama:11434"
)

class AskRequest(BaseModel):
    pergunta: str

class AskResponse(BaseModel):
    resposta: str
    fontes: List[str]

@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    docs_and_scores = vectorstore.similarity_search_with_score(
        request.pergunta,
        k=20  # Pegamos mais blocos para dar chance melhor
    )

    # Filtrar por score de relevância
    docs = [doc for doc, score in docs_and_scores if score >= 0.5]

    if not docs:
        return AskResponse(
            resposta="Não encontrei esta informação nos documentos fornecidos.",
            fontes=[]
        )

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
Você é um assistente que responde perguntas exclusivamente com base nos documentos fornecidos.

Regras obrigatórias:
- Utilize apenas informações explícitas do contexto.
- NÃO invente informações.
- Se a informação não estiver no contexto, responda: "Não encontrei esta informação nos documentos fornecidos."
- Se encontrar dados sobre contribuições esporádicas, vincule corretamente ao tema de reembolso previdenciário.

Documentos:
{context}

Pergunta:
{request.pergunta}

Resposta:
"""

    response = llm.invoke(prompt)
    fontes = [doc.metadata.get("source", "desconhecido") for doc, score in docs_and_scores]

    return AskResponse(
        resposta=response.content.strip(),
        fontes=fontes
    )
