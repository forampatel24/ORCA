import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import ChatPanel from "./components/chat/ChatPanel"
import LeafletMap from "./components/map/LeafletMap"
import VisualizationSidebar from "./components/viz/VisualizationSidebar"
import { useVizStore } from "./stores/vizStore"
import { useMapStore } from "./stores/mapStore"
import { useChatStore } from "./stores/chatStore"
import { SstChart, ChlorophyllChart } from "./components/dashboard/Charts"

const qc = new QueryClient()

function LegendBar({ activeSub }: { activeSub: string | null }) {
  if (!activeSub) return null
  const legends: Record<string, { title: string; gradient: string; labels: [string, string]; note: string }> = {
    sst: { title: "SST (°C)", gradient: "from-blue-900 via-cyan-500 via-yellow-400 to-red-500", labels: ["26°C", "30°C"], note: "Open-Meteo Marine 23 days" },
    chl: { title: "Chlorophyll (mg/m³)", gradient: "from-blue-900 via-emerald-500 to-green-700", labels: ["0.1", "2.0"], note: "Copernicus 0.139" },
    waves: { title: "Wave Height (m)", gradient: "from-emerald-600 via-yellow-500 via-orange-500 to-red-600", labels: ["0.5m", "2.0m"], note: "Open-Meteo Marine" },
    wind: { title: "Wind Speed (km/h)", gradient: "from-slate-600 via-sky-500 to-blue-700", labels: ["5", "25"], note: "Open-Meteo Archive" },
    pfz: { title: "PFZ Suitability", gradient: "from-sky-600 via-green-500 to-emerald-600", labels: ["Low", "High"], note: "INCOIS 46 zones" },
    weather: { title: "Temperature", gradient: "from-blue-700 via-yellow-400 to-red-600", labels: ["24°C", "30°C"], note: "Open-Meteo" },
  }
  const l = legends[activeSub]
  if (!l) return null
  return (
    <div className="flex items-center gap-3 bg-slate-900/90 border border-slate-700 rounded px-3 py-2 text-xs backdrop-blur">
      <span className="font-semibold text-slate-200 whitespace-nowrap">{l.title}</span>
      <div className={`h-3 w-32 rounded bg-gradient-to-r ${l.gradient} border border-white/20`} />
      <span className="text-slate-400 text-[11px]">
        {l.labels[0]} — {l.labels[1]}
      </span>
      <span className="text-slate-500 text-[11px] hidden sm:inline">• {l.note}</span>
    </div>
  )
}

function InfoCard({ activeSub }: { activeSub: string | null }) {
  if (!activeSub) return null
  const cards: Record<string, { title: string; lines: string[]; source: string }> = {
    pfz: { title: "POTENTIAL FISHING ZONE", lines: ["46 PFZ (15 Aug–06 Sep) near Mumbai", "Green markers • Dashed halo = 5km zone", "Hover for SST/Chl/distance/validity"], source: "INCOIS PFZ • PostGIS" },
    sst: { title: "SEA SURFACE TEMPERATURE", lines: ["23-day SST 29.1–29.2°C Mumbai", "Colored dots • Hover for temp/location", "Updated daily 12:00 IST"], source: "Copernicus + Open-Meteo Marine" },
    chl: { title: "CHLOROPHYLL-a", lines: ["Chlorophyll 0.139 mg/m³ flat (archive fallback)", "Green dots intensity = concentration", "Needs Copernicus CHL live"], source: "INCOIS/MOSDAC pending" },
    fish: { title: "FISH / FISHING INFO", lines: ["CMFRI 8 landings + OBIS ingested", "No map layer yet — API pending", "Will show species & grounds"], source: "CMFRI / OBIS" },
    wind: { title: "WIND", lines: ["Wind 15–18 km/h SW Mumbai", "Arrows = direction • Hover for gust", "23 days archive 12:00 IST"], source: "Open-Meteo Archive" },
    waves: { title: "WAVE CONDITIONS", lines: ["Significant wave 1.4–1.6 m", "Circle size = height • Color = severity", "Period ~6s • Direction W→E"], source: "Open-Meteo Marine" },
    currents: { title: "CURRENTS", lines: ["No live streamlines", "current_speed null in DB", "Needs Copernicus PHY currents"], source: "Copernicus GLOBAL_PHY" },
    weather: { title: "WEATHER", lines: ["Temp 26–28°C • Rain 0.2–0.5 mm", "Cells with icon • Hover for humidity", "23 days noon IST"], source: "Open-Meteo Archive" },
    sea: { title: "SEA CONDITIONS", lines: ["Composite: SST 29.1°C • Wave 1.5m", "Wind 15.8 km/h • Chl 0.139", "Mumbai 19.076°N,72.877°E"], source: "Ocean + Weather" },
    cyclone: { title: "CYCLONE", lines: ["No active cyclone in Mumbai bbox", "Track + cone when IMD warning active", "marine_hazards 0 rows (15 Aug–06 Sep)"], source: "IMD Cyclone" },
    lightning: { title: "LIGHTNING", lines: ["No recent lightning activity", "Markers when marine_hazards has lightning", "Mumbai bbox clear"], source: "IMD Lightning" },
    mpa: { title: "MARINE PROTECTED AREAS", lines: ["0 MPA in Mumbai bbox 72.2,18.5,73.2,19.5", "Thane Creek outside bbox", "WDPA + protected_areas"], source: "WDPA / protected_areas" },
    restricted: { title: "RESTRICTED ZONES", lines: ["1 coastline geofence only", "No red hatched polygons in bbox", "Natural Earth 10m"], source: "PostGIS geofences" },
    alerts: { title: "SAFETY ALERTS", lines: ["All clear — 0 active hazards", "High-wave / rough-sea / storm none", "Safety has visual priority over PFZ"], source: "marine_hazards" },
    vessel: { title: "VESSEL", lines: ["User vessel 19.076°N, 72.877°E", "Mumbai coastal operating area", "Heading/course later"], source: "User location" },
    ports: { title: "PORTS", lines: ["Port markers pending", "Needs Natural Earth ports dataset", "Hover for name/info later"], source: "Natural Earth ports" },
    eez: { title: "EEZ", lines: ["Indian EEZ maritime boundary", "Blue dashed • 5 MarineRegions clipped", "Mumbai bbox offshore"], source: "MarineRegions WFS" },
    route: { title: "ROUTE", lines: ["Optimized route Mumbai→PFZ", "Green dashed • Shortest vs Safest later", "Accounts weather/waves/restricted"], source: "Route engine (stub)" },
    geofence: { title: "DISTANCE / GEOFENCING", lines: ["2.4 km buffer demo circle", "Detects MPA/restricted intersection", "PostGIS ST_Distance/ST_Intersects"], source: "PostGIS geospatial" },
  }
  const c = cards[activeSub]
  if (!c) return null
  return (
    <div className="bg-slate-900/90 border border-slate-700 rounded p-3 text-xs backdrop-blur min-w-[220px]">
      <div className="font-semibold text-white tracking-wide text-[11px]">{c.title}</div>
      <div className="mt-2 space-y-1 text-slate-300">
        {c.lines.map((l, i) => (
          <div key={i} className="leading-tight">
            • {l}
          </div>
        ))}
      </div>
      <div className="mt-2 text-[11px] text-slate-500">Source: {c.source} • Hover for values</div>
    </div>
  )
}

function Dashboard() {
  const { pfz } = useMapStore()
  const { activeSub } = useVizStore()
  const { messages } = useChatStore()
  const lastAssistant = [...messages].reverse().find((m) => m.role === "assistant")

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col">
      <header className="border-b border-slate-800 px-4 py-3 flex justify-between items-center bg-slate-950">
        <div>
          <h1 className="text-lg font-bold tracking-tight">ORCA — Marine Intelligence Command Center</h1>
          <p className="text-[11px] text-slate-400">Mumbai coastal operating area • 72.2,18.5,73.2,19.5 • 46 PFZ • 23-day SST/Wave • Chat+Map sync</p>
        </div>
        <div className="text-xs text-slate-500 flex items-center gap-3">
          <span className="hidden sm:inline">PFZ {pfz.length} • Ocean 23 • Weather 23</span>
          <span className="px-2 py-1 bg-emerald-900/30 border border-emerald-700 rounded text-emerald-300 text-[11px]">● Live</span>
        </div>
      </header>

      <div className="flex flex-1 min-h-0">
        {/* Left — Chat */}
        <div className="w-[380px] shrink-0 border-r border-slate-800 bg-slate-950 flex flex-col">
          <div className="flex-1 min-h-0 p-2">
            <ChatPanel />
          </div>
          <div className="border-t border-slate-800 p-3 bg-slate-900/50">
            <div className="text-xs font-semibold mb-1">Evidence Drawer</div>
            <div className="text-xs text-slate-400 whitespace-pre-wrap max-h-20 overflow-auto">
              {lastAssistant?.content?.slice(0, 380) || "No evidence yet — ask ORCA e.g. 'Is it safe near Mumbai tomorrow?'"}
            </div>
            <div className="text-[11px] mt-2 text-slate-500">Sources: INCOIS + IMD + PostGIS + Qdrant • Risk: {lastAssistant?.risk ? JSON.stringify(lastAssistant.risk).slice(0, 60) : "No assessment"}</div>
          </div>
        </div>

        {/* Center — Map */}
        <div className="flex-1 min-w-0 flex flex-col bg-slate-950 p-3 gap-3">
          <div className="flex-1 min-h-[420px] relative flex flex-col">
            <div className="flex justify-between items-center mb-2 gap-2">
              <div className="text-xs text-slate-400">
                {activeSub ? (
                  <span>
                    <span className="text-white font-medium">{activeSub.toUpperCase()}</span> • Mumbai 19.076°N, 72.877°E
                  </span>
                ) : (
                  <span>Select a visualization → map adapts • Hover for values</span>
                )}
              </div>
              <LegendBar activeSub={activeSub} />
            </div>
            <div className="flex-1 min-h-0 relative rounded-lg overflow-hidden border border-slate-800">
              <LeafletMap />
              {/* Info card overlay */}
              <div className="absolute bottom-3 left-3 z-[400] max-w-[260px] hidden md:block">
                <InfoCard activeSub={activeSub} />
              </div>
            </div>
            {/* Mobile info card */}
            {activeSub && (
              <div className="md:hidden mt-2">
                <InfoCard activeSub={activeSub} />
              </div>
            )}
          </div>

          {/* Charts — only show for fishing/marine context */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            <div className="border border-slate-800 rounded p-3 bg-slate-900">
              <div className="text-xs font-semibold mb-1">SST Trend (23 days 15 Aug–06 Sep)</div>
              <SstChart />
            </div>
            <div className="border border-slate-800 rounded p-3 bg-slate-900">
              <div className="text-xs font-semibold mb-1">Chlorophyll (23 days)</div>
              <ChlorophyllChart />
            </div>
          </div>
        </div>

        {/* Right — Sidebar */}
        <VisualizationSidebar />
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
