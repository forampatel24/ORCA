import csv, psycopg, uuid
c = psycopg.connect("host=localhost dbname=orca_db user=postgres password=postgres")
cur = c.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS cmfri_landings (id UUID PRIMARY KEY, year INT, state VARCHAR, species VARCHAR, landings_tonnes INT, gear VARCHAR)")
cur.execute("DELETE FROM cmfri_landings WHERE state IN ('Maharashtra','Gujarat')")
n = 0
with open(r"D:\Foram_TP\ORCA\data\external\cmfri_landings.csv") as f:
    for r in csv.DictReader(f):
        if r["state"] != "Maharashtra":
            continue
        cur.execute("INSERT INTO cmfri_landings (id,year,state,species,landings_tonnes,gear) VALUES (%s,%s,%s,%s,%s,%s)",
                    (str(uuid.uuid4()), int(r["year"]), r["state"], r["species"], int(r["landings_tonnes"]), r["gear"]))
        n += 1
c.commit()
cur.execute("SELECT count(*) FROM cmfri_landings")
print("cmfri inserted:", n, "total:", cur.fetchone()[0])
c.close()
