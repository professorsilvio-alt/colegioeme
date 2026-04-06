#!/bin/bash
# =============================================
# Backup automático do banco MySQL - Colégio EME
# Executa semanalmente via PythonAnywhere Tasks
# =============================================

BACKUP_DIR="$HOME/backups"
DB_USER="SilvioFreitas"
DB_HOST="SilvioFreitas.mysql.pythonanywhere-services.com"
DB_NAME="SilvioFreitas\$colegioeme"
MAX_BACKUPS=4  # Manter apenas os últimos 4 backups

# Criar diretório de backups se não existir
mkdir -p "$BACKUP_DIR"

# Nome do arquivo com data
FILENAME="backup_colegioeme_$(date +%Y%m%d_%H%M%S).sql.gz"

echo "$(date): Iniciando backup..."

# Fazer dump compactado
mysqldump -u "$DB_USER" -h "$DB_HOST" "$DB_NAME" | gzip > "$BACKUP_DIR/$FILENAME"

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$BACKUP_DIR/$FILENAME" | cut -f1)
    echo "$(date): Backup criado com sucesso: $FILENAME ($SIZE)"

    # Remover backups antigos, manter apenas os últimos MAX_BACKUPS
    cd "$BACKUP_DIR"
    ls -t backup_colegioeme_*.sql.gz | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm
    TOTAL=$(ls backup_colegioeme_*.sql.gz | wc -l)
    echo "$(date): $TOTAL backup(s) mantido(s) no diretório."
else
    echo "$(date): ERRO ao criar backup!"
fi
