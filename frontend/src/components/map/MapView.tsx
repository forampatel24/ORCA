import { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { useMapStore } from '../../stores/mapStore'

export default function MapView() {
  const ref = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const { center, pfz, selectedPfz, layers } = useMapStore()

  useEffect(() => {
    if (!ref.current || mapRef.current) return
    const map = new maplibregl.Map({
      container: ref.current,
      style: 'https://demotiles.maplibre.org/style.json',
      center,
      zoom: 4.5,
    })
    map.addControl(new maplibregl.NavigationControl(), 'top-right')
    map.on('load', () => {
      // ORCA footprint: India states + cities + EEZ/coast — all from local public/ (data-driven)
      fetch('/india_states.geojson').then(r=>r.json()).then(data=>{
        map.addSource('india-states', { type: 'geojson', data })
        map.addLayer({ id: 'india-states-fill', type: 'fill', source: 'india-states', paint: { 'fill-color': '#1e293b', 'fill-opacity': 0.35 } })
        map.addLayer({ id: 'india-states-line', type: 'line', source: 'india-states', paint: { 'line-color': '#94a3b8', 'line-width': 1 } })
        map.addLayer({ id: 'india-states-hover', type: 'fill', source: 'india-states', paint: { 'fill-color': '#38bdf8', 'fill-opacity': 0 } })
        // hover highlight + click popup
        map.on('mousemove','india-states-hover', e=>{
          if(e.features?.[0]) map.getCanvas().style.cursor='pointer'
        })
        map.on('mouseleave','india-states-hover', ()=>{ map.getCanvas().style.cursor='' })
        map.on('click','india-states-fill', e=>{
          const f:any=e.features?.[0]; if(!f) return;
          new maplibregl.Popup().setLngLat(e.lngLat).setHTML(`<div style="color:#0f172a"><b>${f.properties?.NAME_1 || f.properties?.ST_NM || 'State'}</b></div>`).addTo(map)
        })
      }).catch(()=>{})
      fetch('/india_coastline.geojson').then(r=>r.json()).then(data=>{
        map.addSource('india-coast', { type: 'geojson', data })
        map.addLayer({ id: 'india-coast-line', type: 'line', source: 'india-coast', paint: { 'line-color': '#38bdf8', 'line-width': 2 } })
      }).catch(()=>{})
      fetch('/india_eez.geojson').then(r=>r.json()).then(data=>{
        map.addSource('india-eez', { type: 'geojson', data })
        map.addLayer({ id: 'india-eez-fill', type: 'fill', source: 'india-eez', paint: { 'fill-color': '#0ea5e9', 'fill-opacity': 0.08 } })
        map.addLayer({ id: 'india-eez-line', type: 'line', source: 'india-eez', paint: { 'line-color': '#0ea5e9', 'line-width': 1, 'line-dasharray': [4,4] } })
      }).catch(()=>{})
      // cities via base style labels (not hard-coded) — no manual points
      // ORCA Mumbai pilot highlight box 18.5-20.5 / 72-73.5
      map.addSource('orca-mumbai-box', { type:'geojson', data:{ type:'Feature', geometry:{ type:'Polygon', coordinates:[[[72,18.5],[73.5,18.5],[73.5,20.5],[72,20.5],[72,18.5]]] }, properties:{} } as any })
      map.addLayer({ id:'orca-box-fill', type:'fill', source:'orca-mumbai-box', paint:{ 'fill-color':'#22d3ee','fill-opacity':0.07 } })
      map.addLayer({ id:'orca-box-line', type:'line', source:'orca-mumbai-box', paint:{ 'line-color':'#22d3ee','line-width':2,'line-dasharray':[6,4] } })
    })
    mapRef.current = map
  }, [])

  useEffect(() => {
    const map = mapRef.current
    if (!map || !map.isStyleLoaded()) return
    // PFZ markers — interactive with popup
    document.querySelectorAll('.orca-pfz-marker').forEach((m) => m.remove())
    if (layers.pfz) {
      pfz.forEach((p: any) => {
        const el = document.createElement('div')
        el.className = 'orca-pfz-marker'
        el.style.width = p.id === selectedPfz?.id ? '14px' : '12px'; el.style.height = p.id === selectedPfz?.id ? '14px' : '12px'; el.style.background = p.id === selectedPfz?.id ? '#f59e0b' : '#0ea5e9'; el.style.borderRadius = '50%'; el.style.border = '2px solid white'; el.style.cursor='pointer'
        const popup = new maplibregl.Popup({ offset: 12 }).setHTML(`<div style="color:#0f172a"><b>${p.metadata?.sector || p.sector || 'PFZ'}</b><br/>SST ${p.metadata?.sst || '-'}°C Chl ${p.metadata?.chl || '-'}<br/>${p.distance_km?.toFixed(1)||'-'}km away<br/><small>${p.latitude.toFixed(2)},${p.longitude.toFixed(2)}</small></div>`)
        el.addEventListener('click', () => popup.setLngLat([p.longitude, p.latitude]).addTo(map))
        new maplibregl.Marker({ element: el }).setLngLat([p.longitude, p.latitude]).addTo(map)
      })
    }
    // layer toggles
    try {
      for(const l of ['india-states-fill','india-states-line','india-eez-fill','india-eez-line','india-coast-line','orca-box-fill','orca-box-line']){
        if(map.getLayer(l)) map.setLayoutProperty(l,'visibility', l.includes('states')? (layers.mpa?'visible':'none') : (l.includes('eez')? (layers.eez?'visible':'none') : (layers.pfz?'visible':'none')))
      }
    } catch {}
  }, [pfz, selectedPfz, layers])

  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.flyTo({ center, zoom: center[0] > 80 ? 6 : 8, duration: 1200 })
    }
  }, [center])

  return <div ref={ref} className="w-full h-full min-h-[400px] rounded border border-slate-700" />
}
