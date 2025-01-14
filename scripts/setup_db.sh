#!/bin/bash

# Create the database user
psql postgres -c "CREATE USER bakery_user WITH PASSWORD 'bakery_password';"

# Create the database
psql postgres -c "CREATE DATABASE bakery_chatbot;"

# Grant privileges to the user
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE bakery_chatbot TO bakery_user;"

# Connect to the database and grant schema privileges
psql bakery_chatbot -c "GRANT ALL ON SCHEMA public TO bakery_user;"

echo "Database setup completed!" 