import { useEffect, useState } from 'react'
import ReactECharts from 'echarts-for-react'
import { api } from '../../api/client'

export function SstChart() {
  const [dates, setDates] = useState<string[]>([])
  const [sst, setSst] = useState<number[]>([])
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    const token = localStorage.getItem('orca_token')
    const fetchData = async () => {
      try {
        const headers: any = token ? { Authorization: 'Bearer ' + token } : {}
        const res = await api.get('/ocean/history', { params: { latitude: 19.076, longitude: 72.877, limit: 7 }, headers })
        const items = res.data.items || []
        const labels = items.map((r:any) => r.observation_time ? new Date(r.observation_time).toLocaleDateString('en-IN',{day:'2-digit',month:'short'}) : '')
        const temps = items.map((r:any) => r.sst ?? null)
        if (labels.length && temps.some((v:any) => v != null)) { setDates(labels); setSst(temps) }
        else { setDates([]); setSst([]) }
      } catch {
        try {
          const res = await api.get('/weather/', { params: { latitude: 19.076, longitude: 72.877, limit: 7 }, headers: token ? { Authorization: 'Bearer ' + token } : {} })
          const items = [...(res.data.items||[])].sort((a:any,b:any) => new Date(a.observation_time).getTime() - new Date(b.observation_time).getTime())
          if (items.length) { setDates(items.map((r:any) => new Date(r.observation_time).toLocaleDateString('en-IN',{day:'2-digit',month:'short'}))); setSst(items.map((r:any) => r.temperature)) }
          else { setDates([]); setSst([]) }
        } catch { setDates([]); setSst([]) }
      } finally { setLoading(false) }
    }
    fetchData()
  }, [])
  const option = {
    backgroundColor: 'transparent',
    textStyle: { color: '#94a3b8' },
    title: { text: loading ? 'SST past 7 days (loading)...' : 'SST past 7 days to today (Mumbai)', textStyle: { color: '#64748b', fontSize: 11 } },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 30, fontSize: 9 } },
    yAxis: { type: 'value', name: 'SST C', min: 26 },
    series: [{ data: sst, type: 'line', smooth: true, lineStyle: { color: '#0ea5e9', width: 2 }, areaStyle: { color: 'rgba(14,165,233,0.15)' } }],
  }
  return <ReactECharts option={option} style={{ height: 220 }} />
}

export function ChlorophyllChart() {
  const [dates, setDates] = useState<string[]>([])
  const [chl, setChl] = useState<number[]>([])
  useEffect(() => {
    const fetchChl = async () => {
      // Real Copernicus NRT chlorophyll first - 7 days for command centre (no flat mock fallback)
      try {
        const res = await api.get('/ocean/chlorophyll-history', { params: { latitude: 19.076, longitude: 72.877, limit: 7 } })
        const items = res.data.items || []
        if (items.length) {
          setDates(items.map((r: any) => new Date(r.observation_time).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })))
          setChl(items.map((r: any) => r.chlorophyll))
          return
        }
      } catch { /* fall through to DB series */ }
      try {
        const token = localStorage.getItem('orca_token')
        const headers: any = token ? { Authorization: 'Bearer ' + token } : {}
        const res = await api.get('/ocean/history', { params: { latitude: 19.076, longitude: 72.877, limit: 7 }, headers })
        const items = (res.data.items || []).filter((r: any) => r.chlorophyll != null)
        if (items.length) {
          setDates(items.map((r: any) => new Date(r.observation_time).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' })))
          setChl(items.map((r: any) => r.chlorophyll))
          return
        }
        setDates([]); setChl([])
      } catch {
        setDates([]); setChl([])
      }
    }
    fetchChl()
  }, [])
  const option = {
    backgroundColor: 'transparent',
    textStyle: { color: '#94a3b8' },
    title: { text: 'Chlorophyll past 7 days to today (Mumbai)', textStyle: { color: '#64748b', fontSize: 10 } },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 30, fontSize: 9 } },
    yAxis: { type: 'value', name: 'Chl mg/m3' },
    series: [{ data: chl, type: 'bar', itemStyle: { color: '#10b981' } }],
  }
  return <ReactECharts option={option} style={{ height: 220 }} />
}
