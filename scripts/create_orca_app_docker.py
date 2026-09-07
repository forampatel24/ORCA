import psycopg
conn = psycopg.connect("host=localhost port=5433 dbname=orca_db user=postgres password=postgres")
cur = conn.cursor()
try:
    cur.execute("CREATE USER orca_app WITH PASSWORD 'orca_app_pass'")
    print("created orca_app")
except Exception as e:
    print("exists", str(e)[:100])
cur.execute("GRANT CONNECT ON DATABASE orca_db TO orca_app")
cur.execute("GRANT USAGE ON SCHEMA public TO orca_app")
cur.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO orca_app")
cur.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO orca_app")
cur.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO orca_app")
cur.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO orca_app")
try:
    cur.execute("REVOKE CREATE ON SCHEMA public FROM orca_app")
except Exception:
    pass
conn.commit()
c2 = psycopg.connect("host=localhost port=5433 dbname=orca_db user=orca_app password=orca_app_pass")
cur2 = c2.cursor()
cur2.execute("SELECT count(*) FROM pfz_observations")
print("orca_app pfz read ok:", cur2.fetchone()[0])
conn.close(); c2.close()
