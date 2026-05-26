#!/bin/bash
# ==========================================================
# Backup automático do banco MySQL - Colégio EME (Capelum)
# Recomendado rodar diariamente via PythonAnywhere Tasks
# ==========================================================

# 1. Configurações
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKUP_DIR="$HOME/backups"
ENV_FILE="$BASE_DIR/.env"
MAX_BACKUPS=4  # Mantém os últimos 4 backups

# 2. Carregar senha se o .env existir
if [ -f "$ENV_FILE" ]; then
    # Extrai o DB_PASSWORD ignorando espaços e aspas
    export MYSQL_PWD=$(grep '^DB_PASSWORD=' "$ENV_FILE" | cut -d '=' -f2- | tr -d '"'\''' | xargs)
fi

# 3. Dados do Banco (Carregados do .env com fallback seguro)
if [ -f "$ENV_FILE" ]; then
    DB_USER=$(grep '^DB_USER=' "$ENV_FILE" | cut -d '=' -f2- | tr -d '"'\''' | xargs)
    DB_HOST=$(grep '^DB_HOST=' "$ENV_FILE" | cut -d '=' -f2- | tr -d '"'\''' | xargs)
    DB_NAME=$(grep '^DB_NAME=' "$ENV_FILE" | cut -d '=' -f2- | tr -d '"'\''' | xargs)
fi

DB_USER=${DB_USER:-"SilvioFreitas"}
DB_HOST=${DB_HOST:-"SilvioFreitas.mysql.pythonanywhere-services.com"}
DB_NAME=${DB_NAME:-"SilvioFreitas\$capelo"}

# Criar diretório de backups se não existir
mkdir -p "$BACKUP_DIR"

# Nome do arquivo com timestamp (ISO 8601 compact)
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
FILENAME="backup_colegioeme_${TIMESTAMP}.sql.gz"

echo "--------------------------------------------------------"
echo "$(date): Iniciando backup do banco: $DB_NAME"

# 4. Executar o Dump
# Usamos a variável MYSQL_PWD herdada do export acima para autenticação automática
mysqldump --no-tablespaces -u "$DB_USER" -h "$DB_HOST" "$DB_NAME" | gzip > "$BACKUP_DIR/$FILENAME"

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$BACKUP_DIR/$FILENAME" | cut -f1)
    echo "$(date): Backup concluído com sucesso: $FILENAME ($SIZE)"

    # 5. Rotação: Remover arquivos antigos e manter apenas os 4 mais recentes
    echo "$(date): Limpando backups antigos (limite: $MAX_BACKUPS)..."
    cd "$BACKUP_DIR"
    # Lista arquivos por data (novos primeiro), pula os primeiros 4, deleta o resto
    ls -t backup_colegioeme_*.sql.gz | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm
    
    TOTAL=$(ls backup_colegioeme_*.sql.gz | wc -l)
    echo "$(date): Rotação finalizada. Total no disco: $TOTAL"
else
    echo "$(date): >>> ERRO CRÍTICO <<< falha ao gerar o dump do MySQL."
    exit 1
fi
echo "--------------------------------------------------------"
