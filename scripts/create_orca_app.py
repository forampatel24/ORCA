import psycopg
conn=psycopg.connect('host=localhost dbname=orca_db user=postgres password=postgres')
cur=conn.cursor()
try:
    cur.execute("CREATE USER orca_app WITH PASSWORD 'orca_app_pass'")
    print('created orca_app')
except Exception as e:
    print('exists', e)
cur.execute('GRANT CONNECT ON DATABASE orca_db TO orca_app')
cur.execute('GRANT USAGE ON SCHEMA public TO orca_app')
cur.execute('GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO orca_app')
cur.execute('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO orca_app')
try:
    cur.execute('REVOKE CREATE ON SCHEMA public FROM orca_app')
except: pass
conn.commit()
import psycopg as p2
c2=p2.connect('host=localhost dbname=orca_db user=orca_app password=orca_app_pass')
cur2=c2.cursor()
cur2.execute('SELECT count(*) FROM pfz_observations')
print('orca_app read', cur2.fetchone()[0])
try:
    cur2.execute('DROP TABLE pfz_observations')
    print('should not allow drop')
except Exception as e:
    print('blocked DROP', str(e)[:120])
