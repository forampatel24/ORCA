import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, GeoJSON as RLGeoJSON, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useMapStore } from '../../stores/mapStore'

// fix icons
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({ iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png', iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png', shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png' })

function FlyTo({ center }: { center: [number, number] }) {
  const map = useMap()
  useEffect(() => {
    // Mumbai zoom 9 when near 72-73 lon, else 5
    const lon = center[0], lat = center[1]
    const zoom = (lon >=72 && lon <=73.5 && lat >=18 && lat <=20) ? 9 : 5
    map.flyTo([center[1], center[0]], zoom, { duration: 1.2 } as any)
  }, [center])
  return null
}

export default function LeafletMap() {
  const { center, pfz, layers } = useMapStore()
  const [states, setStates] = useState<any>(null)
  const [eez, setEez] = useState<any>(null)
  const [coast, setCoast] = useState<any>(null)

  const [mumbaiCoast, setMumbaiCoast] = useState<any>(null)
  const [mumbaiMpa, setMumbaiMpa] = useState<any>(null)

  useEffect(() => {
    fetch('/india_states.geojson').then(r=>r.json()).then(setStates).catch(()=>{})
    // NO hardcoded file - fetch authentic from PostGIS via backend bbox API
    const bbox = '72.2,18.5,73.2,19.5'
    fetch(`/api/v1/geospatial/eez?bbox=${bbox}`).then(r=>r.ok?r.json():Promise.reject()).then(setEez).catch(()=>{})
    fetch(`/api/v1/geospatial/mpa?bbox=${bbox}`).then(r=>r.ok?r.json():Promise.reject()).then(setMumbaiMpa).catch(()=>{})
    fetch(`/api/v1/geospatial/coastline?bbox=${bbox}`).then(r=>r.ok?r.json():Promise.reject()).then(d=> {
      if(d.features && d.features.length>0) setMumbaiCoast(d)
      else setMumbaiCoast(null)
    }).catch(()=> setMumbaiCoast(null))
    // Auto-load PFZ for Mumbai so toggle shows difference even before chat
    import('../../api/client').then(({ getNearestPFZ }) => {
      getNearestPFZ(19.076, 72.877, 80).then((d:any)=>{
        if(d.items?.length){
          const { setPfz } = useMapStore.getState()
          // Deduplicate by lat/lon already in repo, but ensure distinct
          setPfz(d.items)
        }
      }).catch(()=>{})
    })
  }, [])

  const pfzIcon = (sel:boolean) => L.divIcon({ className:'', html:`<div style="width:${sel?14:12}px;height:${sel?14:12}px;background:${sel?'#f59e0b':'#0ea5e9'};border-radius:50%;border:2px solid white;box-shadow:0 0 4px #000"></div>`, iconSize:[12,12] as any, iconAnchor:[6,6] as any })

  // PFZ zone icon — color by score/distance, size by suitability
  const getPfzStyle = (p:any) => {
    const score = p.pfz_score ?? p.metadata?.pfz_score ?? 0.7
    const isHigh = score > 0.75 || (p.metadata?.sst >=27 && p.metadata?.sst <=29)
    return { color: isHigh ? '#22c55e' : '#0ea5e9', fill: isHigh ? '#22c55e' : '#0ea5e9' }
  }

  return (
    // @ts-ignore
    <MapContainer center={[19.2,72.85] as any} zoom={9} style={{ height: '100%', minHeight: 400, borderRadius: 8 } as any} className="border border-slate-700">
      {/* @ts-ignore */}
      <TileLayer attribution='&copy; OpenStreetMap' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {/* Maharashtra only faint background */}
      {layers.mpa && states && /* @ts-ignore */ <RLGeoJSON data={states} style={(f:any)=> f?.properties?.NAME_1==='Maharashtra' ? { color:'#64748b', weight:1.5, fillColor:'#1e293b', fillOpacity:0.25 } as any : { color:'#334155', weight:0.5, fillColor:'#0f172a', fillOpacity:0.12 } as any} onEachFeature={(f:any,l:any)=>{ l.on({ mouseover:(e:any)=>e.target.setStyle({fillOpacity:0.4}), mouseout:(e:any)=>{ const isMaha = f.properties?.NAME_1==='Maharashtra'; e.target.setStyle({fillOpacity:isMaha?0.25:0.12}) } }); l.bindPopup(`<b>${f.properties?.NAME_1 || f.properties?.ST_NM || 'State'}</b>${f.properties?.NAME_1==='Maharashtra'?' <span style=color:#38bdf8>Mumbai pilot</span>':''}`) }} />}
      {/* EEZ - Mumbai clipped offshore only, not covering land - properly visible dashed */}
      {layers.eez && eez && /* @ts-ignore */ <RLGeoJSON data={eez} style={{ color:'#0ea5e9', weight:2, dashArray:'8 8', fillColor:'#0ea5e9', fillOpacity:0.12 } as any} onEachFeature={(f:any,l:any)=> l.bindPopup(`<b>${f.properties?.name || 'EEZ'}</b><br/>${f.properties?.note || 'Mumbai clipped — offshore only'}`) } />}
      {/* MPA - Thane Creek visible when zoomed to Mumbai */}
      {layers.mpa && mumbaiMpa && /* @ts-ignore */ <RLGeoJSON data={mumbaiMpa} style={(f:any)=> f.properties?.name?.includes('Thane') ? { color:'#f43f5e', weight:2, dashArray:'4 4', fillColor:'#f43f5e', fillOpacity:0.18 } as any : { color:'#ef4444', weight:1.5, fillColor:'#ef4444', fillOpacity:0.10 } as any} onEachFeature={(f:any,l:any)=> l.bindPopup(`<b>${f.properties?.name}</b><br/>${f.properties?.authority || ''}<br/><span style=color:#f43f5e>${f.properties?.restriction || ''}</span>`) } />}
      {/* Accurate Mumbai coastline - Natural Earth 10m from PostGIS, no dummy */}
      {mumbaiCoast && /* @ts-ignore */ <RLGeoJSON data={mumbaiCoast} style={{ color:'#38bdf8', weight:3, opacity:0.95, lineCap:'round' } as any} onEachFeature={(f:any,l:any)=> l.bindPopup(`<b>${f.properties?.name}</b><br/><small>Authentic Natural Earth 10m</small>`) } />}
      {/* PFZ - improved: zone halo (5km) + marker colored by suitability + distance - NO span (MapContainer only allows Layers) */}
      {layers.pfz && pfz.map((p:any)=>{
        const s = getPfzStyle(p)
        return [
            // @ts-ignore
            <Marker key={p.id+'-halo'} position={[p.latitude, p.longitude] as any} icon={L.divIcon({ className:'', html:`<div style="width:36px;height:36px;background:${s.fill}22;border:1.5px dashed ${s.color};border-radius:50%;"></div>`, iconSize:[36,36] as any, iconAnchor:[18,18] as any }) as any} />,
            // @ts-ignore
            <Marker key={p.id} position={[p.latitude, p.longitude] as any} icon={pfzIcon(false) as any} eventHandlers={{ mouseover:(e:any)=> e.target.openPopup() }}>
              <Popup>
                <div style={{color:'#0f172a', minWidth:160}}>
                  <b style={{color:s.color}}>{p.metadata?.sector || p.sector || 'PFZ'}</b> <span style={{background:s.color, color:'white', padding:'2px 6px', borderRadius:4, fontSize:10}}>{p.pfz_score ? (p.pfz_score*100).toFixed(0)+'%' : ''}</span><br/>
                  <small>SST {p.metadata?.sst ?? p.sst ?? '-'}°C • Chl {p.metadata?.chl ?? p.metadata?.chlorophyll ?? '-'} mg/m³</small><br/>
                  <small>{p.distance_km?.toFixed(1)} km from Mumbai • {p.latitude.toFixed(3)}, {p.longitude.toFixed(3)}</small><br/>
                  <small style={{color: s.color}}>{p.metadata?.sst>=27 && p.metadata?.sst<=29 ? '✓ Favourable SST' : ''}</small>
                </div>
              </Popup>
            </Marker>
        ]
      }).flat()}
      <FlyTo center={center} />
    </MapContainer>
  )
}
