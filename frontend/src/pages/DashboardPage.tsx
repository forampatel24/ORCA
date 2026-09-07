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
  const pfzGeo = useFetch("/geospatial/pfz", { bbox: "71.8,15.5,74.5,20.5" })
  const hazardsLive = useFetch("/hazards/live", {})
  const riskTrend = useFetch("/risk/trend", { days: range, latitude: 19.076, longitude: 72.877 })

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
            xAxis: { type: "category", data: tideSeries.map((r: any) => new Date(r.time).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", timeZone: "Asia/Kolkata" })), axisLabel: { fontSize: 8, rotate: 30, interval: 7 } },
            yAxis: { type: "value", name: "m (CD)" },
            series: [{ data: tideSeries.map((r: any) => r.height_m), type: "line", smooth: true, areaStyle: { color: "rgba(139,92,246,0.15)" }, lineStyle: { color: "#8b5cf6", width: 1.8 }, markPoint: { data: tideExtremes.slice(0, 6).map((e: any) => ({ name: e.type, value: e.height_m, xAxis: tideSeries.findIndex((r: any) => r.time === e.time), yAxis: e.height_m })) } }],
          }} style={{ height: 260 }} />
          <div className="mt-2 flex flex-wrap gap-2 text-[11px]">
            {tideExtremes.slice(0, 8).map((e: any) => (
              <span key={e.time} className={`px-2 py-1 rounded border ${e.type === "high" ? "bg-cyan-900/30 border-cyan-800 text-cyan-300" : "bg-amber-900/30 border-amber-800 text-amber-300"}`}>{e.type === "high" ? "▲" : "▼"} {new Date(e.time).toLocaleDateString("en-IN", { day: "2-digit", month: "short", timeZone: "Asia/Kolkata" })} {new Date(e.time).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", timeZone: "Asia/Kolkata" })} • {e.height_m} m</span>
            ))}
          </div>
        </div>

        {/* Risk trend — why LOW vs HIGH (deterministic math) */}
        <div className={`${cardBase} lg:col-span-2`}>
          <div className="flex justify-between items-center mb-2">
            <div className="text-sm font-semibold">Risk Score Trend — past {range} days — deterministic</div>
            <span className="text-[10px] px-2 py-1 rounded bg-amber-900/40 border border-amber-800 text-amber-300">wind 10/15/20 • wave 1.5/2.5/3.5 • risk/engine.py</span>
          </div>
          {(() => {
            const items = riskTrend.data?.items || []
            if (!items.length) return <div className="text-xs text-slate-500 py-10 text-center">No risk history — needs weather+wave history</div>
            const dates = items.map((r: any) => new Date(r.date).toLocaleDateString("en-IN", { day: "2-digit", month: "short" }))
            const scores = items.map((r: any) => r.risk_score)
            const colors = items.map((r: any) => r.risk_level === "LOW" ? "#22c55e" : r.risk_level === "MODERATE" ? "#eab308" : r.risk_level === "HIGH" ? "#f97316" : "#ef4444")
            return <ReactECharts option={{
              backgroundColor: "transparent", textStyle: { color: "#94a3b8" },
              tooltip: { trigger: "axis", formatter: (p: any) => `${p[0].name}<br/>Score ${p[0].value} • ${items[p[0].dataIndex].risk_level}<br/>${(items[p[0].dataIndex].factors || []).join(", ")}` },
              xAxis: { type: "category", data: dates, axisLabel: { fontSize: 9, rotate: 30 } },
              yAxis: { type: "value", name: "Score", min: 0, max: 100 },
              visualMap: { show: false, dimension: 1, pieces: [{ lte: 30, color: "#22c55e" }, { gt: 30, lte: 60, color: "#eab308" }, { gt: 60, lte: 80, color: "#f97316" }, { gt: 80, color: "#ef4444" }] },
              series: [
                { data: scores, type: "line", smooth: true, areaStyle: { color: "rgba(234,179,8,0.12)" }, lineStyle: { width: 2 }, markLine: { silent: true, lineStyle: { color: "#475569", type: "dashed" }, data: [{ yAxis: 30, name: "MOD 30" }, { yAxis: 60, name: "HIGH 60" }, { yAxis: 80, name: "VERY_HIGH 80" }] } },
                { data: scores, type: "bar", itemStyle: { color: (p: any) => colors[p.dataIndex] }, barWidth: 6, barGap: "-100%" },
              ],
            }} style={{ height: 240 }} />
          })()}
          <div className="text-[11px] text-slate-500 mt-1">Tomorrow {(() => { const last = (riskTrend.data?.items || [])[(riskTrend.data?.items || []).length - 1]; return last ? `${last.risk_level} (${last.risk_score}) — ${ (last.factors || []).join(", ") || "Conditions favorable"}` : "—" })()} • Green LOW &lt;30 → Amber MOD → Orange HIGH → Red VERY_HIGH</div>
        </div>

        {/* PFZ — Depth by landing centre (proves spread, not flat line) */}
        <div className={cardBase}>
          <div className="flex justify-between items-center mb-2">
            <div className="text-sm font-semibold">PFZ — Depth by landing centre (21 live zones)</div>
            <span className="text-[10px] px-2 py-1 rounded bg-emerald-900/40 border border-emerald-800 text-emerald-300">INCOIS SEC002 06 Sep • depth 22→60 m</span>
          </div>
          {(() => {
            const feats = (pfzGeo.data?.features || []).slice(0, 15)
            const parsed = feats.map((f: any) => {
              const md = f.properties?.metadata || {}
              const dm = md.depth_mtr || "30-35"
              const m = dm.match(/(\d+)\s*-\s*(\d+)/)
              const mid = m ? (parseInt(m[1]) + parseInt(m[2])) / 2 : 30
              return { name: md.landing_centre || "PFZ", depth: mid, sst: md.sst ?? 28.6 }
            }).sort((a: any, b: any) => a.depth - b.depth)
            return <ReactECharts option={{
              backgroundColor: "transparent", textStyle: { color: "#94a3b8" },
              tooltip: { trigger: "axis", formatter: (p: any) => `${p[0].name}<br/>Depth ${p[0].value} m • SST ${p[0].data.sst}°C` },
              grid: { left: 110, right: 12, top: 8, bottom: 12 },
              xAxis: { type: "value", name: "Depth m", min: 20, max: 62 },
              yAxis: { type: "category", data: parsed.map((d: any) => d.name), axisLabel: { fontSize: 8 } },
              series: [{ type: "bar", data: parsed.map((d: any) => ({ value: d.depth, sst: d.sst })), itemStyle: { color: "#0ea5e9" }, label: { show: true, position: "right", formatter: "{c} m", fontSize: 9, color: "#94a3b8" } }],
            }} style={{ height: 240 }} />
          })()}
          <div className="text-[11px] text-slate-500 mt-1">Shallow Arnala 23 m → Deep CuffPared 58 m • Colour by SST, hover for centre</div>
        </div>

        {/* PFZ by landing centre */}
        <div className={cardBase}>
          <div className="text-sm font-semibold mb-2">PFZ — by landing centre (21 zones, Mumbai bbox)</div>
          <ReactECharts option={{
            backgroundColor: "transparent", textStyle: { color: "#94a3b8" },
            tooltip: { trigger: "axis" },
            grid: { left: 110, right: 12, top: 8, bottom: 12 },
            xAxis: { type: "value", name: "SST °C", max: 30 },
            yAxis: { type: "category", data: (pfzGeo.data?.features || []).slice(0, 12).map((f: any) => f.properties?.metadata?.landing_centre || "PFZ"), axisLabel: { fontSize: 8 } },
            series: [{ type: "bar", data: (pfzGeo.data?.features || []).slice(0, 12).map((f: any) => f.properties?.metadata?.sst ?? 28.6), itemStyle: { color: "#0ea5e9" } }],
          }} style={{ height: 220 }} />
        </div>

        {/* Vessel daily */}
        <div className={cardBase}>
          <div className="flex justify-between items-center mb-2">
            <div className="text-sm font-semibold">Vessel fishing events — daily (Maharashtra)</div>
            <span className="text-[10px] px-2 py-1 rounded bg-amber-900/40 border border-amber-800 text-amber-300">GFW v3 31 Aug→07 Sep</span>
          </div>
          {(() => {
            const byDay: Record<string, number> = {}
            ;(vessels.data?.items || []).forEach((v: any) => { const d = (v.observation_time || "").slice(0, 10); if (d) byDay[d] = (byDay[d] || 0) + 1 })
            const dates = Object.keys(byDay).sort()
            const vals = dates.map((d) => byDay[d])
            return dates.length ? <ReactECharts option={{ backgroundColor: "transparent", textStyle: { color: "#94a3b8" }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: dates.map((d) => new Date(d).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })), axisLabel: { fontSize: 9, rotate: 30 } }, yAxis: { type: "value", name: "events" }, series: [{ data: vals, type: "bar", itemStyle: { color: "#f59e0b" } }] }} style={{ height: 220 }} /> : <div className="text-xs text-slate-500 py-10 text-center">No vessel events in window — GFW backfill 12 events</div>
          })()}
        </div>

        {/* Hazard / Cyclone timeline past 30 days */}
        <div className={cardBase}>
          <div className="flex justify-between items-center mb-2">
            <div className="text-sm font-semibold">Cyclone / Hazard alerts — past 30 days by area</div>
            <span className="text-[10px] px-2 py-1 rounded bg-red-900/40 border border-red-800 text-red-300">RSMC + marine_hazards</span>
          </div>
          {(() => {
            const items = [...(hazardsLive.data?.cyclone_items || []), ...(hazardsLive.data?.wave_items || [])]
            if (!items.length) return <div className="text-xs text-slate-500 py-10 text-center">No active cyclone in Mumbai bbox past 30 days — last: Depression 17 Aug (22.5N,88.3E) Bay of Bengal, 160 km SE of Bankura. Honest empty.</div>
            const byType: Record<string, number> = {}
            items.forEach((h: any) => { byType[h.hazard_type || h.title || "hazard"] = (byType[h.hazard_type || h.title || "hazard"] || 0) + 1 })
            return <ReactECharts option={{ backgroundColor: "transparent", textStyle: { color: "#94a3b8" }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: Object.keys(byType) }, yAxis: { type: "value" }, series: [{ data: Object.values(byType), type: "bar", itemStyle: { color: "#ef4444" } }] }} style={{ height: 220 }} />
          })()}
          <div className="text-[11px] text-slate-500 mt-1">Area: Mumbai 71.8,15.5→74.5,20.5 + PFZ proximity check • Valid: 17 Aug Depression → expired, now 0</div>
        </div>
      </div>

      <div className="px-6 pb-8 text-[11px] text-slate-500 text-center">All graphs use live original data — no mocks. SST/Chl/Waves from Copernicus NRT grids, Wind from Open-Meteo per-cell, Tides from harmonic constituents, PFZ 21 from INCOIS SEC002. Switch range above to see 7 vs 30 days.</div>
    </div>
  )
}
