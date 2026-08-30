import ReactECharts from 'echarts-for-react'

export function SstChart() {
  const option = {
    backgroundColor: 'transparent',
    textStyle: { color: '#94a3b8' },
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
    yAxis: { type: 'value', name: 'SST °C' },
    series: [{ data: [27.8, 28.2, 28.5, 27.9, 28.1], type: 'line', smooth: true, lineStyle: { color: '#0ea5e9' } }],
  }
  return <ReactECharts option={option} style={{ height: 200 }} />
}

export function ChlorophyllChart() {
  const option = {
    backgroundColor: 'transparent',
    textStyle: { color: '#94a3b8' },
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
    yAxis: { type: 'value', name: 'Chl mg/m3' },
    series: [{ data: [0.6, 0.8, 1.1, 0.9, 0.7], type: 'bar', itemStyle: { color: '#10b981' } }],
  }
  return <ReactECharts option={option} style={{ height: 200 }} />
}
