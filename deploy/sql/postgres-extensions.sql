-- deploy/sql/postgres-extensions.sql
-- Run once per database via DO admin / doadmin (managed PostgreSQL 17).

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
