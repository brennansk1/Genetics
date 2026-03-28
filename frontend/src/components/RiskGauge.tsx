"use client";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Cell,
  ReferenceLine,
  Tooltip,
} from "recharts";

interface RiskGaugeProps {
  /** Percentile 0 - 100. */
  percentile: number;
  /** The condition name displayed above. */
  label: string;
  /** Risk category drives the accent color. */
  risk: "high" | "moderate" | "low";
}

const barColor: Record<string, string> = {
  high: "#ef4444",
  moderate: "#eab308",
  low: "#22c55e",
};

export default function RiskGauge({ percentile, label, risk }: RiskGaugeProps) {
  const data = [{ name: label, value: percentile }];

  return (
    <div className="flex flex-col items-center">
      <p className="mb-1 text-xs font-medium uppercase tracking-wider text-gray-400">
        {label}
      </p>
      <div className="h-36 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 10, right: 20, bottom: 10, left: 10 }}
          >
            <XAxis type="number" domain={[0, 100]} hide />
            <YAxis type="category" dataKey="name" hide />
            <Tooltip
              cursor={false}
              contentStyle={{
                backgroundColor: "#111827",
                border: "1px solid #374151",
                borderRadius: "0.5rem",
                fontSize: "0.75rem",
              }}
              formatter={(value) => [`${value}th percentile`, "Score"]}
            />
            {/* Background track */}
            <Bar dataKey={() => 100} fill="#1f2937" radius={[6, 6, 6, 6]} barSize={28} isAnimationActive={false} />
            {/* Value bar */}
            <Bar dataKey="value" radius={[6, 6, 6, 6]} barSize={28}>
              <Cell fill={barColor[risk]} />
            </Bar>
            <ReferenceLine x={50} stroke="#6b7280" strokeDasharray="3 3" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-1 text-lg font-bold" style={{ color: barColor[risk] }}>
        {percentile}<span className="text-xs font-normal text-gray-500">th</span>
      </p>
    </div>
  );
}
