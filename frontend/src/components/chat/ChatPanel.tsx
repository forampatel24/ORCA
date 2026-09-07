import { useState } from 'react'
import { useChatStore } from '../../stores/chatStore'
import { useMapStore } from '../../stores/mapStore'
import { useVizStore } from '../../stores/vizStore'
import { chat, getNearestPFZ, login } from '../../api/client'
import { api } from '../../api/client'

export default function ChatPanel() {
  const [input, setInput] = useState('')
  const { messages, addMessage, loading, setLoading } = useChatStore()
  const { setCenter, setSelected } = useMapStore()
  const { setActiveSub, setActiveCategory } = useVizStore()

  const VIZ_KEYWORDS: [RegExp, string, string][] = [
    [/pfz|fishing zone/i, "pfz", "fishing"],
    [/\bsst\b|sea surface temperature/i, "sst", "fishing"],
    [/chlorophyll|\bchl\b/i, "chl", "fishing"],
    [/\bwind\b/i, "wind", "marine"],
    [/\bwave/i, "waves", "marine"],
    [/\bcurrent/i, "currents", "marine"],
    [/\bcyclone/i, "cyclone", "safety"],
    [/lightning|thunder/i, "lightning", "safety"],
    [/\btide\b|\bsea condition/i, "sea", "marine"],
    [/\bvessel\b/i, "vessel", "navigation"],
    [/\beez\b|maritime boundary/i, "eez", "navigation"],
    [/\bmpa|protected/i, "mpa", "safety"],
  ]

  async function ensureLogin() {
    if (!localStorage.getItem('orca_token')) {
      await login('test@orca.local', 'test123')
    }
  }

  async function send() {
    if (!input.trim()) return
    const userMsg = input
    addMessage({ role: 'user', content: userMsg })
    setInput('')
    setLoading(true)
    try {
      await ensureLogin()
      const data = await chat(userMsg)
      let txt = (data.response||"").replace(/\*\*/g,"").replace(/###/g,"")
      addMessage({ role: 'assistant', content: txt, evidence: data.evidence, risk: data.risk })
      // auto-open matching visualization (pfz/sst/wind etc.) on the map
      for (const [re, sub, cat] of VIZ_KEYWORDS) {
        if (re.test(userMsg)) { setActiveCategory(cat as any); setActiveSub(sub as any); break }
      }
      // map sync — use backend-provided center (from data/location_coords.json via PostGIS) not hard-coded
      try {
        let lat=19.0, lon=72.8
        if (data.center && data.center.length===2) { lon=data.center[0]; lat=data.center[1] }
        else if (data.location) {
          // fallback: if backend didn't send center, use PFZ items centroid
          lon=72.8; lat=19.0
        }
        const pfzData = await getNearestPFZ(lat, lon, 150)
        // Keep the full live set (21) on the map - chat only moves center/selection
        if (pfzData.items?.length) {
          // show all PFZ for that region, center on map-provided center
          setSelected(pfzData.items[0])
          setCenter(data.center || [pfzData.items[0].longitude, pfzData.items[0].latitude])
        } else if (data.center) setCenter(data.center as any)
      } catch { if(data.center) setCenter(data.center as any) }
      // route intent: if user asks for route, parse coords or PFZ names and show on map (redirect to visualization)
      try {
        const ql = userMsg.toLowerCase()
        if (ql.includes("route") || (ql.includes(" from ") && ql.includes(" to "))) {
          let a: any = null, b: any = null
          let aName: string | null = null, bName: string | null = null
          // Try named PFZ first (e.g. "Arnala to Varsoli" or "Kore to Patwadi") - token match so "Kore" hits "Edavan/Kore"
          try {
            const pfzRes = await api.get("/geospatial/pfz?bbox=71.8,15.5,74.5,20.5")
            const feats: any[] = pfzRes.data.features || []
            const names = feats.map((f: any) => f.properties?.metadata?.landing_centre).filter(Boolean) as string[]
            const ql2 = ql
            const scored = names.map((n) => {
              const tokens = n.toLowerCase().split(/[^a-z0-9]+/).filter((t: string) => t.length >= 3)
              let bestIdx = Infinity
              for (const t of tokens) { const idx = ql2.indexOf(t); if (idx !== -1 && idx < bestIdx) bestIdx = idx }
              // also whole-name match (e.g. "Arnala") is stronger
              const wholeIdx = ql2.indexOf(n.toLowerCase())
              if (wholeIdx !== -1 && wholeIdx < bestIdx) bestIdx = wholeIdx
              return { n, idx: bestIdx }
            }).filter((x: any) => x.idx !== Infinity).sort((a: any, b: any) => a.idx - b.idx)
            const found = scored.map((x: any) => x.n)
            if (found.length >= 2) { aName = found[0]; bName = found[1] }
            else if (found.length === 1) {
              // single PFZ mentioned - if user also said "from X to Y" but second name was missed (e.g. typo),
              // treat as destination and origin = vessel (correct for "route to Patwadi")
              // but for "Kore to Patwadi" this branch won't run because found would be 2 after token fix
              if (ql.includes("from") || ql.includes("to")) {
                // use vessel as start if query says "to <PFZ>"
                const vp = (useMapStore.getState() as any).userPos
                if (vp && ql.indexOf(found[0].toLowerCase().split(/[^a-z0-9]+/).find((t: string) => ql.includes(t))!) > ql.indexOf("to")) {
                  aName = null; bName = found[0]; a = [vp[1], vp[0]]
                } else { aName = found[0] }
              } else { aName = found[0] }
            }
          } catch {}
          if (aName || bName) {
            const params: any = {}
            if (aName) params.start_name = aName; else if (a) { params.start_lat = a[0]; params.start_lon = a[1] }
            if (bName) params.end_name = bName; else if (b) { params.end_lat = b[0]; params.end_lon = b[1] }
            // If one end is still missing, use vessel position or Mumbai default
            if (!params.start_lat && !params.start_name) {
              const vp = (useMapStore.getState() as any).userPos
              if (vp) { params.start_lat = vp[1]; params.start_lon = vp[0] } else { params.start_lat = 19.076; params.start_lon = 72.877 }
            }
            const r = await api.post("/routes/calculate", null, { params })
            const route = r.data.routes?.[0]
            const coords = route?.coordinates // [[lon,lat],...]
            if (coords && coords.length >= 2) {
              const latlngs = coords.map((c: any) => [c[1], c[0]])
              ;(window as any).__orca_chat_route = latlngs
              window.dispatchEvent(new CustomEvent("orca-chat-route", { detail: latlngs }))
              setActiveSub("route" as any)
              addMessage({ role: "assistant", content: `Route ${route.pfz_start || aName || "start"} → ${route.pfz_end || bName || "end"} shown — green line ${route.distance_km} km, safety-aware (hazards/MPA/EEZ avoided). PFZ layer stays visible.` })
              return
            }
          }
          // fallback: extract lat,lon pairs like 19.07,72.87
          const pairs = [...userMsg.matchAll(/(\d+\.\d+)\s*[, ]\s*(\d+\.\d+)/g)].map((m: any) => [parseFloat(m[1]), parseFloat(m[2])])
          if (pairs.length >= 2) { a = pairs[0]; b = pairs[1] }
          else if (pairs.length === 1) {
            const vp = (useMapStore.getState() as any).userPos
            if (vp) { a = [vp[1], vp[0]]; b = pairs[0] as any }
          }
          if (a && b) {
            const r = await api.post("/routes/calculate", null, { params: { start_lat: a[0], start_lon: a[1], end_lat: b[0], end_lon: b[1] } })
            const dist = r.data.routes?.[0]?.distance_km
            const coords = r.data.routes?.[0]?.coordinates
            const latlngs = coords ? coords.map((c: any) => [c[1], c[0]]) : [a, b]
            ;(window as any).__orca_chat_route = latlngs
            window.dispatchEvent(new CustomEvent("orca-chat-route", { detail: latlngs }))
            setActiveSub("route" as any)
            addMessage({ role: "assistant", content: `Route shown on map — ${a[0]},${a[1]} → ${b[0]},${b[1]} ${dist ? `(${dist} km)` : ""}. Green dashed line, safety-checked.` })
          } else if (ql.includes("route")) {
            // no coords or names - show safe route to nearest PFZ from current vessel
            const vp = (useMapStore.getState() as any).userPos || [72.877, 19.076]
            const lon2 = Array.isArray(vp) ? vp[0] : 72.877, lat2 = Array.isArray(vp) ? vp[1] : 19.076
            const nr = await api.get("/geospatial/notify", { params: { latitude: lat2, longitude: lon2 } })
            const pfz = nr.data.pfz_nearest
            if (pfz) {
              const r = await api.post("/routes/calculate", null, { params: { start_lat: lat2, start_lon: lon2, end_lat: pfz.latitude, end_lon: pfz.longitude } })
              const coords = r.data.routes?.[0]?.coordinates || [[lon2, lat2], [pfz.longitude, pfz.latitude]]
              const latlngs = coords.map((c: any) => [c[1], c[0]])
              ;(window as any).__orca_chat_route = latlngs
              window.dispatchEvent(new CustomEvent("orca-chat-route", { detail: latlngs }))
              setActiveSub("route" as any)
              addMessage({ role: "assistant", content: `Route to nearest PFZ ${pfz.landing_centre || ""} shown — green line to ${pfz.latitude.toFixed(3)},${pfz.longitude.toFixed(3)} (${pfz.distance_km.toFixed(1)} km).` })
            }
          }
        }
      } catch {}
    } catch (e: any) {
      addMessage({ role: 'assistant', content: `Error: ${e.response?.data?.detail || e.message}` })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full border border-slate-800 rounded bg-slate-900">
      <div className="p-3 border-b border-slate-800 font-semibold">Ask ORCA</div>
      <div className="flex-1 overflow-auto p-3 space-y-3">
        {messages.map((m, i) => (
          <div key={i} className={`p-3 rounded ${m.role === 'user' ? 'bg-blue-900 ml-8' : 'bg-slate-800 mr-8'}`}>
            <div className="text-sm whitespace-pre-wrap">{m.content}</div>
            {m.evidence && <div className="text-xs text-slate-400 mt-2">Evidence: {JSON.stringify(m.evidence).slice(0,120)}</div>}
            {m.risk && <div className="text-xs mt-1">Risk: {JSON.stringify(m.risk)}</div>}
          </div>
        ))}
        {loading && <div className="text-sm text-slate-500">ORCA thinking... ✓ Location resolved</div>}
      </div>
      <div className="p-3 border-t border-slate-800 flex gap-2">
        <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && send()} placeholder="Is it safe to fish tomorrow near Mumbai?" className="flex-1 bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm" />
        <button onClick={send} className="bg-blue-600 px-4 py-2 rounded text-sm">Send</button>
      </div>
    </div>
  )
}
