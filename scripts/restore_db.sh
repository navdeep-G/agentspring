#!/bin/bash
set -e
DB_NAME=${1:-agentspring}
DB_USER=${2:-user}
DB_HOST=${3:-localhost}
BACKUP_FILE=${4}

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <db_name> <db_user> <db_host> <backup_file>"
  exit 1
fi

psql -U $DB_USER -h $DB_HOST $DB_NAME < $BACKUP_FILE

echo "Restore complete from: $BACKUP_FILE" 