export default function RiskCard({ risk }: { risk?: any }) {
  if (!risk) return <div className="p-3 border border-slate-800 rounded text-sm text-slate-500">No risk assessed yet</div>
  const color = risk.risk_level === 'VERY_HIGH' ? 'bg-red-900' : risk.risk_level === 'HIGH' ? 'bg-red-800' : risk.risk_level === 'MODERATE' ? 'bg-amber-800' : 'bg-green-800'
  return (
    <div className={`p-3 rounded border ${color} border-slate-700`}>
      <div className="font-bold">Risk: {risk.risk_level} ({risk.risk_score})</div>
      <div className="text-xs mt-1">{risk.risk_factors?.join(', ')}</div>
      <div className="text-xs text-slate-300 mt-1">Confidence: {risk.confidence}</div>
    </div>
  )
}
