#!/bin/sh
# Database roles and schemas enforcing the single-writer rule (ADR-001).
#
# Runs once at first container start via docker-entrypoint-initdb.d, as the
# POSTGRES_USER superuser against the application database. Role passwords are
# read from the environment (MTG_AI_DATA_PASSWORD, MTG_AI_APP_PASSWORD) so no
# credential is committed to source.
#
#   mtg_ai_data : owns the "data" schema; sole writer of reference/corpus/
#                 analytics tables.
#   mtg_ai_app  : owns the "app" schema (users, sessions, decks, ...); holds
#                 USAGE + SELECT on "data" but NO write there.

set -eu

: "${MTG_AI_DATA_PASSWORD:?MTG_AI_DATA_PASSWORD must be set}"
: "${MTG_AI_APP_PASSWORD:?MTG_AI_APP_PASSWORD must be set}"

psql -v ON_ERROR_STOP=1 \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    --set data_password="$MTG_AI_DATA_PASSWORD" \
    --set app_password="$MTG_AI_APP_PASSWORD" <<-'EOSQL'
    -- Roles (idempotent). Passwords come from psql variables, not literals.
    SELECT format('CREATE ROLE mtg_ai_data LOGIN PASSWORD %L', :'data_password')
    WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'mtg_ai_data')
    \gexec
    SELECT format('CREATE ROLE mtg_ai_app LOGIN PASSWORD %L', :'app_password')
    WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'mtg_ai_app')
    \gexec

    -- Both roles may connect to and create schemas in this database.
    GRANT CONNECT ON DATABASE mtg_ai TO mtg_ai_data, mtg_ai_app;
    GRANT CREATE ON DATABASE mtg_ai TO mtg_ai_data, mtg_ai_app;

    -- Schemas, each owned by its writer role so only that role can DDL within it.
    CREATE SCHEMA IF NOT EXISTS data AUTHORIZATION mtg_ai_data;
    CREATE SCHEMA IF NOT EXISTS app AUTHORIZATION mtg_ai_app;

    -- App role: read-only access to the data schema. USAGE lets it resolve
    -- names; SELECT is granted on existing and (via default privileges) future
    -- tables. No INSERT/UPDATE/DELETE is ever granted, so the single-writer
    -- rule is a database-level guarantee, not a convention.
    GRANT USAGE ON SCHEMA data TO mtg_ai_app;
    GRANT SELECT ON ALL TABLES IN SCHEMA data TO mtg_ai_app;
    ALTER DEFAULT PRIVILEGES IN SCHEMA data
        GRANT SELECT ON TABLES TO mtg_ai_app;
    ALTER DEFAULT PRIVILEGES FOR ROLE mtg_ai_data IN SCHEMA data
        GRANT SELECT ON TABLES TO mtg_ai_app;

    -- Prevent the implicit PUBLIC role from writing the public schema.
    REVOKE CREATE ON SCHEMA public FROM PUBLIC;
EOSQL
