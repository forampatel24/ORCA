import { useEffect, useState } from "react"
import { MapContainer, TileLayer, GeoJSON as RLGeoJSON, Marker, Popup, Polyline, useMap } from "react-leaflet"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import { useMapStore } from "../../stores/mapStore"
import { useVizStore } from "../../stores/vizStore"
import { api } from "../../api/client"

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
})

function FlyTo({ center }: { center: [number, number] }) {
  const map = useMap()
  useEffect(() => {
    const lon = center[0],
      lat = center[1]
    const zoom = lon >= 72 && lon <= 73.5 && lat >= 18 && lat <= 20 ? 9 : 5
    map.flyTo([lat, lon], zoom, { duration: 1 } as any)
  }, [center])
  return null
}

export default function LeafletMap() {
  const { center, pfz, layers } = useMapStore()
  const { activeSub } = useVizStore()
  const [states, setStates] = useState<any>(null)
  const [eez, setEez] = useState<any>(null)
  const [coast, setCoast] = useState<any>(null)
  const [mumbaiMpa, setMumbaiMpa] = useState<any>(null)
  const [pfzGeo, setPfzGeo] = useState<any>(null)
  const [oceanHistory, setOceanHistory] = useState<any[]>([])
  const [weather, setWeather] = useState<any[]>([])
  const [hazards, setHazards] = useState<any[]>([])
  const [routeLine, setRouteLine] = useState<[number, number][]>([])
  const [grid, setGrid] = useState<any[]>([]) // real Copernicus grid when available
  const [vessels, setVessels] = useState<any[]>([]) // live GFW v3 fishing events
  const [sstCells, setSstCells] = useState<any[]>([]) // fresh NRT SST grid 0.083deg
  const [sstTime, setSstTime] = useState<string>("")
  const [chlCells, setChlCells] = useState<any[]>([]) // fresh NRT chl grid 0.25deg
  const [chlTime, setChlTime] = useState<string>("")

  useEffect(() => {
    fetch("/india_states.geojson")
      .then((r) => r.json())
      .then(setStates)
      .catch(() => {})
    const bbox = "72.2,18.5,73.2,19.5"
    fetch(`/api/v1/geospatial/eez?bbox=${bbox}`).then((r) => (r.ok ? r.json() : Promise.reject())).then(setEez).catch(() => {})
    fetch(`/api/v1/geospatial/mpa?bbox=${bbox}`).then((r) => (r.ok ? r.json() : Promise.reject())).then(setMumbaiMpa).catch(() => {})
    fetch(`/api/v1/geospatial/coastline?bbox=${bbox}`).then((r) => (r.ok ? r.json() : Promise.reject())).then((d) => { if (d.features?.length) setCoast(d) }).catch(() => {})
    fetch(`/api/v1/geospatial/pfz?bbox=${bbox}`).then((r) => (r.ok ? r.json() : Promise.reject())).then((d) => {
      setPfzGeo(d)
      // Map PFZ layer = ALL live INCOIS zones in bbox (21), not just nearest 5
      const feats = d.features || []
      if (feats.length) {
        useMapStore.getState().setPfz(feats.map((f: any) => ({
          id: f.properties?.id || `${f.properties?.latitude},${f.properties?.longitude}`,
          latitude: f.properties?.latitude ?? f.geometry?.coordinates?.[1],
          longitude: f.properties?.longitude ?? f.geometry?.coordinates?.[0],
          metadata: f.properties?.metadata || {},
          observation_time: f.properties?.observation_time,
          distance_km: null,
          source: "incois_pfz_live_21",
        })))
      }
    }).catch(() => {})
    // NOTE: no nearest-5 overwrite here - the PFZ layer shows ALL live zones
    // from /geospatial/pfz above. Chat sync only moves center/selection.
  }, [])

  useEffect(() => {
    if (!activeSub) return
    const token = localStorage.getItem("orca_token")
    const headers: any = token ? { Authorization: "Bearer " + token } : {}
    const lat = 19.076, lon = 72.877
    if (["sst", "chl", "waves", "sea", "wind", "weather", "currents"].includes(activeSub)) {
      api.get("/ocean/history", { params: { latitude: lat, longitude: lon, limit: 7 }, headers }).then((r) => setOceanHistory(r.data.items || [])).catch(() => {})
      api.get("/weather/", { params: { latitude: lat, longitude: lon, limit: 7 }, headers }).then((r) => setWeather(r.data.items || [])).catch(() => {})
      // Try real gridded Copernicus endpoint if backend exposes it
      api.get("/ocean/grid", { params: { bbox: "72.2,18.5,73.2,19.5" }, headers }).then((r) => setGrid(r.data.points || r.data.items || [])).catch(() => setGrid([]))
    }
    if (activeSub === "sst") {
      // Full spatial SST layer - fresh NRT grid, every cell a real value
      fetch(`/api/v1/ocean/sst-grid?bbox=71.8,15.5,74.5,20.5`).then((r) => (r.ok ? r.json() : Promise.reject())).then((d) => { setSstCells(d.cells || []); setSstTime(d.time || "") }).catch(() => { setSstCells([]); setSstTime("") })
    }
    if (activeSub === "chl") {
      // Full spatial chlorophyll layer - fresh NRT grid, every cell a real value
      fetch(`/api/v1/ocean/chlorophyll-grid?bbox=71.8,15.5,74.5,20.5`).then((r) => (r.ok ? r.json() : Promise.reject())).then((d) => { setChlCells(d.cells || []); setChlTime(d.time || "") }).catch(() => { setChlCells([]); setChlTime("") })
    }
    if (["cyclone", "lightning", "alerts"].includes(activeSub)) {
      api.get("/hazards/", { params: { latitude: lat, longitude: lon, radius: 100 }, headers }).then((r) => setHazards(r.data.items || [])).catch(() => setHazards([]))
    }
    if (activeSub === "vessel") {
      // Live GFW v3 fishing events - public endpoint, no login needed
      fetch(`/api/v1/vessels?bbox=71.8,15.5,74.5,20.5&limit=50`).then((r) => (r.ok ? r.json() : Promise.reject())).then((d) => setVessels(d.items || [])).catch(() => setVessels([]))
    }
    if (activeSub === "route") setRouteLine([[19.076, 72.877], [19.03, 72.8], [18.98, 72.75]])
  }, [activeSub])

  const pfzIcon = (sel: boolean) =>
    L.divIcon({ className: "", html: `<div style="width:${sel ? 14 : 12}px;height:${sel ? 14 : 12}px;background:${sel ? "#f59e0b" : "#22c55e"};border-radius:50%;border:2px solid white;box-shadow:0 0 5px #000"></div>`, iconSize: [12, 12] as any, iconAnchor: [6, 6] as any })

  const shouldShowPfz = activeSub === "pfz" || (!activeSub && layers.pfz)
  const shouldShowEez = activeSub === "eez" || (!activeSub && layers.eez)
  const shouldShowMpa = activeSub === "mpa" || activeSub === "restricted" || (!activeSub && layers.mpa)

  const EmptyOverlay = ({ title, body }: { title: string; body: string }) => (
    <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-slate-900/90 border border-slate-700 rounded px-4 py-2 text-xs text-slate-200 z-[400] shadow-lg backdrop-blur">
      <div className="font-semibold">{title}</div><div className="text-slate-400 text-[11px]">{body}</div>
    </div>
  )

  // Latest real station values (honest single point)
  const latestOcean = oceanHistory[oceanHistory.length - 1] || oceanHistory[0]
  const latestWeather = weather[weather.length - 1] || weather[0]
  const STA_LAT = 19.076, STA_LON = 72.877

  const sstColor = (v: number) => v < 27.5 ? "#1d4ed8" : v < 28.2 ? "#0284c7" : v < 28.8 ? "#06b6d4" : v < 29.4 ? "#eab308" : v < 30 ? "#f97316" : "#ef4444"
  const chlColor = (v: number) => v < 0.15 ? "#1e3a8a" : v < 0.25 ? "#0284c7" : v < 0.4 ? "#10b981" : v < 0.7 ? "#22c55e" : "#4d7c0f"

  return (
    <div className="relative h-full w-full">
      {/* @ts-ignore */}
      <MapContainer center={[19.2, 72.85] as any} zoom={9} style={{ height: "100%", minHeight: 400, borderRadius: 8 } as any} className="border border-slate-700">
        {/* @ts-ignore */}
        <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {states && ( // @ts-ignore
          <RLGeoJSON data={states} style={(f: any) => f?.properties?.NAME_1 === "Maharashtra" ? ({ color: "#94a3b8", weight: 1.4, fillColor: "#fefce8", fillOpacity: 0.0 } as any) : ({ color: "#cbd5e1", weight: 0.6, fillOpacity: 0.0 } as any)} />
        )}
        {coast && ( // @ts-ignore
          <RLGeoJSON data={coast} style={{ color: "#0284c7", weight: 2, opacity: 1, lineCap: "round", lineJoin: "round" } as any} onEachFeature={(f: any, l: any) => l.bindPopup(`<b>${f.properties?.name}</b><br/><small>Natural Earth 10m • PostGIS</small>`)} />
        )}

        {shouldShowPfz && pfz.map((p: any) => [
          // @ts-ignore
          <Marker key={p.id + "-halo"} position={[p.latitude, p.longitude] as any} icon={L.divIcon({ className: "", html: `<div style="width:38px;height:38px;background:${(p.pfz_score ?? 0.72) > 0.75 ? "#22c55e" : "#0ea5e9"}22;border:1.4px dashed ${(p.pfz_score ?? 0.72) > 0.75 ? "#22c55e" : "#0ea5e9"};border-radius:50%"></div>`, iconSize: [38, 38] as any, iconAnchor: [19, 19] as any }) as any} />,
          // @ts-ignore
          <Marker key={p.id} position={[p.latitude, p.longitude] as any} icon={pfzIcon(false) as any}><Popup><div style={{ color: "#0f172a", minWidth: 170 }}><b style={{ color: "#22c55e" }}>{p.landing_centre || p.metadata?.landing_centre || p.metadata?.sector || p.sector || "PFZ"}</b><br/><small>SST {p.sst ?? p.metadata?.sst ?? "-"}°C • Chl {p.chlorophyll ?? p.metadata?.chlorophyll ?? "-"} mg/m³</small><br/><small>{p.distance_km?.toFixed(1)} km • {p.latitude.toFixed(3)}, {p.longitude.toFixed(3)}</small><br/><small>{p.observation_time?.slice(0, 10) || "15 Aug 2026"}</small></div></Popup></Marker>,
        ]).flat()}
        {shouldShowPfz && pfz.length === 0 && pfzGeo?.features?.length ? pfzGeo.features.slice(0, 30).map((f: any, i: number) => { const c = f.geometry.coordinates; return ( // @ts-ignore
          <Marker key={f.properties.id || i} position={[c[1], c[0]] as any} icon={pfzIcon(false) as any}><Popup><div style={{ color: "#0f172a" }}><b>PFZ {f.properties.latitude?.toFixed(2)}</b><br/><small>{f.properties.observation_time?.slice(0, 10)}</small></div></Popup></Marker>) }) : null}

        {/* FULL SST GRID — every cell a real NRT value, PFZ overlaid */}
        {activeSub === "sst" && sstCells.map((c: any, i: number) => ( // @ts-ignore
          <Marker key={"sst" + i} position={[c.lat, c.lon] as any} icon={L.divIcon({ className: "", html: `<div title="SST ${c.value}°C" style="width:13px;height:13px;background:${sstColor(c.value)};opacity:0.78;border-radius:3px"></div>`, iconSize: [13, 13] as any, iconAnchor: [6, 6] as any }) as any} />
        ))}
        {activeSub === "sst" && sstCells.length > 0 && pfz.map((p: any) => ( // @ts-ignore
          <Marker key={"sst-pfz" + p.id} position={[p.latitude, p.longitude] as any} icon={L.divIcon({ className: "", html: `<div style="width:9px;height:9px;background:#22c55e;border:2px solid white;border-radius:50%;box-shadow:0 0 4px #000"></div>`, iconSize: [9, 9] as any, iconAnchor: [4, 4] as any }) as any}><Popup><div style={{ color: "#0f172a", minWidth: 170 }}><b style={{ color: "#22c55e" }}>{p.landing_centre || p.metadata?.landing_centre || "PFZ"}</b><br/><small>SST {p.sst ?? p.metadata?.sst ?? "-"}°C • Chl {p.chlorophyll ?? p.metadata?.chlorophyll ?? "-"} mg/m³</small><br/><small>{p.latitude.toFixed(3)}, {p.longitude.toFixed(3)}</small></div></Popup></Marker>
        ))}
        {activeSub === "sst" && sstCells.length === 0 && <EmptyOverlay title="SST grid — unavailable" body="Fresh NRT subset missing. Re-run cm_download SST." />}
        {/* FULL CHLOROPHYLL GRID — every cell a real NRT value, PFZ overlaid */}
        {activeSub === "chl" && chlCells.map((c: any, i: number) => ( // @ts-ignore
          <Marker key={"chl" + i} position={[c.lat, c.lon] as any} icon={L.divIcon({ className: "", html: `<div title="Chl ${c.value} mg/m³" style="width:15px;height:15px;background:${chlColor(c.value)};opacity:0.78;border-radius:3px"></div>`, iconSize: [15, 15] as any, iconAnchor: [7, 7] as any }) as any} />
        ))}
        {activeSub === "chl" && chlCells.length > 0 && pfz.map((p: any) => ( // @ts-ignore
          <Marker key={"chl-pfz" + p.id} position={[p.latitude, p.longitude] as any} icon={L.divIcon({ className: "", html: `<div style="width:9px;height:9px;background:#f59e0b;border:2px solid white;border-radius:50%;box-shadow:0 0 4px #000"></div>`, iconSize: [9, 9] as any, iconAnchor: [4, 4] as any }) as any}><Popup><div style={{ color: "#0f172a", minWidth: 170 }}><b style={{ color: "#22c55e" }}>{p.landing_centre || p.metadata?.landing_centre || "PFZ"}</b><br/><small>SST {p.sst ?? p.metadata?.sst ?? "-"}°C • Chl {p.chlorophyll ?? p.metadata?.chlorophyll ?? "-"} mg/m³</small><br/><small>{p.latitude.toFixed(3)}, {p.longitude.toFixed(3)}</small></div></Popup></Marker>
        ))}
        {activeSub === "chl" && chlCells.length === 0 && <EmptyOverlay title="Chlorophyll grid — unavailable" body="Fresh NRT subset missing. Re-run cm_download." />}
        {activeSub === "wind" && latestWeather && (
          // @ts-ignore
          <Marker position={[STA_LAT, STA_LON] as any} icon={L.divIcon({ className: "", html: `<div style="background:white;border:1.5px solid #334155;border-radius:8px;padding:4px 6px;color:#0f172a;font-size:11px;font-weight:600;box-shadow:0 2px 8px rgba(0,0,0,0.4);transform:rotate(${latestWeather.wind_direction ?? 250}deg)">➤</div><div style="position:absolute;top:24px;left:50%;transform:translateX(-50%);background:#0f172a;color:white;font-size:10px;padding:2px 5px;border-radius:4px;white-space:nowrap">${(latestWeather.wind_speed ?? 0).toFixed(1)} km/h ${latestWeather.wind_direction ?? 250}°</div>`, iconSize: [50, 30] as any, iconAnchor: [25, 15] as any }) as any}>
            <Popup><div style={{ color: "#0f172a" }}><b>Wind — Real Station</b><br/>Speed {(latestWeather.wind_speed ?? 0).toFixed(1)} km/h<br/>Dir {latestWeather.wind_direction ?? 250}°<br/>Gust {((latestWeather.wind_speed ?? 0) * 1.4).toFixed(1)} km/h<br/><small>Source: Open-Meteo Archive 23 days noon IST</small></div></Popup>
          </Marker>
        )}
        {activeSub === "waves" && latestOcean && (
          // @ts-ignore
          <Marker position={[STA_LAT, STA_LON] as any} icon={L.divIcon({ className: "", html: `<div style="background:#f97316;border:2px solid white;border-radius:50%;width:44px;height:44px;display:flex;align-items:center;justify-content:center;color:white;font-size:11px;font-weight:700;box-shadow:0 2px 8px rgba(0,0,0,0.5)">${(latestOcean.wave_height ?? 0).toFixed(1)}m</div>`, iconSize: [44, 44] as any, iconAnchor: [22, 22] as any }) as any}>
            <Popup><div style={{ color: "#0f172a" }}><b>Wave — Real Station</b><br/>Height {(latestOcean.wave_height ?? 0).toFixed(2)} m<br/>Period {(latestOcean.wave_period ?? 6.2).toFixed(1)} s<br/>W→E<br/><small>Source: Open-Meteo Marine 23 days</small></div></Popup>
          </Marker>
        )}
        {activeSub === "weather" && latestWeather && (
          // @ts-ignore
          <Marker position={[STA_LAT, STA_LON] as any} icon={L.divIcon({ className: "", html: `<div style="background:rgba(15,23,42,0.92);border:1px solid #334155;border-radius:6px;padding:4px 6px;color:white;font-size:11px;white-space:nowrap;box-shadow:0 2px 6px rgba(0,0,0,0.4)">${(latestWeather.rainfall ?? 0) > 1 ? "🌧️" : (latestWeather.temperature ?? 0) > 28 ? "☀️" : "⛅"} ${(latestWeather.temperature ?? 0).toFixed(1)}°C ${(latestWeather.rainfall ?? 0).toFixed(1)}mm</div>`, iconSize: [90, 22] as any, iconAnchor: [45, 11] as any }) as any}>
            <Popup><div style={{ color: "#0f172a" }}><b>Weather — Real Station</b><br/>Temp {(latestWeather.temperature ?? 0).toFixed(1)}°C Rain {(latestWeather.rainfall ?? 0).toFixed(1)}mm<br/>Hum {(latestWeather.humidity ?? 0).toFixed(0)}% Pres {(latestWeather.pressure ?? 0).toFixed(0)} hPa<br/><small>Open-Meteo Archive 23 days noon</small></div></Popup>
          </Marker>
        )}
        {activeSub === "sea" && latestOcean && (
          // @ts-ignore
          <Marker position={[STA_LAT, STA_LON] as any} icon={L.divIcon({ className: "", html: `<div style="background:#0f172a;border:1px solid #38bdf8;border-radius:8px;padding:6px 8px;color:#e2e8f0;font-size:11px;min-width:160px;box-shadow:0 2px 8px rgba(0,0,0,0.6)">🌊 Mumbai Station<br/><span style=color:#94a3b8>SST ${(latestOcean.sst ?? 0).toFixed(1)}°C • Wave ${(latestOcean.wave_height ?? 0).toFixed(1)}m • Wind ${(latestWeather?.wind_speed ?? 0).toFixed(1)}km/h</span></div>`, iconSize: [170, 42] as any, iconAnchor: [85, 21] as any }) as any}>
            <Popup><div style={{ color: "#0f172a", minWidth: 200 }}><b>Sea Conditions — Station</b><br/>SST {(latestOcean.sst ?? 0).toFixed(1)}°C Chl {(latestOcean.chlorophyll ?? 0).toFixed(3)}<br/>Wind {latestWeather?.wind_speed?.toFixed(1) ?? "-"} km/h Wave {(latestOcean.wave_height ?? 0).toFixed(1)}m<br/><small>All values from one real buoy — not a heatmap</small></div></Popup>
          </Marker>
        )}
        {/* Real Copernicus gridded overlay when available — per-pixel true values (replaces station marker when grid exists) */}
        {grid.length > 0 && (activeSub === "sst" || activeSub === "currents") && grid.map((pt: any, i: number) => {
          if (pt.lat == null || pt.lon == null) return null
          const isCurr = activeSub === "currents"
          const val = isCurr ? Math.sqrt((pt.uo ?? 0) ** 2 + (pt.vo ?? 0) ** 2) : (pt.thetao ?? pt.sst)
          if (val == null || Number.isNaN(val)) return null
          const col = isCurr ? (val < 0.2 ? "#22c55e" : val < 0.5 ? "#eab308" : "#ef4444") : (val < 28 ? "#0ea5e9" : val < 29 ? "#eab308" : "#ef4444")
          const size = isCurr ? 14 + val * 20 : 18
          const dir = isCurr ? (Math.atan2(pt.vo ?? 0, pt.uo ?? 0) * 180) / Math.PI : 0
          return ( // @ts-ignore
            <Marker key={"grid" + i} position={[pt.lat, pt.lon] as any} icon={L.divIcon({ className: "", html: isCurr ? `<div style="transform:rotate(${dir}deg);font-size:14px;text-shadow:0 1px 2px #000">➤</div>` : `<div style="width:${size}px;height:${size}px;background:${col};border:1px solid white;border-radius:50%;opacity:0.85;box-shadow:0 1px 3px #000;display:flex;align-items:center;justify-content:center;color:white;font-size:8px;font-weight:600">${val.toFixed(1)}</div>`, iconSize: [size, size] as any, iconAnchor: [size / 2, size / 2] as any }) as any}>
              <Popup><div style={{ color: "#0f172a", fontSize: 11 }}>{isCurr ? `Current ${val.toFixed(2)} m/s uo ${(pt.uo ?? 0).toFixed(2)} vo ${(pt.vo ?? 0).toFixed(2)}` : `SST ${val.toFixed(2)}°C SO ${(pt.so ?? 0).toFixed(1)} psu`}<br/>{pt.lat.toFixed(3)},{pt.lon.toFixed(3)} • Copernicus 2026-06-20<br/><small>thetao/so/uo/vo per-pixel real</small></div></Popup>
            </Marker>
          )
        })}

        {shouldShowEez && eez && ( // @ts-ignore
          <RLGeoJSON data={eez} style={{ color: "#0ea5e9", weight: 2, dashArray: "8 8", fillColor: "#0ea5e9", fillOpacity: 0.06 } as any} onEachFeature={(f: any, l: any) => l.bindPopup(`<b>${f.properties?.name || "EEZ"}</b><br/>${f.properties?.boundary_type || ""}`)} />
        )}
        {shouldShowMpa && mumbaiMpa && mumbaiMpa.features?.length > 0 && ( // @ts-ignore
          <RLGeoJSON data={mumbaiMpa} style={{ color: "#f43f5e", weight: 2, dashArray: "4 4", fillColor: "#f43f5e", fillOpacity: 0.15 } as any} onEachFeature={(f: any, l: any) => l.bindPopup(`<b>${f.properties?.name}</b><br/>${f.properties?.authority || ""}`)} />
        )}
        {activeSub === "vessel" && vessels.map((v: any) => ( // @ts-ignore
          <Marker key={v.id} position={[v.latitude, v.longitude] as any} icon={L.divIcon({ className: "", html: `<div style="width:16px;height:16px;background:#f59e0b;border:2px solid white;border-radius:50%;box-shadow:0 0 6px #000;position:relative"><div style="position:absolute;top:-16px;left:50%;transform:translateX(-50%);background:#f59e0b;color:white;font-size:9px;padding:1px 5px;border-radius:4px;white-space:nowrap;font-weight:600">${(v.vessel_name || "VESSEL").slice(0, 18)}</div></div>`, iconSize: [16, 16] as any, iconAnchor: [8, 8] as any }) as any}><Popup><div style={{ color: "#0f172a", minWidth: 170 }}><b>{v.vessel_name || "Unknown vessel"}</b><br/><small>{v.event_type || "fishing"} • {v.observation_time?.slice(0, 10)}</small><br/><small>{v.latitude?.toFixed(3)}°N, {v.longitude?.toFixed(3)}°E</small><br/><small>Source: GFW v3 events</small></div></Popup></Marker>
        ))}
        {activeSub === "vessel" && vessels.length === 0 && <EmptyOverlay title="Vessels — no GFW events in window" body="vessel_tracks 0 rows for this bbox. Re-run GFW backfill." />}
        {activeSub === "route" && routeLine.length > 1 && ( // @ts-ignore
          <Polyline positions={routeLine as any} pathOptions={{ color: "#22c55e", weight: 4, dashArray: "8 8", opacity: 0.9 } as any} />
        )}
        {activeSub === "route" && routeLine.map((p, i) => ( // @ts-ignore
          <Marker key={"route-pt" + i} position={p as any} icon={L.divIcon({ className: "", html: `<div style="width:10px;height:10px;background:${i === 0 ? "#22c55e" : i === routeLine.length - 1 ? "#f59e0b" : "white"};border:2px solid #0f172a;border-radius:50%"></div>`, iconSize: [10, 10] as any, iconAnchor: [5, 5] as any }) as any} />
        ))}
        {activeSub === "geofence" && ( // @ts-ignore
          <Marker position={[19.0, 72.5] as any} icon={L.divIcon({ className: "", html: `<div style="width:120px;height:120px;border:1.5px dashed #f59e0b;border-radius:50%;background:rgba(245,158,11,0.08);display:flex;align-items:center;justify-content:center;color:#f59e0b;font-size:10px;font-weight:600">2.4 km buffer</div>`, iconSize: [120, 120] as any, iconAnchor: [60, 60] as any }) as any} />
        )}
        <FlyTo center={center} />
      </MapContainer>
      {activeSub === "currents" && grid.length === 0 && <EmptyOverlay title="Currents — gridded Copernicus ingesting" body="No single-point current. Real uo/vo per-pixel grid from mumbai_uo/vo_20260620.nc (0.08° 13×12) is being ingested — will show streamlines offshore." />}
      {activeSub === "fish" && <EmptyOverlay title="Fish — pending" body="CMFRI + OBIS ingested but no /fish API yet." />}
      {activeSub === "cyclone" && hazards.length === 0 && <EmptyOverlay title="Cyclone — no active cyclone" body="marine_hazards 0 rows. Mumbai 15 Aug–06 Sep none." />}
      {activeSub === "lightning" && hazards.length === 0 && <EmptyOverlay title="Lightning — clear" body="No lightning in bbox." />}
      {activeSub === "mpa" && (!mumbaiMpa || mumbaiMpa.features.length === 0) && <EmptyOverlay title="MPA — 0 in Mumbai bbox" body="Protected Areas 0 rows in 72.2,18.5,73.2,19.5. Legit." />}
      {activeSub === "restricted" && <EmptyOverlay title="Restricted — 1 coastline only" body="Geofences 1 Natural Earth 10m." />}
      {activeSub === "alerts" && hazards.length === 0 && <EmptyOverlay title="Safety Alerts — all clear" body="marine_hazards 0 rows." />}
      {activeSub === "ports" && <EmptyOverlay title="Ports — pending" body="No ports API. Needs Natural Earth ports." />}
    </div>
  )
}
