import { useState } from 'react'

export default function App() {
  const [msg, setMsg] = useState('')
  const [resp, setResp] = useState('')

  async function send() {
    const r = await fetch('/api/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    })
    const j = await r.json()
    setResp(JSON.stringify(j, null, 2))
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 p-4">
        <h1 className="text-xl font-bold">ORCA — Marine Intelligence Platform</h1>
        <p className="text-sm text-slate-400">M0 scaffold • React + FastAPI + MapLibre placeholder</p>
      </header>
      <div className="grid grid-cols-2 gap-4 p-4">
        <div className="border border-slate-800 rounded p-4">
          <h2 className="font-semibold mb-2">Chat (M0 stub -&gt; M4 orchestrator)</h2>
          <div className="flex gap-2">
            <input value={msg} onChange={e => setMsg(e.target.value)} placeholder="Is it safe to fish tomorrow near Mumbai?" className="flex-1 bg-slate-900 border border-slate-700 rounded px-3 py-2" />
            <button onClick={send} className="bg-blue-600 px-4 py-2 rounded">Send</button>
          </div>
          <pre className="mt-4 text-xs bg-slate-900 p-3 rounded overflow-auto">{resp || 'No response yet'}</pre>
        </div>
        <div className="border border-slate-800 rounded p-4">
          <h2 className="font-semibold mb-2">Map (MapLibre - M9)</h2>
          <div className="h-64 bg-slate-900 rounded flex items-center justify-center text-slate-500">MapLibre mount point - M9</div>
        </div>
      </div>
    </div>
  )
}
