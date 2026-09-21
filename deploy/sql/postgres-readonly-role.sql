-- deploy/sql/postgres-readonly-role.sql
-- Read-only role for Cursor / analysis (SELECT only). Run as doadmin.
--
-- 1. Create user "saas_base-user-readonly" in the DigitalOcean Users tab.
-- 2. GRANT CONNECT (once, any database).
-- 3. Connect to EACH app database and run the schema grants below.
--
-- Alembic creates tables as saas_base-user-admin, so default privileges
-- must be FOR ROLE "saas_base-user-admin".
-- Keycloak database is separate — skip it here.

-- =============================================================================
-- CONNECT (run once as doadmin, any database)
-- =============================================================================
GRANT CONNECT ON DATABASE saas_base_dev TO "saas_base-user-readonly";
GRANT CONNECT ON DATABASE saas_base_test TO "saas_base-user-readonly";
GRANT CONNECT ON DATABASE saas_base_staging TO "saas_base-user-readonly";
GRANT CONNECT ON DATABASE saas_base_prod TO "saas_base-user-readonly";

-- =============================================================================
-- Repeat while connected to: saas_base_dev, saas_base_test,
-- saas_base_staging, saas_base_prod
-- =============================================================================
GRANT USAGE ON SCHEMA public TO "saas_base-user-readonly";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "saas_base-user-readonly";
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO "saas_base-user-readonly";

ALTER DEFAULT PRIVILEGES FOR ROLE "saas_base-user-admin" IN SCHEMA public
  GRANT SELECT ON TABLES TO "saas_base-user-readonly";
ALTER DEFAULT PRIVILEGES FOR ROLE "saas_base-user-admin" IN SCHEMA public
  GRANT SELECT ON SEQUENCES TO "saas_base-user-readonly";

SELECT current_database() AS db,
       has_table_privilege('saas_base-user-readonly', 'users', 'SELECT') AS can_select,
       has_table_privilege('saas_base-user-readonly', 'users', 'INSERT') AS can_insert;
