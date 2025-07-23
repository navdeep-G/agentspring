#!/bin/bash
set -e
DB_NAME=${1:-agentspring}
DB_USER=${2:-user}
DB_HOST=${3:-localhost}
BACKUP_FILE=${4:-backup_$(date +%Y%m%d_%H%M%S).sql}

pg_dump -U $DB_USER -h $DB_HOST $DB_NAME > $BACKUP_FILE

echo "Backup complete: $BACKUP_FILE" 