# Exame CSI-30

Este projeto realiza a integração entre a API do Google e o banco de dados orientado a grafos Neo4j.

## 🚀 Pré-requisitos

Antes de começar, certifique-se de ter instalado em seu ambiente WSL:

*   [Python 3.x](https://www.python.org/)
*   pip (Gerenciador de pacotes do Python)
*   Uma conta/instância ativa no [Neo4j AuraDB](https://neo4j.com/cloud/aura/) (ou local)
*   Uma chave de API válida do Google (Google AI/Gemini)

## 🛠️ Instalação e Configuração

Siga os passos abaixo para configurar o ambiente de desenvolvimento no terminal do WSL.

### 1. Configuração do Ambiente Virtual

Navegue até a pasta do projeto e execute os comandos abaixo para criar e ativar um ambiente virtual isolado:

```bash
# Criar o ambiente virtual
python3 -m venv venv

# Ativar o ambiente virtual
source venv/bin/activate
```

*Você saberá que o ambiente está ativo quando aparecer `(venv)` no início da linha do terminal.*

### 2. Instalação das Dependências

Com o ambiente virtual ativo, instale as bibliotecas necessárias listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Configuração das Variáveis de Ambiente

Crie um arquivo chamado `.env` na raiz do projeto para armazenar suas credenciais de segurança.

1. Crie o arquivo `.env`.
2. Cole o seguinte conteúdo dentro dele, substituindo os valores pelos seus dados reais:

```ini
# Chaves de API
GOOGLE_API_KEY="sua_chave_da_google_api_aqui"

# Configurações do Neo4j
NEO4J_URI="neo4j+s://<ID do database aqui>.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="sua_senha_neo4j_aqui"
```

> **Importante:** Nunca compartilhe o arquivo `.env`, pois ele contém senhas sensíveis.

## ▶️ Como Rodar

Após seguir todos os passos de instalação e configuração, execute o arquivo principal:

```bash
python3 main.py
```

## 📦 Estrutura de Arquivos

*   `main.py`: Arquivo principal de execução.
*   `requirements.txt`: Lista de dependências do projeto.
*   `.env`: (Criado pelo usuário) Variáveis de ambiente e segredos.
*   `venv/`: Pasta do ambiente virtual (não deve ser versionada).
