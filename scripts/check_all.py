import psycopg, json, asyncio
from pathlib import Path

print("=== M1 PostGIS ===")
c=psycopg.connect('host=localhost dbname=orca_db user=postgres password=postgres')
cur=c.cursor()
for tbl in ['maritime_boundaries','protected_areas','geofences','pfz_observations','weather_observations','knowledge_documents','knowledge_chunks']:
    cur.execute(f'SELECT count(*) FROM {tbl}')
    print(tbl, cur.fetchone()[0])
try:
    cur.execute('SELECT count(*) FROM cmfri_landings')
    print('cmfri_landings', cur.fetchone()[0])
except: print('cmfri_landings 0 (table missing)')
cur.execute('SELECT PostGIS_Version()'); print('postgis', cur.fetchone()[0])
# spatial
cur.execute("SELECT ST_Contains(geometry, ST_GeomFromText('POINT(72.8 19.0)',4326)) FROM maritime_boundaries WHERE name='India EEZ'")
print('EEZ contains Mumbai', cur.fetchone()[0])
cur.execute("SELECT ST_Contains(geometry, ST_GeomFromText('POINT(78.5 9.0)',4326)) FROM protected_areas WHERE name='Gulf of Mannar MPA'")
print('MPA contains Gulf', cur.fetchone()[0])

print("\n=== M3 Backend API ===")
import httpx, os
# use httpx sync via requests-like but use httpx
import requests
try:
    r=requests.get('http://127.0.0.1:8000/api/v1/health')
    print('health', r.json())
    r=requests.post('http://127.0.0.1:8000/api/v1/auth/login', data={'username':'test@orca.local','password':'test123'})
    tok=r.json()['access_token']
    print('login ok token len', len(tok))
    h={'Authorization': f'Bearer {tok}'}
    r=requests.get('http://127.0.0.1:8000/api/v1/pfz/nearest?latitude=19.0&longitude=72.8&radius=50', headers=h)
    print('pfz nearest count', r.json()['count'], 'first dist', r.json()['items'][0]['distance_km'])
    r=requests.get('http://127.0.0.1:8000/api/v1/weather/?latitude=19.0&longitude=72.8', headers=h)
    print('weather items', len(r.json()['items']))
    r=requests.post('http://127.0.0.1:8000/api/v1/chat/', json={'message':'Where is nearest PFZ today?'}, headers=h)
    print('chat PFZ', r.json()['response'][:200])
    r=requests.post('http://127.0.0.1:8000/api/v1/chat/', json={'message':'Is it safe to fish tomorrow near Mumbai?'}, headers=h)
    print('chat safety', r.json()['response'][:300])
except Exception as e:
    print('API error', e)

print("\n=== M4 Orchestrator ===")
from app.agents.orchestrator.graph import orchestrator_app
async def t4():
    s=await orchestrator_app.ainvoke({'session_id':'s1','user_query':'Where is nearest PFZ today?'})
    print('intent', s['intent'], 'plan', len(s['plan']), 'agents', list(s['agent_results'].keys()))
    s=await orchestrator_app.ainvoke({'session_id':'s2','user_query':'Is it safe tomorrow near Mumbai?'})
    print('safety risk', s['agent_results']['risk_agent']['risk_level'], 'score', s['agent_results']['risk_agent']['risk_score'])
asyncio.run(t4())

print("\n=== M5 Agents ===")
from app.tools.geospatial import check_geofence
from app.tools.risk import calculate_risk
from app.analytics.pfz.scoring import score_pfz
from app.analytics.risk.engine import calculate_risk as risk2
print('geofence Mumbai', check_geofence(19.0,72.8)['inside_geofence'])
print('risk HIGH', calculate_risk(18,3.0)['risk_level'])
print('risk engine VERY_HIGH', risk2(22,4.0, lightning=True, cyclone=True)['risk_level'])
print('pfz score', score_pfz(28.2,0.8,15.2,'MODERATE')['pfz_score'])

print("\n=== M6 Analytics ===")
from app.analytics.ocean.anomaly import sst_anomaly
from app.analytics.routing.engine import haversine
print('sst anomaly', sst_anomaly(28.5))
print('haversine', haversine(19.0,72.8,19.1,72.5))

print("\n=== M8 RAG ===")
from app.rag.retrieval import retrieve
hits=retrieve('wind risk 15 m/s', top_k=5, top_n=2)
print('rag wind', [(h['citation'], round(h['score'],3)) for h in hits])
hits=retrieve('MPA buffer 5km', top_k=5, top_n=2)
print('rag MPA', [(h['citation'], round(h['score'],3)) for h in hits])

print("\n=== Frontend ===")
print('frontend exists', Path('D:/Foram_TP/ORCA/frontend/src/App.tsx').exists(), 'size', Path('D:/Foram_TP/ORCA/frontend/src/App.tsx').stat().st_size)
print('frontend vite', Path('D:/Foram_TP/ORCA/frontend/vite.config.ts').exists())

print("\nALL CHECKS DONE")
