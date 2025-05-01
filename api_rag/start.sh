#!/bin/bash

# Primeiro inicializa os modelos do Ollama
python init_ollama.py

# Se a inicialização foi bem sucedida, inicia a API
if [ $? -eq 0 ]; then
    uvicorn api:app --host 0.0.0.0 --port 8000
else
    echo "Falha ao inicializar modelos Ollama"
    exit 1
fi
