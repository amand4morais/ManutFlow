import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).parent

# Configurações do banco de dados
DATABASE_PATH = BASE_DIR / 'data' / 'manutencao.db'
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configurações do Flask
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = True

# Configurações da API Groq
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
# Modelos sugeridos: 'llama-3.3-70b-versatile' ou 'mixtral-8x7b-32768'
GROQ_MODEL = 'llama-3.3-70b-versatile'
