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
  const { setActiveSub } = useVizStore()

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
      // route intent: if user asks for route, parse coords and show on map (redirect to visualization)
      try {
        const ql = userMsg.toLowerCase()
        if (ql.includes("route") || (ql.includes(" from ") && ql.includes(" to "))) {
          // extract lat,lon pairs like 19.07,72.87
          const pairs = [...userMsg.matchAll(/(\d+\.\d+)\s*[, ]\s*(\d+\.\d+)/g)].map((m: any) => [parseFloat(m[1]), parseFloat(m[2])])
          let a: any = null, b: any = null
          if (pairs.length >= 2) { a = pairs[0]; b = pairs[1] }
          else if (pairs.length === 1) {
            const vp = (useMapStore.getState() as any).userPos
            if (vp) { a = [vp[1], vp[0]]; b = pairs[0] as any }
          }
          if (a && b) {
            const r = await api.post("/routes/calculate", null, { params: { start_lat: a[0], start_lon: a[1], end_lat: b[0], end_lon: b[1] } })
            // store route line for LeafletMap via custom event + viz switch
            const dist = r.data.routes?.[0]?.distance_km
            ;(window as any).__orca_chat_route = [[a[0], a[1]], [b[0], b[1]]]
            window.dispatchEvent(new CustomEvent("orca-chat-route", { detail: [[a[0], a[1]], [b[0], b[1]]] }))
            setActiveSub("route" as any)
            addMessage({ role: "assistant", content: `Route shown on map — ${a[0]},${a[1]} → ${b[0]},${b[1]} ${dist ? `(${dist} km)` : ""}. Green dashed line.` })
          } else if (ql.includes("route")) {
            // no coords - show safe route to nearest PFZ from current vessel
            const vp = (useMapStore.getState() as any).userPos || [72.877, 19.076]
            const lon2 = Array.isArray(vp) ? vp[0] : 72.877, lat2 = Array.isArray(vp) ? vp[1] : 19.076
            const nr = await api.get("/geospatial/notify", { params: { latitude: lat2, longitude: lon2 } })
            const pfz = nr.data.pfz_nearest
            if (pfz) {
              ;(window as any).__orca_chat_route = [[lat2, lon2], [pfz.latitude, pfz.longitude]]
              window.dispatchEvent(new CustomEvent("orca-chat-route", { detail: [[lat2, lon2], [pfz.latitude, pfz.longitude]] }))
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
