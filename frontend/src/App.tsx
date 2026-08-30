import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ChatPanel from './components/chat/ChatPanel'
import MapView from './components/map/MapView'
import { SstChart, ChlorophyllChart } from './components/dashboard/Charts'
import { useMapStore } from './stores/mapStore'
import { useChatStore } from './stores/chatStore'

const qc = new QueryClient()

function Dashboard() {
  const { pfz, layers, toggleLayer, selectedPfz } = useMapStore()
  const { messages } = useChatStore()
  const lastAssistant = [...messages].reverse().find((m) => m.role === 'assistant')

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 p-4 flex justify-between">
        <div>
          <h1 className="text-xl font-bold">ORCA — Marine Intelligence Command Center</h1>
          <p className="text-xs text-slate-400">M9 • MapLibre + ECharts + Chat+Map Sync • All data on D:</p>
        </div>
        <div className="text-xs text-slate-500">PFZ {pfz.length} | Time: <input type="date" defaultValue="2026-08-30" className="bg-slate-800 rounded px-2 py-1" /> <button className="ml-2 px-2 py-1 bg-slate-800 rounded">&lt; Prev</button></div>
      </header>
      <div className="grid grid-cols-12 gap-4 p-4">
        <div className="col-span-4 flex flex-col gap-4 h-[calc(100vh-100px)]">
          <div className="flex-1 min-h-0">
            <ChatPanel />
          </div>
          <div className="border border-slate-800 rounded p-3">
            <div className="text-xs font-semibold mb-2">Evidence Drawer</div>
            <div className="text-xs text-slate-400 whitespace-pre-wrap">{lastAssistant?.content?.slice(0,400) || 'No evidence yet - ask ORCA'}</div>
            <div className="text-xs mt-2">Source: INCOIS + IMD + PostGIS + Qdrant</div>
          </div>
        </div>
        <div className="col-span-8 flex flex-col gap-4">
          <div className="flex gap-2 text-xs">
            <label className="flex items-center gap-1"><input type="checkbox" checked={layers.pfz} onChange={() => toggleLayer('pfz')} /> PFZ</label>
            <label className="flex items-center gap-1"><input type="checkbox" checked={layers.mpa} onChange={() => toggleLayer('mpa')} /> MPA</label>
            <label className="flex items-center gap-1"><input type="checkbox" checked={layers.eez} onChange={() => toggleLayer('eez')} /> EEZ</label>
            <span className="ml-auto text-slate-500">Selected: {selectedPfz?.sector || 'none'} {selectedPfz?.distance_km?.toFixed(1) || ''} km</span>
          </div>
          <div className="h-[400px]">
            <MapView />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="border border-slate-800 rounded p-3">
              <div className="text-xs font-semibold">SST Trend</div>
              <SstChart />
            </div>
            <div className="border border-slate-800 rounded p-3">
              <div className="text-xs font-semibold">Chlorophyll</div>
              <ChlorophyllChart />
            </div>
          </div>
          <div className="border border-slate-800 rounded p-3 text-xs">
            <span className="font-semibold">Risk:</span> {lastAssistant?.risk ? JSON.stringify(lastAssistant.risk) : 'No assessment yet'} | <span className="text-amber-400">Geofence: Test MPA Mumbai protected distance 0.0</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <Dashboard />
    </QueryClientProvider>
  )
}
