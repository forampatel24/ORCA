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
      for (const [re, sub, cat] of VIZ_KEYWORDS) {
        if (re.test(userMsg)) { setActiveCategory(cat as any); setActiveSub(sub as any); break }
      }
      try {
        let lat=19.0, lon=72.8
        if (data.center && data.center.length===2) { lon=data.center[0]; lat=data.center[1] }
        else if (data.location) { lon=72.8; lat=19.0 }
        const pfzData = await getNearestPFZ(lat, lon, 150)
        if (pfzData.items?.length) {
          setSelected(pfzData.items[0])
          setCenter(data.center || [pfzData.items[0].longitude, pfzData.items[0].latitude])
        } else if (data.center) setCenter(data.center as any)
      } catch { if(data.center) setCenter(data.center as any) }
      try {
        const ql = userMsg.toLowerCase()
        const isRoute = ql.includes("route") || ql.includes("मार्ग") || ql.includes("रूट") || ql.includes("रस्ता") || (ql.includes(" from ") && ql.includes(" to ")) || (ql.includes("पासून") && (ql.includes("पर्यंत") || ql.includes("ते")))
        if (isRoute) {
          const evRoute = (data.evidence as any)?.route_live || (data as any)?.route_live
          if (evRoute?.coordinates && evRoute.coordinates.length >= 2) {
            const latlngs = evRoute.coordinates.map((c: any) => [c[1], c[0]])
            ;(window as any).__orca_chat_route = latlngs
            ;(window as any).__orca_chat_instructions = evRoute.instructions || []
            window.dispatchEvent(new CustomEvent("orca-chat-route", { detail: latlngs }))
            window.dispatchEvent(new CustomEvent("orca-chat-instructions", { detail: evRoute.instructions || [] }))
            setActiveSub("route" as any)
            const mid = latlngs[Math.floor(latlngs.length/2)]
            setCenter([mid[1], mid[0]] as any)
          } else {
            let aName: string | null = null, bName: string | null = null
            const DEV_TO_EN: Record<string, string> = {
              "एडावण": "Edavan/Kore", "कोरे": "Edavan/Kore",
              "पटवाडी": "Patwadi", "अरनाळा": "Arnala", "आर्णाला": "Arnala",
              "टेंभी": "Tembhi", "मलबार": "Malabar Port (Mumbai)", "वरळी": "Worli",
              "ससून": "SasoonDock", "कालबादेवी": "Kalbadevi", "चिंचबंदर": "Chinchbunder",
              "न्यू फेरी": "NewFerryWharf", "ससवणे": "Sasawane", "कोलाबा": "Colaba Pt.(Mumbai)",
              "नवगाव": "Navgaon", "थाळ": "Thal", "वरसोली": "VarsoliChalmala",
              "अलिबाग": "Alibag", "नागाव": "Nagaon", "रेवदंडा": "Revadanda", "कोर्लई": "Korlai", "मालवण": "Malvan Marine Sanctuary Maharashtra",
            }
            try {
              const pfzRes = await api.get("/geospatial/pfz?bbox=71.8,15.5,74.5,20.5")
              const feats: any[] = pfzRes.data.features || []
              const names = feats.map((f: any) => f.properties?.metadata?.landing_centre).filter(Boolean) as string[]
              const devHits: string[] = []
              for (const [dev, en] of Object.entries(DEV_TO_EN)) { if (userMsg.includes(dev) && !devHits.includes(en)) devHits.push(en) }
              if (devHits.length >= 2) { aName = devHits[0]; bName = devHits[1] }
              else if (devHits.length === 1) {
                aName = devHits[0]
                // need second PFZ from English part after "to"
                const toIdx = Math.max(ql.indexOf(" to "), ql.indexOf(" ते "), ql.indexOf(" पर्यंत "))
                const afterTo = toIdx !== -1 ? ql.substring(toIdx + 4) : ""
                if (afterTo) {
                  for (const n of names) {
                    const low = n.toLowerCase()
                    if (afterTo.includes(low) || low.split(/[^a-z0-9]+/).some(t => t.length>=3 && afterTo.includes(t))) { bName = n; break }
                  }
                }
              } else {
                // English: split into from-part and to-part to avoid Worli vs Worli-Lotus clash at same idx
                const toIdx = ql.indexOf(" to ")
                const fromPart = toIdx !== -1 ? ql.substring(0, toIdx) : ql
                const toPart = toIdx !== -1 ? ql.substring(toIdx + 4) : ""
                const scorePart = (part: string) => {
                  let best: string | null = null, bestIdx = Infinity, bestWhole = false
                  for (const n of names) {
                    const low = n.toLowerCase()
                    const wholeIdx = part.indexOf(low)
                    let curIdx = wholeIdx !== -1 ? wholeIdx : Infinity
                    let curWhole = wholeIdx !== -1
                    if (!curWhole) {
                      const toks = low.split(/[^a-z0-9]+/).filter(t=>t.length>=3)
                      for (const t of toks) { const idx = part.indexOf(t); if (idx!==-1 && idx < curIdx) { curIdx = idx; curWhole = false } }
                    }
                    if (curIdx!==Infinity && (curIdx < bestIdx || (curIdx===bestIdx && curWhole && !best)) ) { best = n; bestIdx = curIdx; bestWhole = curWhole }
                  }
                  return best
                }
                if (toIdx !== -1) {
                  aName = scorePart(fromPart)
                  bName = scorePart(toPart)
                } else {
                  // no explicit from/to, pick two earliest distinct PFZs in query, deduped by position
                  const scored = names.map(n => {
                    const low=n.toLowerCase()
                    const wholeIdx=ql.indexOf(low)
                    let bIdx=wholeIdx!==-1?wholeIdx:Infinity
                    let isW=wholeIdx!==-1
                    if(!isW){ const toks=low.split(/[^a-z0-9]+/).filter(t=>t.length>=3); for(const t of toks){const idx=ql.indexOf(t); if(idx!==-1 && idx<bIdx){bIdx=idx}} }
                    return {n, idx:bIdx, isWhole:isW, len:n.length}
                  }).filter(x=>x.idx!==Infinity).sort((a,b)=>a.idx-b.idx || (b.isWhole as any)-(a.isWhole as any) || a.len-b.len)
                  const uniq: string[]=[]; const seen=new Set<number>()
                  for(const s of scored){ if(!seen.has(s.idx)){ uniq.push(s.n); seen.add(s.idx)} }
                  if(uniq.length>=2){ aName=uniq[0]; bName=uniq[1] } else if(uniq.length===1){ aName=uniq[0] }
                }
              }
            } catch {}
            if (aName || bName) {
              const params: any = {}
              if (aName) params.start_name = aName
              if (bName) params.end_name = bName
              if (!params.start_name) {
                const vp = (useMapStore.getState() as any).userPos
                if (vp) { params.start_lat = vp[1]; params.start_lon = vp[0] } else { params.start_lat = 19.076; params.start_lon = 72.877 }
              }
              const r = await api.post("/routes/calculate", null, { params })
              const route = r.data.routes?.[0]
              const coords = route?.coordinates
              if (coords && coords.length >= 2) {
                const latlngs = coords.map((c: any) => [c[1], c[0]])
                ;(window as any).__orca_chat_route = latlngs
                ;(window as any).__orca_chat_instructions = route.instructions || []
                window.dispatchEvent(new CustomEvent("orca-chat-route", { detail: latlngs }))
                window.dispatchEvent(new CustomEvent("orca-chat-instructions", { detail: route.instructions || [] }))
                setActiveSub("route" as any)
                const mid = latlngs[Math.floor(latlngs.length/2)]
                setCenter([mid[1], mid[0]] as any)
                if (route.instructions && route.instructions.length) {
                  addMessage({ role: 'assistant', content: `Navigation — ${route.pfz_start || aName || "start"} → ${route.pfz_end || bName || "end"} (${route.distance_km} km):\n` + route.instructions.join("\n") })
                }
              }
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
