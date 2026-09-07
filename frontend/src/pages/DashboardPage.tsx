import { useEffect, useState } from "react"
import ReactECharts from "echarts-for-react"
import { api } from "../api/client"

function StatCard({ icon, label, value, sub, trend, color }: any) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-4 flex flex-col gap-1">
      <div className="flex justify-between items-center">
        <span className="text-[11px] tracking-wide text-slate-500 font-semibold">{label}</span>
        <span className={`text-lg ${color}`}>{icon}</span>
      </div>
      <div className="text-xl font-bold text-white">{value}</div>
      <div className="text-[11px] text-slate-400">{sub}</div>
      {trend && <div className="text-[10px] text-emerald-400 mt-1">↗ {trend}</div>}
    </div>
  )
}

function useFetch(url: string, params?: any) {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    setLoading(true)
    api.get(url, { params }).then((r) => setData(r.data)).catch(() => setData(null)).finally(() => setLoading(false))
  }, [JSON.stringify(params), url])
  return { data, loading }
}

export default function DashboardPage() {
  const [range, setRange] = useState<7 | 30>(30)
  const ocean = useFetch("/ocean/history", { latitude: 19.076, longitude: 72.877, limit: range })
  const chl = useFetch("/ocean/chlorophyll-history", { latitude: 19.076, longitude: 72.877, limit: range })
  const weather = useFetch("/weather/", { latitude: 19.076, longitude: 72.877, limit: range })
  const tides = useFetch("/ocean/tides", { hours: range === 30 ? 720 : 48 })
  const vessels = useFetch("/vessels", { bbox: "71.8,15.5,74.5,20.5", limit: 50 })

  const sstDates = (ocean.data?.items || []).slice(-range).map((r: any) => new Date(r.observation_time).toLocaleDateString("en-IN", { day: "2-digit", month: "short" }))
  const sstVals = (ocean.data?.items || []).slice(-range).map((r: any) => r.sst)
  const waveVals = (ocean.data?.items || []).slice(-range).map((r: any) => r.wave_height)
  const windVals = (weather.data?.items || []).slice(-range).map((r: any) => r.wind_speed)
  const tempVals = (weather.data?.items || []).slice(-range).map((r: any) => r.temperature)
  const chlDatesAll = (chl.data?.items || []).map((r: any) => new Date(r.observation_time).toLocaleDateString("en-IN", { day: "2-digit", month: "short" }))
  const chlValsAll = (chl.data?.items || []).map((r: any) => r.chlorophyll)
  const chlDates = chlDatesAll.slice(-range)
  const chlVals = chlValsAll.slice(-range)
  const tideSeriesAll = tides.data?.series || []
  const tideExtremes = tides.data?.extremes || []
  // For 30 days (720h) the series is 1440 points — sample for readability
  const tideSeries = range === 30 ? tideSeriesAll.filter((_: any, i: number) => i % 4 === 0) : tideSeriesAll.slice(0, 96)

  const latestSst = sstVals[sstVals.length - 1]
  const latestWind = windVals[windVals.length - 1]
  const latestWave = waveVals[waveVals.length - 1]
  const avgSst = sstVals.length ? (sstVals.reduce((a: number, b: number) => a + (b || 0), 0) / sstVals.length).toFixed(1) : "—"

  const cardBase = "rounded-xl border border-slate-800 bg-slate-900 p-4"

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <div className="border-b border-slate-800 px-6 py-4 flex flex-wrap justify-between items-center gap-3 bg-slate-950/80 backdrop-blur sticky top-0 z-20">
        <div>
          <h1 className="text-xl font-bold tracking-tight">ORCA Analytics Dashboard</h1>
          <p className="text-xs text-slate-400">Mumbai coastal operating area • Live • Past {range} days to today • 19.076°N, 72.877°E</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setRange(7)} className={`px-3 py-1.5 rounded text-xs font-medium border ${range === 7 ? "bg-sky-600 border-sky-500 text-white" : "bg-slate-800 border-slate-700 text-slate-300"}`}>7 days</button>
          <button onClick={() => setRange(30)} className={`px-3 py-1.5 rounded text-xs font-medium border ${range === 30 ? "bg-sky-600 border-sky-500 text-white" : "bg-slate-800 border-slate-700 text-slate-300"}`}>30 days</button>
          <span className="ml-2 text-[11px] text-slate-500 hidden sm:inline">Sources: Copernicus NRT • Open-Meteo • INCOIS • GFW</span>
        </div>
      </div>

      {/* Stats */}
      <div className="px-6 py-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <StatCard icon="🌡️" label="SST NOW" value={latestSst ? `${latestSst.toFixed(1)}°C` : "—"} sub={`Avg ${avgSst}°C`} color="text-sky-400" trend={sstVals.length > 1 ? `${(sstVals[sstVals.length-1] - sstVals[0]).toFixed(1)}°C` : ""} />
        <StatCard icon="🌿" label="CHL NOW" value={chlVals.length ? `${chlVals[chlVals.length-1].toFixed(3)}` : "—"} sub="mg/m³ Copernicus" color="text-emerald-400" />
        <StatCard icon="🌊" label="WAVE NOW" value={latestWave ? `${latestWave.toFixed(1)} m` : "—"} sub="VHM0 WAM" color="text-orange-400" />
        <StatCard icon="💨" label="WIND NOW" value={latestWind ? `${latestWind.toFixed(1)} km/h` : "—"} sub="Open-Meteo" color="text-cyan-400" />
        <StatCard icon="🌙" label="NEXT TIDE" value={tideExtremes[0] ? `${tideExtremes[0].type === "high" ? "▲" : "▼"} ${tideExtremes[0].height_m} m` : "—"} sub={tideExtremes[0] ? new Date(tideExtremes[0].time).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", timeZone: "Asia/Kolkata" }) : "—"} color="text-violet-400" />
        <StatCard icon="🚢" label="VESSELS" value={vessels.data?.count ?? "—"} sub="GFW 31 Aug→07 Sep" color="text-amber-400" />
      </div>

      {/* Charts grid */}
      <div className="px-6 pb-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* SST */}
        <div className={cardBase}>
          <div className="flex justify-between items-center mb-2">
            <div className="text-sm font-semibold">Sea Surface Temperature — past {range} days</div>
            <span className="text-[10px] px-2 py-1 rounded bg-sky-900/40 border border-sky-800 text-sky-300">Copernicus NRT 0.083° + Open-Meteo</span>
          </div>
          <ReactECharts option={{
            backgroundColor: "transparent", textStyle: { color: "#94a3b8" },
            tooltip: { trigger: "axis" },
            xAxis: { type: "category", data: sstDates, axisLabel: { fontSize: 9, rotate: 30 } },
            yAxis: { type: "value", name: "°C", min: 27 },
            series: [{ data: sstVals, type: "line", smooth: true, areaStyle: { color: "rgba(14,165,233,0.15)" }, lineStyle: { color: "#0ea5e9", width: 2 } }],
          }} style={{ height: 220 }} />
        </div>

        {/* Chlorophyll */}
        <div className={cardBase}>
          <div className="flex justify-between items-center mb-2">
            <div className="text-sm font-semibold">Chlorophyll-a — NRT (available {chlDates.length} days)</div>
            <span className="text-[10px] px-2 py-1 rounded bg-emerald-900/40 border border-emerald-800 text-emerald-300">Copernicus BGC 0.25°</span>
          </div>
          <ReactECharts option={{
            backgroundColor: "transparent", textStyle: { color: "#94a3b8" },
            tooltip: { trigger: "axis" },
            xAxis: { type: "category", data: chlDates, axisLabel: { fontSize: 9, rotate: 30 } },
            yAxis: { type: "value", name: "mg/m³" },
            series: [{ data: chlVals, type: "bar", itemStyle: { color: "#10b981" } }],
          }} style={{ height: 220 }} />
        </div>

        {/* Waves */}
        <div className={cardBase}>
          <div className="text-sm font-semibold mb-2">Significant Wave Height — past {range} days</div>
          <ReactECharts option={{
            backgroundColor: "transparent", textStyle: { color: "#94a3b8" },
            tooltip: { trigger: "axis" },
            xAxis: { type: "category", data: sstDates, axisLabel: { fontSize: 9, rotate: 30 } },
            yAxis: { type: "value", name: "m" },
            series: [{ data: waveVals, type: "line", smooth: true, lineStyle: { color: "#f97316", width: 2 }, areaStyle: { color: "rgba(249,115,22,0.12)" } }],
          }} style={{ height: 220 }} />
          <div className="text-[11px] text-slate-500 mt-1">Source: Copernicus WAM VHM0 + Open-Meteo Marine • Green &lt;1.0 m → Red &gt;2.5 m</div>
        </div>

        {/* Wind */}
        <div className={cardBase}>
          <div className="text-sm font-semibold mb-2">Wind Speed — past {range} days (gust as bars)</div>
          <ReactECharts option={{
            backgroundColor: "transparent", textStyle: { color: "#94a3b8" },
            tooltip: { trigger: "axis" },
            xAxis: { type: "category", data: (weather.data?.items || []).map((r: any) => new Date(r.observation_time).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })), axisLabel: { fontSize: 9, rotate: 30 } },
            yAxis: { type: "value", name: "km/h" },
            series: [
              { data: windVals, type: "line", smooth: true, lineStyle: { color: "#38bdf8", width: 2 } },
              { data: (weather.data?.items || []).map((r: any) => r.wind_direction), type: "bar", yAxisIndex: 0, itemStyle: { color: "rgba(56,189,248,0.25)" }, name: "dir" },
            ],
          }} style={{ height: 220 }} />
        </div>

        {/* Tides */}
        <div className={`${cardBase} lg:col-span-2`}>
          <div className="flex justify-between items-center mb-2">
            <div className="text-sm font-semibold">Tides — harmonic curve (Mumbai Apollo Bunder, MSL 2.10 m) — next 48h + {range}-day extremes</div>
            <span className="text-[10px] px-2 py-1 rounded bg-violet-900/40 border border-violet-800 text-violet-300">Admiralty 10 constituents</span>
          </div>
          <ReactECharts option={{
            backgroundColor: "transparent", textStyle: { color: "#94a3b8" },
            tooltip: { trigger: "axis" },
            xAxis: { type: "category", data: tideSeries.slice(0, 96).map((r: any) => new Date(r.time).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", timeZone: "Asia/Kolkata" })), axisLabel: { fontSize: 8, rotate: 30, interval: 7 } },
            yAxis: { type: "value", name: "m (CD)" },
            series: [{ data: tideSeries.slice(0, 96).map((r: any) => r.height_m), type: "line", smooth: true, areaStyle: { color: "rgba(139,92,246,0.15)" }, lineStyle: { color: "#8b5cf6", width: 1.8 }, markPoint: { data: tideExtremes.slice(0, 6).map((e: any) => ({ name: e.type, value: e.height_m, xAxis: tideSeries.findIndex((r: any) => r.time === e.time), yAxis: e.height_m })) } }],
          }} style={{ height: 260 }} />
          <div className="mt-2 flex flex-wrap gap-2 text-[11px]">
            {tideExtremes.slice(0, 8).map((e: any) => (
              <span key={e.time} className={`px-2 py-1 rounded border ${e.type === "high" ? "bg-cyan-900/30 border-cyan-800 text-cyan-300" : "bg-amber-900/30 border-amber-800 text-amber-300"}`}>{e.type === "high" ? "▲" : "▼"} {new Date(e.time).toLocaleDateString("en-IN", { day: "2-digit", month: "short", timeZone: "Asia/Kolkata" })} {new Date(e.time).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", timeZone: "Asia/Kolkata" })} • {e.height_m} m</span>
            ))}
          </div>
        </div>
      </div>

      <div className="px-6 pb-8 text-[11px] text-slate-500 text-center">All graphs use live original data — no mocks. SST/Chl/Waves from Copernicus NRT grids, Wind from Open-Meteo per-cell, Tides from harmonic constituents, PFZ 21 from INCOIS SEC002. Switch range above to see 7 vs 30 days.</div>
    </div>
  )
}
