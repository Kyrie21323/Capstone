-- Manual SQL migration script to upgrade password_hash column
-- This script can be run directly on Postgres if the automatic migration doesn't work
--
-- Usage (on Postgres):
--   psql -d your_database_name -f migrations/manual_password_hash_upgrade.sql
--
-- Or via psql prompt:
--   \i migrations/manual_password_hash_upgrade.sql

-- Check current column type (for reference)
-- SELECT column_name, data_type, character_maximum_length 
-- FROM information_schema.columns 
-- WHERE table_name = 'user' AND column_name = 'password_hash';

-- Upgrade password_hash from VARCHAR(128) to VARCHAR(255)
-- This is safe to run multiple times (idempotent) - it will only change if needed
ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(255);

-- Verify the change
-- SELECT column_name, data_type, character_maximum_length 
-- FROM information_schema.columns 
-- WHERE table_name = 'user' AND column_name = 'password_hash';
