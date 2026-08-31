import ReactECharts from 'echarts-for-react'

export function SstChart() {
  const option = {
    backgroundColor: 'transparent',
    textStyle: { color: '#94a3b8' },
    title: { text: 'SST trend (sample from PFZ 27.5-29.3°C)', textStyle: { color: '#64748b', fontSize: 11 } },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Gujarat','Mumbai','Goa','Karnataka','Kochi','Chennai','Vizag','Odisha','Andaman'] },
    yAxis: { type: 'value', name: 'SST °C', min: 27 },
    series: [{ data: [27.5,27.9,28.5,28.6,29.1,28.8,28.4,28.0,29.3], type: 'line', smooth: true, lineStyle: { color: '#0ea5e9' } }],
  }
  return <ReactECharts option={option} style={{ height: 200 }} />
}

export function ChlorophyllChart() {
  const option = {
    backgroundColor: 'transparent',
    textStyle: { color: '#94a3b8' },
    title: { text: 'Chlorophyll (mg/m3) — fish food proxy', textStyle: { color: '#64748b', fontSize: 11 } },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Gujarat','Mumbai','Goa','Karnataka','Kochi','Chennai','Vizag','Odisha','Andaman'] },
    yAxis: { type: 'value', name: 'Chl' },
    series: [{ data: [0.5,0.7,0.7,0.9,1.1,0.6,0.9,0.8,1.0], type: 'bar', itemStyle: { color: '#10b981' } }],
  }
  return <ReactECharts option={option} style={{ height: 200 }} />
}
