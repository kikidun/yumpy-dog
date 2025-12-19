#!/bin/bash
echo "Please enter postgres host name:"
read hostname
echo "Please enter postgres user name:"
read username
echo "Please enter postgres password:"
read password
echo "Please enter postgres database:"
read database

touch app/.env
touch database/.env
touch worker/.env

appworker="PG_HOST=$hostname
PG_USER=$username
DB_PASSWORD=$password
PG_DATABASE=$database"

db="POSTGRES_USER=$username
POSTGRES_PASSWORD=$password
POSTGRES_DB=$database"

printf "$appworker" > app/.env
printf "$appworker" > worker/.env
printf "$db" > database/.env