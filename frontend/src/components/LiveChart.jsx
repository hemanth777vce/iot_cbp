import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { Activity } from 'lucide-react';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <div className="tooltip-time">{label || (payload[0] && payload[0].payload.timestamp)}</div>
        {payload.map((entry, index) => (
          <div key={`tooltip-item-${index}`} className="tooltip-item">
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span className="tooltip-dot" style={{ backgroundColor: entry.color }} />
              <span>{entry.name}:</span>
            </span>
            <span className="mono" style={{ fontWeight: 600 }}>
              {entry.value} {entry.unit || ''}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export default function LiveChart({
  data = [],
  lines = [],
  height = 260,
  emptyMessage = 'No telemetry data available yet',
  dualAxis = false,
}) {
  if (!data || data.length === 0) {
    return (
      <div className="empty-state" style={{ minHeight: height }}>
        <Activity className="empty-icon" />
        <p className="empty-title">Waiting for Telemetry</p>
        <p className="empty-desc">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis
            dataKey="time_label"
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
            dy={8}
          />
          <YAxis
            yAxisId="left"
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
            dx={-4}
          />
          {dualAxis && (
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              dx={4}
            />
          )}
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            wrapperStyle={{ paddingBottom: '12px', fontSize: '12px' }}
          />
          {lines.map((l) => (
            <Line
              key={l.dataKey}
              yAxisId={l.yAxisId || 'left'}
              type="monotone"
              dataKey={l.dataKey}
              name={l.name || l.dataKey}
              stroke={l.color || '#2563eb'}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 5 }}
              unit={l.unit}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
