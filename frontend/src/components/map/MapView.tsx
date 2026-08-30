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
      zoom: 7,
    })
    map.addControl(new maplibregl.NavigationControl(), 'top-right')
    mapRef.current = map
  }, [])

  useEffect(() => {
    const map = mapRef.current
    if (!map || !map.isStyleLoaded()) return
    // PFZ markers
    const markers = document.querySelectorAll('.orca-pfz-marker')
    markers.forEach((m) => m.remove())
    if (layers.pfz) {
      pfz.forEach((p: any) => {
        const el = document.createElement('div')
        el.className = 'orca-pfz-marker'
        el.style.width = '12px'; el.style.height = '12px'; el.style.background = p.id === selectedPfz?.id ? '#f59e0b' : '#0ea5e9'; el.style.borderRadius = '50%'; el.style.border = '2px solid white'
        el.title = `${p.sector || 'PFZ'} ${p.distance_km?.toFixed(1)}km`
        new maplibregl.Marker({ element: el }).setLngLat([p.longitude, p.latitude]).addTo(map)
      })
    }
  }, [pfz, selectedPfz, layers.pfz])

  useEffect(() => {
    if (mapRef.current) mapRef.current.setCenter(center)
  }, [center])

  return <div ref={ref} className="w-full h-full min-h-[400px] rounded border border-slate-700" />
}
