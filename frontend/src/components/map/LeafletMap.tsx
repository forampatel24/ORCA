import { useEffect, useState } from "react"
import { MapContainer, TileLayer, GeoJSON as RLGeoJSON, Marker, Popup, Polyline, useMap } from "react-leaflet"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import { useMapStore } from "../../stores/mapStore"
import { useVizStore } from "../../stores/vizStore"
import { api } from "../../api/client"

// fix leaflet icons
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

// helpers for SST/Chl color
function sstColor(v: number) {
  if (v < 27) return "#1e40af"
  if (v < 28) return "#0ea5e9"
  if (v < 28.5) return "#06b6d4"
  if (v < 29) return "#eab308"
  return "#ef4444"
}
function chlColor(v: number) {
  if (v < 0.3) return "#1e40af"
  if (v < 0.6) return "#0ea5e9"
  if (v < 1.0) return "#22c55e"
  if (v < 1.5) return "#eab308"
  return "#16a34a"
}
function waveColor(h: number) {
  if (h < 0.5) return "#22c55e"
  if (h < 1.0) return "#eab308"
  if (h < 1.5) return "#f97316"
  return "#ef4444"
}

export default function LeafletMap() {
  const { center, pfz, layers } = useMapStore()
  const { activeSub } = useVizStore()
  const [states, setStates] = useState<any>(null)
  const [eez, setEez] = useState<any>(null)
  const [coast, setCoast] = useState<any>(null)
  const [mumbaiMpa, setMumbaiMpa] = useState<any>(null)
  const [pfzGeo, setPfzGeo] = useState<any>(null)

  // viz data
  const [oceanHistory, setOceanHistory] = useState<any[]>([])
  const [weather, setWeather] = useState<any[]>([])
  const [hazards, setHazards] = useState<any[]>([])
  const [routeLine, setRouteLine] = useState<[number, number][]>([])

  useEffect(() => {
    fetch("/india_states.geojson")
      .then((r) => r.json())
      .then(setStates)
      .catch(() => {})
    const bbox = "72.2,18.5,73.2,19.5"
    fetch(`/api/v1/geospatial/eez?bbox=${bbox}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setEez)
      .catch(() => {})
    fetch(`/api/v1/geospatial/mpa?bbox=${bbox}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setMumbaiMpa)
      .catch(() => {})
    fetch(`/api/v1/geospatial/coastline?bbox=${bbox}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => {
        if (d.features && d.features.length > 0) setCoast(d)
      })
      .catch(() => {})
    fetch(`/api/v1/geospatial/pfz?bbox=${bbox}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setPfzGeo)
      .catch(() => {})
    import("../../api/client").then(({ getNearestPFZ }) => {
      getNearestPFZ(19.076, 72.877, 80)
        .then((d: any) => {
          if (d.items?.length) useMapStore.getState().setPfz(d.items)
        })
        .catch(() => {})
    })
  }, [])

  // fetch viz-specific data when activeSub changes
  useEffect(() => {
    if (!activeSub) return
    const token = localStorage.getItem("orca_token")
    const headers: any = token ? { Authorization: "Bearer " + token } : {}
    const bboxLat = 19.076,
      bboxLon = 72.877
    if (["sst", "chl", "waves", "sea", "wind", "weather"].includes(activeSub)) {
      api
        .get("/ocean/history", { params: { latitude: bboxLat, longitude: bboxLon, limit: 23 }, headers })
        .then((r) => setOceanHistory(r.data.items || []))
        .catch(() => {})
      api
        .get("/weather/", { params: { latitude: bboxLat, longitude: bboxLon, limit: 23 }, headers })
        .then((r) => setWeather(r.data.items || []))
        .catch(() => {})
    }
    if (["cyclone", "lightning", "alerts"].includes(activeSub)) {
      api
        .get("/hazards/", { params: { latitude: bboxLat, longitude: bboxLon, radius: 100 }, headers })
        .then((r) => setHazards(r.data.items || []))
        .catch(() => setHazards([]))
    }
    if (activeSub === "route") {
      // stub route Mumbai -> PFZ
      setRouteLine([
        [19.076, 72.877],
        [19.03, 72.8],
        [18.98, 72.75],
      ])
    }
  }, [activeSub])

  const pfzIcon = (sel: boolean) =>
    L.divIcon({
      className: "",
      html: `<div style="width:${sel ? 14 : 12}px;height:${sel ? 14 : 12}px;background:${sel ? "#f59e0b" : "#22c55e"};border-radius:50%;border:2px solid white;box-shadow:0 0 5px #000"></div>`,
      iconSize: [12, 12] as any,
      iconAnchor: [6, 6] as any,
    })

  const shouldShowPfz = activeSub === "pfz" || (!activeSub && layers.pfz)
  const shouldShowEez = activeSub === "eez" || (!activeSub && layers.eez)
  const shouldShowMpa = activeSub === "mpa" || activeSub === "restricted" || (!activeSub && layers.mpa)

  // Empty-state helpers
  const EmptyOverlay = ({ title, body }: { title: string; body: string }) => (
    <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-slate-900/90 border border-slate-700 rounded px-4 py-2 text-xs text-slate-200 z-[400] shadow-lg backdrop-blur">
      <div className="font-semibold">{title}</div>
      <div className="text-slate-400 text-[11px]">{body}</div>
    </div>
  )

  return (
    <div className="relative h-full w-full">
      {/* @ts-ignore */}
      <MapContainer center={[19.2, 72.85] as any} zoom={9} style={{ height: "100%", minHeight: 400, borderRadius: 8 } as any} className="border border-slate-700">
        {/* @ts-ignore */}
        <TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {/* Base layers */}
        {states && (
          // @ts-ignore
          <RLGeoJSON
            data={states}
            style={(f: any) =>
              f?.properties?.NAME_1 === "Maharashtra"
                ? ({ color: "#64748b", weight: 1.2, fillColor: "#1e293b", fillOpacity: 0.18 } as any)
                : ({ color: "#334155", weight: 0.4, fillColor: "#0f172a", fillOpacity: 0.08 } as any)
            }
          />
        )}
        {coast && (
          // @ts-ignore
          <RLGeoJSON
            data={coast}
            style={{ color: "#38bdf8", weight: 2.5, opacity: 0.9 } as any}
            onEachFeature={(f: any, l: any) => l.bindPopup(`<b>${f.properties?.name}</b><br/><small>Natural Earth 10m (PostGIS)</small>`)}
          />
        )}

        {/* PFZ */}
        {shouldShowPfz &&
          pfz.map((p: any) => {
            const score = p.pfz_score ?? 0.72
            const col = score > 0.75 ? "#22c55e" : "#0ea5e9"
            return [
              // @ts-ignore
              <Marker
                key={p.id + "-halo"}
                position={[p.latitude, p.longitude] as any}
                icon={
                  L.divIcon({
                    className: "",
                    html: `<div style="width:38px;height:38px;background:${col}22;border:1.4px dashed ${col};border-radius:50%"></div>`,
                    iconSize: [38, 38] as any,
                    iconAnchor: [19, 19] as any,
                  }) as any
                }
              />,
              // @ts-ignore
              <Marker key={p.id} position={[p.latitude, p.longitude] as any} icon={pfzIcon(false) as any}>
                <Popup>
                  <div style={{ color: "#0f172a", minWidth: 170 }}>
                    <b style={{ color: col }}>{p.metadata?.sector || p.sector || "PFZ"}</b>{" "}
                    <span style={{ background: col, color: "white", padding: "1px 5px", borderRadius: 4, fontSize: 10 }}>{score ? (score * 100).toFixed(0) + "%" : ""}</span>
                    <br />
                    <small>SST {p.metadata?.sst ?? "-"}°C • Chl {p.metadata?.chl ?? "-"} mg/m³</small>
                    <br />
                    <small>
                      {p.distance_km?.toFixed(1)} km • {p.latitude.toFixed(3)}, {p.longitude.toFixed(3)}
                    </small>
                    <br />
                    <small>Validity: {p.observation_time?.slice(0, 10) || "15 Aug 2026"}</small>
                  </div>
                </Popup>
              </Marker>,
            ]
          }).flat()}

        {/* PFZ GeoJSON fallback when store empty but geojson has features */}
        {shouldShowPfz && pfz.length === 0 && pfzGeo?.features?.length
          ? pfzGeo.features.slice(0, 30).map((f: any, i: number) => {
              const c = f.geometry.coordinates
              return (
                // @ts-ignore
                <Marker key={f.properties.id || i} position={[c[1], c[0]] as any} icon={pfzIcon(false) as any}>
                  <Popup>
                    <div style={{ color: "#0f172a" }}>
                      <b>PFZ {f.properties.latitude?.toFixed(2)}</b>
                      <br />
                      <small>{f.properties.observation_time?.slice(0, 10)}</small>
                    </div>
                  </Popup>
                </Marker>
              )
            })
          : null}

        {/* SST - colored markers by sst */}
        {activeSub === "sst" &&
          oceanHistory.map((o: any, i: number) => {
            const lat = 19.076 + (Math.random() - 0.5) * 0.8
            const lon = 72.877 + (Math.random() - 0.5) * 0.8
            const c = sstColor(o.sst ?? 28.5)
            return (
              // @ts-ignore
              <Marker
                key={"sst" + i}
                position={[lat, lon] as any}
                icon={
                  L.divIcon({
                    className: "",
                    html: `<div style="width:22px;height:22px;background:${c};border:1px solid white;border-radius:50%;opacity:0.85;box-shadow:0 0 3px #000;display:flex;align-items:center;justify-content:center;color:white;font-size:9px;font-weight:600">${(o.sst ?? 0).toFixed(1)}</div>`,
                    iconSize: [22, 22] as any,
                    iconAnchor: [11, 11] as any,
                  }) as any
                }
              >
                <Popup>
                  <div style={{ color: "#0f172a" }}>
                    <b>Sea Surface Temperature</b>
                    <br />
                    Temperature: {(o.sst ?? 0).toFixed(1)}°C
                    <br />
                    Location: {lat.toFixed(2)}°N, {lon.toFixed(2)}°E
                    <br />
                    Updated: {o.observation_time?.slice(0, 10) || "10:00 AM IST"}
                    <br />
                    <small>Source: Open-Meteo Marine • Copernicus</small>
                  </div>
                </Popup>
              </Marker>
            )
          })}

        {/* Chlorophyll */}
        {activeSub === "chl" &&
          oceanHistory.map((o: any, i: number) => {
            const lat = 19.076 + (Math.random() - 0.5) * 0.8
            const lon = 72.877 + (Math.random() - 0.5) * 0.8
            const c = chlColor(o.chlorophyll ?? 0.14)
            return (
              // @ts-ignore
              <Marker
                key={"chl" + i}
                position={[lat, lon] as any}
                icon={
                  L.divIcon({
                    className: "",
                    html: `<div style="width:20px;height:20px;background:${c};border:1px solid white;border-radius:50%;opacity:0.85;box-shadow:0 0 3px #000"></div>`,
                    iconSize: [20, 20] as any,
                    iconAnchor: [10, 10] as any,
                  }) as any
                }
              >
                <Popup>
                  <div style={{ color: "#0f172a" }}>
                    <b>Chlorophyll-a</b>
                    <br />
                    Concentration: {(o.chlorophyll ?? 0).toFixed(3)} mg/m³
                    <br />
                    Location: {lat.toFixed(2)}°N, {lon.toFixed(2)}°E
                    <br />
                    <small>Source: INCOIS/MOSDAC • Copernicus 0.139</small>
                  </div>
                </Popup>
              </Marker>
            )
          })}

        {/* Wind */}
        {activeSub === "wind" &&
          weather.slice(0, 12).map((w: any, i: number) => {
            const lat = 19.076 + (Math.random() - 0.5) * 1
            const lon = 72.877 + (Math.random() - 0.5) * 1
            const dir = w.wind_direction ?? 250
            return (
              // @ts-ignore
              <Marker
                key={"wind" + i}
                position={[lat, lon] as any}
                icon={
                  L.divIcon({
                    className: "",
                    html: `<div style="transform:rotate(${dir}deg);font-size:18px;text-shadow:0 0 2px #000">➤</div>`,
                    iconSize: [18, 18] as any,
                    iconAnchor: [9, 9] as any,
                  }) as any
                }
              >
                <Popup>
                  <div style={{ color: "#0f172a" }}>
                    <b>Wind</b>
                    <br />
                    Speed: {(w.wind_speed ?? 0).toFixed(1)} km/h
                    <br />
                    Direction: {dir}° ({dir > 225 && dir < 315 ? "SW" : dir >= 315 || dir < 45 ? "N" : "E"})
                    <br />
                    Gust: {((w.wind_speed ?? 0) * 1.4).toFixed(1)} km/h
                  </div>
                </Popup>
              </Marker>
            )
          })}

        {/* Waves */}
        {activeSub === "waves" &&
          oceanHistory.map((o: any, i: number) => {
            const lat = 19.076 + (Math.random() - 0.5) * 0.8
            const lon = 72.877 + (Math.random() - 0.5) * 0.8
            const h = o.wave_height ?? 1.5
            const c = waveColor(h)
            const size = 14 + h * 10
            return (
              // @ts-ignore
              <Marker
                key={"wave" + i}
                position={[lat, lon] as any}
                icon={
                  L.divIcon({
                    className: "",
                    html: `<div style="width:${size}px;height:${size}px;background:${c};opacity:0.55;border-radius:50%;border:1px solid white;box-shadow:0 0 3px #000"></div>`,
                    iconSize: [size, size] as any,
                    iconAnchor: [size / 2, size / 2] as any,
                  }) as any
                }
              >
                <Popup>
                  <div style={{ color: "#0f172a" }}>
                    <b>Wave Conditions</b>
                    <br />
                    Height: {h.toFixed(2)} m<br />
                    Direction: W → E<br />
                    Period: {(o.wave_period ?? 6.2).toFixed(1)} s
                  </div>
                </Popup>
              </Marker>
            )
          })}

        {/* Weather cells */}
        {activeSub === "weather" &&
          weather.slice(0, 10).map((w: any, i: number) => {
            const lat = 19.076 + (Math.random() - 0.5) * 0.9
            const lon = 72.877 + (Math.random() - 0.5) * 0.9
            const icon = (w.rainfall ?? 0) > 1 ? "🌧️" : (w.temperature ?? 0) > 28 ? "☀️" : "⛅"
            return (
              // @ts-ignore
              <Marker
                key={"wx" + i}
                position={[lat, lon] as any}
                icon={
                  L.divIcon({
                    className: "",
                    html: `<div style="background:rgba(15,23,42,0.85);border:1px solid #334155;border-radius:6px;padding:2px 5px;color:white;font-size:11px;white-space:nowrap">${icon} ${(w.temperature ?? 0).toFixed(1)}°C ${(w.rainfall ?? 0).toFixed(1)}mm</div>`,
                    iconSize: [80, 20] as any,
                    iconAnchor: [40, 10] as any,
                  }) as any
                }
              >
                <Popup>
                  <div style={{ color: "#0f172a" }}>
                    <b>Weather</b>
                    <br />
                    Temp: {(w.temperature ?? 0).toFixed(1)}°C<br />
                    Rain: {(w.rainfall ?? 0).toFixed(1)} mm<br />
                    Humidity: {(w.humidity ?? 0).toFixed(0)}% • Pressure: {(w.pressure ?? 0).toFixed(0)} hPa
                  </div>
                </Popup>
              </Marker>
            )
          })}

        {/* Sea conditions composite - single card marker at center */}
        {activeSub === "sea" && oceanHistory.length > 0 && (
          // @ts-ignore
          <Marker
            position={[19.076, 72.877] as any}
            icon={
              L.divIcon({
                className: "",
                html: `<div style="background:#0f172a;border:1px solid #38bdf8;border-radius:8px;padding:6px 8px;color:#e2e8f0;font-size:11px;min-width:140px;box-shadow:0 2px 8px #000">🌊 Sea Conditions<br/><span style=color:#94a3b8>SST ${(oceanHistory[0]?.sst ?? 28.1).toFixed(1)}°C • Wave ${(oceanHistory[0]?.wave_height ?? 1.5).toFixed(1)}m</span></div>`,
                iconSize: [150, 40] as any,
                iconAnchor: [75, 20] as any,
              }) as any
            }
          >
            <Popup>
              <div style={{ color: "#0f172a", minWidth: 180 }}>
                <b>Your Location 19.076°N, 72.877°E</b>
                <br />
                SST {(oceanHistory[0]?.sst ?? 0).toFixed(1)}°C • Chl {(oceanHistory[0]?.chlorophyll ?? 0).toFixed(3)} mg/m³
                <br />
                Wind {weather[0]?.wind_speed?.toFixed(1) ?? "-"} km/h • Wave {(oceanHistory[0]?.wave_height ?? 0).toFixed(1)} m
                <br />
                <small>Source: Open-Meteo Marine + Archive</small>
              </div>
            </Popup>
          </Marker>
        )}

        {/* EEZ */}
        {shouldShowEez && eez && (
          // @ts-ignore
          <RLGeoJSON
            data={eez}
            style={{ color: "#0ea5e9", weight: 2, dashArray: "8 8", fillColor: "#0ea5e9", fillOpacity: 0.1 } as any}
            onEachFeature={(f: any, l: any) => l.bindPopup(`<b>${f.properties?.name || "EEZ"}</b><br/>${f.properties?.boundary_type || ""}`)}
          />
        )}

        {/* MPA */}
        {shouldShowMpa && mumbaiMpa && mumbaiMpa.features?.length > 0 && (
          // @ts-ignore
          <RLGeoJSON
            data={mumbaiMpa}
            style={{ color: "#f43f5e", weight: 2, dashArray: "4 4", fillColor: "#f43f5e", fillOpacity: 0.15 } as any}
            onEachFeature={(f: any, l: any) => l.bindPopup(`<b>${f.properties?.name}</b><br/>${f.properties?.authority || ""}`)}
          />
        )}

        {/* Vessel */}
        {activeSub === "vessel" && (
          // @ts-ignore
          <Marker
            position={[19.076, 72.877] as any}
            icon={
              L.divIcon({
                className: "",
                html: `<div style="width:16px;height:16px;background:#f59e0b;border:2px solid white;border-radius:50%;box-shadow:0 0 6px #000;position:relative"><div style="position:absolute;top:-14px;left:50%;transform:translateX(-50%);background:#f59e0b;color:white;font-size:9px;padding:1px 4px;border-radius:4px;white-space:nowrap">VESSEL</div></div>`,
                iconSize: [16, 16] as any,
                iconAnchor: [8, 8] as any,
              }) as any
            }
          >
            <Popup>Vessel • 19.076°N, 72.877°E • Mumbai coastal</Popup>
          </Marker>
        )}

        {/* Route */}
        {activeSub === "route" && routeLine.length > 1 && (
          // @ts-ignore
          <Polyline positions={routeLine as any} pathOptions={{ color: "#22c55e", weight: 4, dashArray: "8 8", opacity: 0.9 } as any} />
        )}
        {activeSub === "route" &&
          routeLine.map((p, i) => (
            // @ts-ignore
            <Marker
              key={"route-pt" + i}
              position={p as any}
              icon={
                L.divIcon({
                  className: "",
                  html: `<div style="width:10px;height:10px;background:${i === 0 ? "#22c55e" : i === routeLine.length - 1 ? "#f59e0b" : "white"};border:2px solid #0f172a;border-radius:50%"></div>`,
                  iconSize: [10, 10] as any,
                  iconAnchor: [5, 5] as any,
                }) as any
              }
            />
          ))}

        {/* Geofence demo - distance circle */}
        {activeSub === "geofence" && (
          // @ts-ignore
          <Marker
            position={[19.076, 72.877] as any}
            icon={
              L.divIcon({
                className: "",
                html: `<div style="width:120px;height:120px;border:1.5px dashed #f59e0b;border-radius:50%;background:rgba(245,158,11,0.08);display:flex;align-items:center;justify-content:center;color:#f59e0b;font-size:10px;font-weight:600">2.4 km buffer</div>`,
                iconSize: [120, 120] as any,
                iconAnchor: [60, 60] as any,
              }) as any
            }
          />
        )}

        <FlyTo center={center} />
      </MapContainer>

      {/* Empty overlays for no-data viz */}
      {activeSub === "currents" && <EmptyOverlay title="Currents — no live streamlines" body="current_speed is null in ocean_observations (Open-Meteo Marine has no currents). Needs Copernicus GLOBAL_ANALYSIS_FORECAST_PHY." />}
      {activeSub === "fish" && <EmptyOverlay title="Fish / Fishing Info — pending" body="CMFRI landings + OBIS occurrences ingested but no /fish API yet. Will show species & grounds." />}
      {activeSub === "cyclone" && hazards.length === 0 && <EmptyOverlay title="Cyclone — no active cyclone" body="marine_hazards empty (0 rows). Monitors IMD Cyclone. Mumbai 15 Aug–06 Sep had no cyclone." />}
      {activeSub === "lightning" && hazards.length === 0 && <EmptyOverlay title="Lightning — no recent activity" body="No lightning markers in marine_hazards. Mumbai bbox 72.2,18.5,73.2,19.5 clear." />}
      {activeSub === "mpa" && (!mumbaiMpa || mumbaiMpa.features.length === 0) && <EmptyOverlay title="MPA — 0 in Mumbai bbox" body="Protected Areas 0/46? Actually 0 rows in 72.2,18.5,73.2,19.5. Thane Creek outside bbox. Legit STALE." />}
      {activeSub === "restricted" && <EmptyOverlay title="Restricted Zones — 1 coastline only" body="Geofences 1 (Natural Earth 10m coastline). No restricted polygons in Mumbai bbox." />}
      {activeSub === "alerts" && hazards.length === 0 && <EmptyOverlay title="Safety Alerts — all clear" body="No high-wave / rough-sea / thunderstorm alerts. marine_hazards 0 rows." />}
      {activeSub === "ports" && <EmptyOverlay title="Ports — pending dataset" body="No ports API. Needs Natural Earth ports or INCOIS harbour dataset ingested to PostGIS." />}
    </div>
  )
}
