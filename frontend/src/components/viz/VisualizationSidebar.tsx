import { useVizStore } from "../../stores/vizStore"

const CATEGORIES = [
  {
    id: "fishing" as const,
    label: "Fishing Intelligence",
    icon: "🎣",
    subs: [
      { id: "pfz", label: "PFZ", desc: "Potential Fishing Zone polygons/markers" },
      { id: "sst", label: "SST", desc: "Sea Surface Temperature heatmap" },
      { id: "chl", label: "Chlorophyll-a", desc: "Chlorophyll concentration heatmap" },
      { id: "fish", label: "Fish / Fishing Info", desc: "Species & fishing-ground info" },
    ],
  },
  {
    id: "marine" as const,
    label: "Marine Conditions",
    icon: "🌊",
    subs: [
      { id: "wind", label: "Wind", desc: "Wind arrows + speed/direction" },
      { id: "waves", label: "Waves", desc: "Wave height + period" },
      { id: "currents", label: "Currents", desc: "Current arrows/streamlines" },
      { id: "weather", label: "Weather", desc: "Temp/Rain/Cloud" },
      { id: "sea", label: "Sea Conditions", desc: "Overall marine summary" },
    ],
  },
  {
    id: "safety" as const,
    label: "Safety & Alerts",
    icon: "⚠️",
    subs: [
      { id: "cyclone", label: "Cyclone", desc: "Track + forecast cone" },
      { id: "lightning", label: "Lightning", desc: "Lightning markers" },
      { id: "mpa", label: "MPA", desc: "Marine Protected Area polygons" },
      { id: "restricted", label: "Restricted Zones", desc: "Red hatched polygons" },
      { id: "alerts", label: "Safety Alerts", desc: "High-wave/rough-sea alerts" },
    ],
  },
  {
    id: "navigation" as const,
    label: "Navigation",
    icon: "🧭",
    subs: [
      { id: "vessel", label: "Vessel", desc: "User vessel position" },
      { id: "ports", label: "Ports", desc: "Port markers" },
      { id: "eez", label: "EEZ", desc: "Maritime boundary" },
      { id: "route", label: "Route", desc: "Optimized route line" },
      { id: "geofence", label: "Distance / Geofencing", desc: "Distance + restricted intersection" },
    ],
  },
] as const

const SOURCE_LABEL: Record<string, string> = {
  pfz: "INCOIS PFZ (46 obs)",
  sst: "Copernicus + Open-Meteo Marine (23 days)",
  chl: "INCOIS/MOSDAC + Open-Meteo (23 days, chl 0.139)",
  fish: "CMFRI / OBIS (pending API)",
  wind: "Open-Meteo Archive (23 days)",
  waves: "Open-Meteo Marine (23 days)",
  currents: "Copernicus current_speed (pending)",
  weather: "Open-Meteo (23 days)",
  sea: "Composite ocean + weather",
  cyclone: "IMD Cyclone / marine_hazards",
  lightning: "IMD Lightning / marine_hazards",
  mpa: "Protected Areas (0 in Mumbai bbox)",
  restricted: "Geofences (1 coastline)",
  alerts: "Active hazards (0)",
  vessel: "User location (Mumbai 19.076,72.877)",
  ports: "Port dataset (pending)",
  eez: "MarineRegions EEZ (5 boundaries)",
  route: "Route engine (stub)",
  geofence: "Geofence check (PostGIS)",
}

export default function VisualizationSidebar() {
  const { sidebarOpen, activeCategory, activeSub, setSidebarOpen, setActiveCategory, setActiveSub } = useVizStore()

  if (!sidebarOpen) {
    return (
      <button
        onClick={() => setSidebarOpen(true)}
        className="fixed right-0 top-1/2 -translate-y-1/2 bg-slate-800 border border-slate-700 border-r-0 rounded-l-lg px-3 py-5 text-xs text-slate-200 hover:bg-slate-700 z-30 shadow-lg"
        aria-label="Open visualizations"
      >
        ◀ Viz
      </button>
    )
  }

  return (
    <div className="w-[320px] shrink-0 bg-slate-900 border-l border-slate-800 flex flex-col h-[calc(100vh-57px)]">
      <div className="p-3 border-b border-slate-800 flex justify-between items-center">
        <div className="text-sm font-semibold tracking-wide">VISUALIZATIONS</div>
        <button onClick={() => setSidebarOpen(false)} className="text-xs bg-slate-800 px-2 py-1 rounded hover:bg-slate-700 border border-slate-700">
          ▶
        </button>
      </div>
      <div className="px-3 py-2 text-[11px] text-slate-500 border-b border-slate-800/50">
        Mumbai coastal operating area • 4 categories • select sub to update map + legend + info card
      </div>

      <div className="flex-1 overflow-auto p-2 space-y-2">
        {CATEGORIES.map((cat) => (
          <div key={cat.id} className="border border-slate-800 rounded overflow-hidden">
            <button
              onClick={() => setActiveCategory(activeCategory === cat.id ? null : cat.id)}
              className={`w-full text-left px-3 py-2.5 text-sm font-medium flex justify-between items-center transition-colors ${activeCategory === cat.id ? "bg-slate-800 text-white" : "hover:bg-slate-800/60 text-slate-200"}`}
            >
              <span>
                {cat.icon} {cat.label}
              </span>
              <span className="text-xs text-slate-500 w-5 h-5 flex items-center justify-center rounded bg-slate-800 border border-slate-700">
                {activeCategory === cat.id ? "−" : "+"}
              </span>
            </button>
            {activeCategory === cat.id && (
              <div className="px-2 py-2 space-y-1.5 bg-slate-950/50">
                {cat.subs.map((sub) => (
                  <button
                    key={sub.id}
                    onClick={() => setActiveSub(sub.id as any)}
                    className={`w-full text-left px-3 py-2.5 rounded text-xs border transition-colors ${activeSub === sub.id ? "bg-blue-600 text-white border-blue-500" : "bg-slate-800 text-slate-300 hover:bg-slate-700 border-slate-700"}`}
                  >
                    <div className="font-medium flex justify-between">
                      <span>{sub.label}</span>
                      {activeSub === sub.id && <span className="text-[10px] bg-white/20 px-1.5 py-0.5 rounded">ACTIVE</span>}
                    </div>
                    <div className="text-[11px] opacity-70 leading-tight mt-0.5">{sub.desc}</div>
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {activeSub ? (
        <div className="p-3 border-t border-slate-800 bg-slate-900">
          <div className="text-xs font-semibold mb-1 flex justify-between">
            <span>Active: {activeSub.toUpperCase()}</span>
            <button onClick={() => setActiveSub(null)} className="text-[10px] text-slate-400 hover:text-white">
              clear
            </button>
          </div>
          <div className="text-[11px] text-slate-500">Map updated • Legend below • Hover for values</div>
          <div className="mt-2 h-7 rounded bg-gradient-to-r from-blue-900 via-cyan-500 via-yellow-400 to-red-500 flex items-center justify-between px-2 text-[10px] text-white font-medium shadow-inner">
            <span>Low</span>
            <span>High</span>
          </div>
          <div className="mt-2 border border-slate-700 rounded p-2.5 text-xs bg-slate-800">
            <div className="font-semibold text-slate-200">{activeSub.toUpperCase()} INFO</div>
            <div className="text-slate-400 mt-1">Location: 19.076°N, 72.877°E (Mumbai)</div>
            <div className="text-slate-400">Updated: 15 Aug – 06 Sep (23 days)</div>
            <div className="text-slate-400 truncate">Source: {SOURCE_LABEL[activeSub] || "PostGIS"}</div>
          </div>
        </div>
      ) : (
        <div className="p-3 border-t border-slate-800 text-[11px] text-slate-500 text-center">Select a subvisualization to update the map</div>
      )}
    </div>
  )
}
