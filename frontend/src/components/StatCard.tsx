import { type ReactNode } from "react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  accent?: "blue" | "teal" | "red" | "yellow" | "green" | "purple";
  subtitle?: string;
}

const accentMap: Record<string, string> = {
  blue: "text-blue-400",
  teal: "text-teal-400",
  red: "text-red-400",
  yellow: "text-yellow-400",
  green: "text-green-400",
  purple: "text-purple-400",
};

const ringMap: Record<string, string> = {
  blue: "ring-blue-500/20",
  teal: "ring-teal-500/20",
  red: "ring-red-500/20",
  yellow: "ring-yellow-500/20",
  green: "ring-green-500/20",
  purple: "ring-purple-500/20",
};

export default function StatCard({
  label,
  value,
  icon,
  accent = "blue",
  subtitle,
}: StatCardProps) {
  return (
    <div
      className={`rounded-xl bg-gray-900 p-5 ring-1 ${ringMap[accent]} transition-shadow hover:shadow-lg hover:shadow-black/30`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-400">{label}</p>
          <p className={`mt-1 text-2xl font-bold ${accentMap[accent]}`}>
            {value}
          </p>
          {subtitle && (
            <p className="mt-0.5 text-xs text-gray-500">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className={`${accentMap[accent]} opacity-70`}>{icon}</div>
        )}
      </div>
    </div>
  );
}
