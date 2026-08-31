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
      // Load India coastline/EEZ from local public files (imported, not hard-coded)
      fetch('/india_coastline.geojson').then(r=>r.json()).then(data=>{
        map.addSource('india-coast', { type: 'geojson', data })
        map.addLayer({ id: 'india-coast-line', type: 'line', source: 'india-coast', paint: { 'line-color': '#38bdf8', 'line-width': 2 } })
      }).catch(()=>{})
      fetch('/india_eez.geojson').then(r=>r.json()).then(data=>{
        map.addSource('india-eez', { type: 'geojson', data })
        map.addLayer({ id: 'india-eez-fill', type: 'fill', source: 'india-eez', paint: { 'fill-color': '#0ea5e9', 'fill-opacity': 0.08 } })
        map.addLayer({ id: 'india-eez-line', type: 'line', source: 'india-eez', paint: { 'line-color': '#0ea5e9', 'line-width': 1, 'line-dasharray': [4,4] } })
      }).catch(()=>{})
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
    // EEZ/Coast visibility toggle
    try {
      if (map.getLayer('india-eez-fill')) map.setLayoutProperty('india-eez-fill','visibility', layers.eez? 'visible':'none')
      if (map.getLayer('india-eez-line')) map.setLayoutProperty('india-eez-line','visibility', layers.eez? 'visible':'none')
      if (map.getLayer('india-coast-line')) map.setLayoutProperty('india-coast-line','visibility', layers.pfz? 'visible':'none')
    } catch {}
  }, [pfz, selectedPfz, layers])

  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.flyTo({ center, zoom: center[0] > 80 ? 6 : 8, duration: 1200 })
    }
  }, [center])

  return <div ref={ref} className="w-full h-full min-h-[400px] rounded border border-slate-700" />
}
