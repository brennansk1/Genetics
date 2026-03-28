type RiskLevel = "high" | "moderate" | "low" | "benign" | "carrier" | "non-carrier" | "affected";

interface RiskBadgeProps {
  level: RiskLevel;
  /** Custom label override. If omitted the level name is shown. */
  label?: string;
}

const colorMap: Record<RiskLevel, string> = {
  high: "bg-red-500/15 text-red-400 ring-red-500/30",
  moderate: "bg-yellow-500/15 text-yellow-400 ring-yellow-500/30",
  low: "bg-green-500/15 text-green-400 ring-green-500/30",
  benign: "bg-gray-500/15 text-gray-400 ring-gray-500/30",
  carrier: "bg-yellow-500/15 text-yellow-400 ring-yellow-500/30",
  "non-carrier": "bg-green-500/15 text-green-400 ring-green-500/30",
  affected: "bg-red-500/15 text-red-400 ring-red-500/30",
};

export default function RiskBadge({ level, label }: RiskBadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ring-1 ring-inset ${colorMap[level]}`}
    >
      {label ?? level}
    </span>
  );
}
