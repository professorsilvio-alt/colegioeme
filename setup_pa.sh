#!/bin/bash

# Script de configuração automática para PythonAnywhere
# Projeto: Colegio EME

echo "--- Iniciando configuração do Colegio EME no PythonAnywhere ---"

# 1. Definir variáveis
REPO_URL="https://github.com/professorsilvio-alt/colegioeme.git"
PROJECT_DIR="$HOME/colegioeme"
VENV_PATH="$HOME/.virtualenvs/colegioeme_env"

# 2. Clonar o repositório se não existir
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Clonando repositório..."
    git clone $REPO_URL $PROJECT_DIR
else
    echo "Pasta do projeto já existe. Atualizando..."
    cd $PROJECT_DIR
    git pull
fi

cd $PROJECT_DIR

# 3. Criar ambiente virtual se não existir
if [ ! -d "$VENV_PATH" ]; then
    echo "Criando ambiente virtual (Python 3.10)..."
    mkvirtualenv colegioeme_env --python=python3.10
else
    echo "Ambiente virtual já existe."
    workon colegioeme_env
fi

# 4. Instalar dependências
echo "Instalando dependências (requirements.txt)..."
pip install -r requirements.txt

# 5. Criar arquivo .env básico se não existir
if [ ! -f ".env" ]; then
    echo "Criando arquivo .env padrão..."
    cp .env.example .env
    # Gerar uma SECRET_KEY aleatória simples para o início
    echo "DJANGO_SECRET_KEY='django-insecure-$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 32)'" >> .env
    echo "DJANGO_DEBUG=False" >> .env
    echo "DJANGO_ALLOWED_HOSTS=$(whoami).pythonanywhere.com" >> .env
fi

# 6. Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# 7. Migrações do banco (opcional, mas recomendado para inicializar)
# Se o usuário quiser manter o banco local, ele deve fazer o upload do db.sqlite3 manualmente.
if [ ! -f "db.sqlite3" ]; then
    echo "Banco de dados não encontrado. Criando novo banco..."
    python manage.py migrate
fi

echo "--- Configuração de arquivos finalizada! ---"
echo ""
echo "PRÓXIMOS PASSOS MANUAIS NA ABA 'WEB' DO PYTHONANYWHERE:"
echo "1. Code: Source code -> $PROJECT_DIR"
echo "2. Code: Working directory -> $PROJECT_DIR"
echo "3. Code: WSGI configuration file -> Clique no link e configure conforme o walkthrough.md"
echo "4. Virtualenv: Path -> $VENV_PATH"
echo "5. Static files: URL -> /static/  | Path -> $PROJECT_DIR/static_root/"
echo ""
echo "Recarregue o site na aba Web após terminar!"
