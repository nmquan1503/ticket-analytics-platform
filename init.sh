#!/bin/bash

set -e

DB_USER="system"
DB_PASS="YourStrongPassword123"
DB_SERVICE="FREEPDB1"

SQL_FILE="sql.sql"


echo "🚀 Running SQL file..."

docker exec -i oracle-db sqlplus $DB_USER/$DB_PASS@$DB_SERVICE < $SQL_FILE

echo "✅ Done!"