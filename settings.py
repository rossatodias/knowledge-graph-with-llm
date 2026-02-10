import os
from os.path import join, dirname
from dotenv import load_dotenv

# Carrega o arquivo .env
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Captura as variáveis de ambiente
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")