-- Run this file against your Postgres database to update the `date` column.
-- Use: docker exec -i techeventradaradmin-db-1 psql -U postgres -d techeventradar < scripts/migration_make_date_nullable.sql
-- Make the date column nullable in the events table
ALTER TABLE events
ALTER COLUMN date DROP NOT NULL;