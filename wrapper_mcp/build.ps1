# Construir a imagem de compilação
docker build -t mcp-wrapper-build -f Dockerfile.build .

# Criar um container temporário
$containerId = docker create mcp-wrapper-build

# Copiar o binário compilado do container
docker cp ${containerId}:/app/dist/mcp_wrapper ./dist/mcp_wrapper

# Remover o container temporário
docker rm $containerId
