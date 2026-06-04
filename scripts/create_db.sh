#!/bin/bash

DB_NAME="tradewinds"
DB_USER="tradewinds_user"
DB_PASS="changeme"

# Create user
psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"

# Create database
psql -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Load schema
psql -U $DB_USER -d $DB_NAME -f init_schema.sql
