# Runbook: Database Restore Drill

## Purpose

Verify that `deploy.yml`'s pre-migration `pg_dump` backups (added in Faz 1,
see [ADR context in deploy.yml](../../.github/workflows/deploy.yml)) are
actually restorable — a backup that's never been test-restored is a backup
you don't actually have. Run this periodically (recommended: whenever
`sw.js`/schema conventions change, or at least quarterly) and after any
incident that touches the backup mechanism itself.

**Always restore into an environment separate from where the backup was
taken** — never test-restore onto the production DB. This drill restores
into a throwaway local Docker container.

## Procedure

1. **Pull a backup down, read-only:**
   ```bash
   scp meto@<server>:~/TechEventRadar/backups/pre_deploy_<timestamp>.sql.gz ./
   ```
   This only reads from the server; nothing on production is touched.

2. **Start an isolated Postgres container** (different port, throwaway
   name — never reuse `techeventradar_db`):
   ```bash
   docker run -d --name restore-drill-pg \
     -e POSTGRES_DB=drill_db -e POSTGRES_USER=drill_user -e POSTGRES_PASSWORD=drill_pass \
     -p 127.0.0.1:55432:5432 postgres:16
   ```

3. **Restore:**
   ```bash
   gunzip -c pre_deploy_<timestamp>.sql.gz | docker exec -i restore-drill-pg psql -U drill_user -d drill_db
   ```

4. **Verify schema is at the expected migration head:**
   ```bash
   docker exec restore-drill-pg psql -U drill_user -d drill_db -c "SELECT version_num FROM alembic_version;"
   # compare against: alembic heads (run against the repo at the commit the backup was taken from)
   ```

5. **Verify real data, not just table existence:**
   ```bash
   docker exec restore-drill-pg psql -U drill_user -d drill_db -c "SELECT count(*) FROM events;"
   ```

6. **Verify the application actually works against the restored DB** —
   the real test, not just SQL checks:
   ```bash
   DATABASE_URL=postgresql://drill_user:drill_pass@127.0.0.1:55432/drill_db \
     ALLOW_INSECURE_DEFAULTS=true SECRET_KEY=<32+ chars> ADMIN_USERNAME=a ADMIN_PASSWORD=b \
     uvicorn app.main:app --host 127.0.0.1 --port 8010
   curl http://127.0.0.1:8010/health
   curl "http://127.0.0.1:8010/api/events?active_only=true"
   ```

7. **Clean up:** `docker stop restore-drill-pg && docker rm restore-drill-pg`, delete the local backup copy.

## Drill log

### 2026-08-01 — first drill, backup `pre_deploy_20260801_161647.sql.gz`

- **Result: PASS.** Restore completed in <1s (116 KB dump, current DB
  size). Schema landed at `f1a2b3c4d5e6`, matching repo HEAD's
  `alembic heads` at drill time. 14/14 tables present. `events`: 238 rows,
  `tags`: 6, `blog_posts`: 3 — real production data, not empty tables.
  Backend booted against the restored DB and served real data via
  `/api/events` (verified a real event title came back, not a stub).
- **Finding — not a failure, but a real gotcha to know about before a
  real disaster:** `pg_dump`'s default output includes `ALTER TABLE ...
  OWNER TO app_user` / `GRANT` statements. Restoring into a fresh
  database whose superuser isn't literally named `app_user` prints one
  `ERROR: role "app_user" does not exist` per object (harmless — `psql`
  continues past errors by default, and the schema still restores
  completely) but all objects end up owned by whichever role ran the
  restore instead of `app_user`. **In a real disaster-recovery scenario
  standing up a brand-new host**, either: create an `app_user` role
  first (`CREATE ROLE app_user;`) before restoring, matching production's
  actual username, or accept the new owner and update `DATABASE_URL`'s
  user to match. Neither blocks recovery, but not knowing this in advance
  during an actual incident would cost time second-guessing the error
  wall. `docker-compose.yml` already creates `POSTGRES_USER` from
  `.env`'s `POSTGRES_USER` — as long as a fresh host's `.env` matches
  the value the backup was taken with, this is a non-issue.
- **RTO observation:** at current data volume (238 events), the restore
  itself is near-instant. The bottleneck in a real incident would be
  provisioning a fresh Postgres instance and getting the backup file
  transferred, not the restore operation itself.
