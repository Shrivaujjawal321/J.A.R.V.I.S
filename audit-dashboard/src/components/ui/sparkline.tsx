"use client";

import { LineChart, Line, ResponsiveContainer, Tooltip } from "recharts";

interface SparklineProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
}

export function Sparkline({
  data,
  width = 80,
  height = 24,
  color = "var(--accent)",
}: SparklineProps) {
  const chartData = data.map((v, i) => ({ i, v }));

  return (
    <ResponsiveContainer width={width} height={height}>
      <LineChart data={chartData}>
        <Line
          type="monotone"
          dataKey="v"
          stroke={color}
          strokeWidth={1.5}
          dot={false}
          isAnimationActive={false}
        />
        <Tooltip
          content={({ active, payload }) => {
            if (!active || !payload?.[0]) return null;
            return (
              <div
                className="rounded border px-1.5 py-1 text-xs shadow"
                style={{
                  background: "var(--surface-raised)",
                  borderColor: "var(--border)",
                  color: "var(--text)",
                }}
              >
                {payload[0].value}
              </div>
            );
          }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
