import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, GeoJSON as RLGeoJSON, Marker, Popup, Rectangle, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useMapStore } from '../../stores/mapStore'

// fix icons
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({ iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png', iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png', shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png' })

function FlyTo({ center }: { center: [number, number] }) {
  const map = useMap()
  useEffect(() => { map.flyTo([center[1], center[0]], center[0] > 80 ? 6 : 8, { duration: 1.2 } as any) }, [center])
  return null
}

export default function LeafletMap() {
  const { center, pfz, layers } = useMapStore()
  const [states, setStates] = useState<any>(null)
  const [eez, setEez] = useState<any>(null)
  const [coast, setCoast] = useState<any>(null)

  useEffect(() => {
    fetch('/india_states.geojson').then(r=>r.json()).then(setStates).catch(()=>{})
    fetch('/india_eez.geojson').then(r=>r.json()).then(setEez).catch(()=>{})
    fetch('/india_coastline.geojson').then(r=>r.json()).then(setCoast).catch(()=>{})
  }, [])

  const pfzIcon = (sel:boolean) => L.divIcon({ className:'', html:`<div style="width:${sel?14:12}px;height:${sel?14:12}px;background:${sel?'#f59e0b':'#0ea5e9'};border-radius:50%;border:2px solid white;box-shadow:0 0 4px #000"></div>`, iconSize:[12,12] as any, iconAnchor:[6,6] as any })

  return (
    // @ts-ignore
    <MapContainer center={[20,78] as any} zoom={5} style={{ height: '100%', minHeight: 400, borderRadius: 8 } as any} className="border border-slate-700">
      {/* @ts-ignore */}
      <TileLayer attribution='&copy; OpenStreetMap' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {layers.mpa && states && /* @ts-ignore */ <RLGeoJSON data={states} style={{ color:'#94a3b8', weight:1, fillColor:'#1e293b', fillOpacity:0.2 } as any} onEachFeature={(f:any,l:any)=>{ l.on({ mouseover:(e:any)=>e.target.setStyle({fillOpacity:0.4}), mouseout:(e:any)=>e.target.setStyle({fillOpacity:0.2}) }); l.bindPopup(`<b>${f.properties?.NAME_1 || f.properties?.ST_NM || 'State'}</b>`) }} />}
      {layers.eez && eez && /* @ts-ignore */ <RLGeoJSON data={eez} style={{ color:'#0ea5e9', weight:1, dashArray:'6 6', fillColor:'#0ea5e9', fillOpacity:0.08 } as any} />}
      {layers.pfz && coast && /* @ts-ignore */ <RLGeoJSON data={coast} style={{ color:'#38bdf8', weight:2 } as any} />}
      {layers.pfz && pfz.map((p:any)=>(
        // @ts-ignore
        <Marker key={p.id} position={[p.latitude, p.longitude] as any} icon={pfzIcon(false) as any}>
          <Popup><b>{p.metadata?.sector || 'PFZ'}</b><br/>SST {p.metadata?.sst}°C Chl {p.metadata?.chl}<br/>{p.distance_km?.toFixed(1)}km</Popup>
        </Marker>
      ))}
      {layers.pfz && /* @ts-ignore */ <Rectangle bounds={[[18.5,72],[20.5,73.5]] as any} pathOptions={{ color:'#22d3ee', weight:2, dashArray:'8 6', fillOpacity:0.05 } as any}><Popup>ORCA Mumbai pilot 18.5-20.5N 72-73.5E<br/>32 PFZ</Popup></Rectangle>}
      <FlyTo center={center} />
    </MapContainer>
  )
}
