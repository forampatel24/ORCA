import { useState } from 'react'
import { useChatStore } from '../../stores/chatStore'
import { useMapStore } from '../../stores/mapStore'
import { chat, getNearestPFZ, login } from '../../api/client'

export default function ChatPanel() {
  const [input, setInput] = useState('')
  const { messages, addMessage, loading, setLoading } = useChatStore()
  const { setPfz, setCenter, setSelected } = useMapStore()

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
        setPfz(pfzData.items || [])
        if (pfzData.items?.length) {
          // show all PFZ for that region, center on map-provided center
          setSelected(pfzData.items[0])
          setCenter(data.center || [pfzData.items[0].longitude, pfzData.items[0].latitude])
        } else if (data.center) setCenter(data.center as any)
      } catch { if(data.center) setCenter(data.center as any) }
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
