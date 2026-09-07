import { useState, useEffect, useRef } from "react"
import { useMapStore } from "../../stores/mapStore"

export default function VesselPositionBar() {
  const { userPos, setUserPos } = useMapStore()
  const [lat, setLat] = useState("19.076")
  const [lon, setLon] = useState("72.877")
  const [notify, setNotify] = useState<any>(null)
  const [toasts, setToasts] = useState<any[]>([])
  const prevCodes = useRef<string>("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (userPos) { setLat(userPos[1].toFixed(3)); setLon(userPos[0].toFixed(3)) }
  }, [userPos])

  async function apply() {
    const la = parseFloat(lat), lo = parseFloat(lon)
    if (Number.isNaN(la) || Number.isNaN(lo)) return
    setUserPos([lo, la])
  }

  function pushToasts(next: any) {
    if (!next) return
    const codes = (next.notifications || []).map((n: any) => n.code).sort().join("|")
    if (codes !== prevCodes.current && next.notifications.length) {
      prevCodes.current = codes
      const id = Date.now()
      setToasts((t) => [...t, { id, items: next.notifications, point: next.point }])
      setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 6000)
    } else if (!next.notifications.length) {
      prevCodes.current = ""
    }
  }

  // Poll notify when user drags marker
  useEffect(() => {
    if (!userPos) return
    const la = userPos[1], lo = userPos[0]
    setLat(la.toFixed(3)); setLon(lo.toFixed(3))
    setLoading(true)
    fetch(`/api/v1/geospatial/notify?latitude=${la}&longitude=${lo}`)
      .then((r) => (r.ok ? r.json() : null)).then((j) => { setNotify(j); pushToasts(j); if (j?.safe_route) (window as any).__orca_safe_route = j.safe_route; else (window as any).__orca_safe_route = null; window.dispatchEvent(new CustomEvent("orca-safe-route", { detail: j?.safe_route })) }).catch(() => {}).finally(() => setLoading(false))
  }, [userPos?.[0], userPos?.[1]])

  const statusColor = notify?.status === "critical" ? "border-red-500 bg-red-900/30 text-red-300"
    : notify?.status === "warning" ? "border-amber-500 bg-amber-900/30 text-amber-300"
    : notify?.status === "info" ? "border-sky-500 bg-sky-900/30 text-sky-300"
    : "border-slate-700 bg-slate-900 text-slate-400"

  return (
    <div className="border-b border-slate-800 bg-slate-900 px-3 py-2">
      <div className="flex items-center gap-2 text-xs">
        <span className="font-semibold tracking-wide">VESSEL POSITION</span>
        <span className="text-slate-500 hidden sm:inline">Enter Mumbai coords (we are not in Mumbai — no GPS)</span>
        <span className="ml-auto text-[10px] text-slate-500 hidden md:inline">Drag marker on map also updates</span>
      </div>
      <div className="mt-2 flex gap-2">
        <input value={lat} onChange={(e) => setLat(e.target.value)} placeholder="Lat e.g. 19.076" className="w-28 bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs" />
        <input value={lon} onChange={(e) => setLon(e.target.value)} placeholder="Lon e.g. 72.877" className="w-28 bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs" />
        <button onClick={apply} className="bg-sky-600 hover:bg-sky-700 px-3 py-1 rounded text-xs font-medium">Set</button>
        <button onClick={() => { setLat("19.076"); setLon("72.877"); setUserPos([72.877, 19.076]) }} className="bg-slate-700 hover:bg-slate-600 px-2 py-1 rounded text-xs">Mumbai</button>
        <button onClick={() => { setUserPos(null); setNotify(null) }} className="text-[11px] text-slate-500 hover:text-slate-300 px-1">clear</button>
      </div>
      {/* Notifications - strictly when entering hazardous / boundary zones */}
      {loading && <div className="mt-2 text-[11px] text-slate-500">Checking geofence…</div>}
      {notify && (
        <div className={`mt-2 rounded border px-2 py-2 text-[11px] ${statusColor}`}>
          <div className="flex justify-between items-center">
            <span className="font-semibold uppercase">{notify.status ?? "info"} • {notify.point.lat.toFixed(3)}, {notify.point.lon.toFixed(3)}</span>
            <span className="text-[10px] opacity-60">PFZ {notify.pfz_nearest ? `${notify.pfz_nearest.distance_km.toFixed(1)} km` : "—"} • EEZ {notify.eez_inside ? "inside" : notify.eez_inside === false ? "outside" : "—"} • Hazards {notify.hazards.length}</span>
          </div>
          {notify.notifications.length === 0 && <div className="mt-1 opacity-70">No boundary/hazard triggered — {notify.suggestion}</div>}
          {notify.notifications.map((n: any, i: number) => (
            <div key={i} className="mt-1 flex gap-1">
              <span>{n.level === "critical" ? "⛔" : n.level === "warning" ? "⚠️" : "ℹ️"}</span>
              <span>{n.message}</span>
            </div>
          ))}
          {notify.suggestion && notify.notifications.length > 0 && <div className="mt-1 opacity-70">Suggestion: {notify.suggestion}</div>}
          <div className="mt-1 text-[10px] opacity-40">Geofence: {notify.geo.inside_geofence || "—"} • Nearest: {notify.geo.nearest_geofence ? `${notify.geo.nearest_geofence} ${notify.geo.distance_to_nearest_km?.toFixed(1)} km` : "—"} • EEZ {notify.eez_inside === false ? `outside ${notify.eez_distance_km?.toFixed(1)} km beyond` : notify.eez_inside ? `${notify.eez_distance_km?.toFixed(1)} km to boundary` : "—"} • PFZ {notify.pfz_nearest ? `${notify.pfz_nearest.distance_km.toFixed(1)} km ${notify.pfz_nearest.landing_centre || ""}` : "—"}</div>
        </div>
      )}
      {/* Immediate alert - CENTER of screen, big, with safe route directions */}
      {toasts.length > 0 && (
        <div className="fixed inset-0 z-[600] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4" onClick={() => setToasts([])}>
          <div className="max-w-lg w-full bg-slate-900 border-2 border-amber-500 rounded-xl shadow-2xl p-5" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-start gap-2">
              <div className="text-lg font-bold text-amber-400">⚠️ Maritime Alert</div>
              <button onClick={() => setToasts([])} className="text-slate-400 hover:text-white text-xl leading-none">×</button>
            </div>
            <div className="text-[11px] text-slate-500 mt-1">{toasts[0].point.lat.toFixed(3)}, {toasts[0].point.lon.toFixed(3)} • {new Date().toLocaleTimeString("en-IN", { timeZone: "Asia/Kolkata" })} IST</div>
            {toasts[0].items.map((n: any, i: number) => (
              <div key={i} className={`mt-3 rounded border px-3 py-2 text-sm ${n.level === "critical" ? "border-red-500 bg-red-900/30 text-red-200" : n.level === "warning" ? "border-amber-500 bg-amber-900/30 text-amber-200" : "border-sky-600 bg-sky-900/30 text-sky-200"}`}>
                <div className="font-semibold">{n.level === "critical" ? "⛔" : n.level === "warning" ? "⚠️" : "ℹ️"} {n.code.replaceAll("_"," ")}</div>
                <div className="mt-1">{n.message}</div>
                {n.distance_km != null && <div className="text-[11px] opacity-60 mt-1">{n.distance_km.toFixed(1)} km away {n.hazard?.title ? `• ${n.hazard.title}` : ""}</div>}
              </div>
            ))}
            {notify?.safe_route && (
              <div className="mt-4 rounded bg-emerald-900/30 border border-emerald-700 px-3 py-3">
                <div className="text-sm font-semibold text-emerald-300">🧭 Safe navigation — green dashed line on map</div>
                <div className="text-xs text-emerald-200 mt-1">{notify.safe_route.instruction}</div>
                <div className="text-[11px] text-emerald-400/70 mt-1">Distance to safety: {notify.safe_route.distance_km?.toFixed(1)} km • Target: {notify.safe_route.target}</div>
                <div className="text-[11px] text-slate-400 mt-1">Follow the green dashed route on the map. Drag the marker along it to update live.</div>
              </div>
            )}
            {notify?.suggestion && <div className="mt-3 text-xs text-slate-300">Suggestion: {notify.suggestion}</div>}
            <div className="mt-4 flex gap-2">
              <button onClick={() => setToasts([])} className="flex-1 bg-slate-700 hover:bg-slate-600 rounded py-2 text-sm">Acknowledge</button>
              {notify?.safe_route && <button onClick={() => { setToasts([]); document.querySelector('[data-testid="map-container"]')?.scrollIntoView({ behavior: "smooth" }) }} className="flex-1 bg-emerald-600 hover:bg-emerald-700 rounded py-2 text-sm font-medium">Show on map</button>}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
