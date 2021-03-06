#!/bin/bash
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" $POSTGRES_DB -c "CREATE DATABASE \"$TODOAPP_DB\";"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" $POSTGRES_DB -c "CREATE USER \"$TODOAPP_USER\" WITH ENCRYPTED PASSWORD '$TODOAPP_PASSWORD';"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" $POSTGRES_DB -c "GRANT ALL PRIVILEGES ON DATABASE \"$TODOAPP_DB\" TO \"$TODOAPP_USER\";"

psql -v ON_ERROR_STOP=1 --username "$TODOAPP_USER" $TODOAPP_DB -c "CREATE TABLE todo (todo_id uuid, text VARCHAR(1000) NOT NULL, status VARCHAR(1) NOT NULL, PRIMARY KEY (todo_id));"
