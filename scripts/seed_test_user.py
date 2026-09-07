import uuid, psycopg
from app.core.security import get_password_hash
c = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
cur = c.cursor()
cur.execute("SELECT id FROM users WHERE email='test@orca.local'")
row = cur.fetchone()
if row:
    print("test user exists:", row[0])
else:
    uid = str(uuid.uuid4())
    cur.execute("INSERT INTO users (id, email, password_hash, name) VALUES (%s,%s,%s,%s)",
                (uid, "test@orca.local", get_password_hash("test123"), "Test"))
    c.commit()
    print("created test user:", uid)
c.close()
