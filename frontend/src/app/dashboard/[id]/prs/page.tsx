"use client";

import { use, useEffect, useState } from "react";
import { getPRSScores, type PRSCondition, type PRSData } from "@/lib/api";
import LoadingSpinner from "@/components/LoadingSpinner";
import StatCard from "@/components/StatCard";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function percentileColor(p: number): string {
  if (p > 80) return "bg-red-500";
  if (p >= 40) return "bg-yellow-500";
  return "bg-green-500";
}

function percentileTrackColor(p: number): string {
  if (p > 80) return "bg-red-500/20";
  if (p >= 40) return "bg-yellow-500/20";
  return "bg-green-500/20";
}

function percentileTextColor(p: number): string {
  if (p > 80) return "text-red-400";
  if (p >= 40) return "text-yellow-400";
  return "text-green-400";
}

function riskBadgeClasses(level: string): string {
  const l = level.toLowerCase();
  if (l === "high" || l === "elevated")
    return "bg-red-500/15 text-red-400 ring-red-500/30";
  if (l === "moderate" || l === "medium")
    return "bg-yellow-500/15 text-yellow-400 ring-yellow-500/30";
  return "bg-green-500/15 text-green-400 ring-green-500/30";
}

// ---------------------------------------------------------------------------
// PRS Card
// ---------------------------------------------------------------------------

function PRSCard({ condition }: { condition: PRSCondition }) {
  const pct = Math.round(condition.percentile);

  return (
    <div className="rounded-xl bg-gray-900 ring-1 ring-gray-800 p-5 flex flex-col gap-4 transition-shadow hover:shadow-lg hover:shadow-black/30">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-sm font-semibold text-gray-200 leading-tight">
          {condition.condition}
        </h3>
        {condition.risk_level && (
          <span
            className={`shrink-0 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ring-1 ring-inset ${riskBadgeClasses(condition.risk_level)}`}
          >
            {condition.risk_level}
          </span>
        )}
      </div>

      {/* Percentile */}
      <div className="flex items-end gap-3">
        <span className={`text-3xl font-bold tabular-nums ${percentileTextColor(pct)}`}>
          {pct}
          <span className="text-base font-medium text-gray-500">%ile</span>
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full">
        <div className={`h-2 w-full rounded-full ${percentileTrackColor(pct)}`}>
          <div
            className={`h-2 rounded-full transition-all ${percentileColor(pct)}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* SNP coverage */}
      {condition.snps_used != null && condition.total_snps != null && (
        <p className="text-xs text-gray-500">
          SNPs used:{" "}
          <span className="text-gray-400 font-medium">
            {condition.snps_used.toLocaleString()}
          </span>{" "}
          / {condition.total_snps.toLocaleString()}
        </p>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function PRSPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const [data, setData] = useState<PRSData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    getPRSScores(id)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message ?? "Failed to load PRS data");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [id]);

  // -- Loading / Error states ------------------------------------------------

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner size="lg" message="Loading polygenic risk scores..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="rounded-xl bg-red-500/10 p-6 text-center ring-1 ring-red-500/30">
          <p className="text-red-400 font-medium">Error loading PRS data</p>
          <p className="mt-1 text-sm text-red-400/70">{error}</p>
        </div>
      </div>
    );
  }

  if (!data || data.conditions.length === 0) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <p className="text-gray-500">No polygenic risk score data available.</p>
      </div>
    );
  }

  // -- Derived values --------------------------------------------------------

  const sorted = [...data.conditions]
    .filter((c) => c.success)
    .sort((a, b) => b.percentile - a.percentile);

  const highCount =
    data.summary?.high_risk ??
    sorted.filter((c) => c.risk_level?.toLowerCase() === "high" || c.risk_level?.toLowerCase() === "elevated").length;
  const moderateCount =
    data.summary?.moderate_risk ??
    sorted.filter((c) => c.risk_level?.toLowerCase() === "moderate" || c.risk_level?.toLowerCase() === "medium").length;

  // -- Render ----------------------------------------------------------------

  return (
    <div className="space-y-8">
      {/* Page heading */}
      <div>
        <h1 className="text-2xl font-bold text-gray-100">
          Polygenic Risk Scores
        </h1>
        <p className="mt-1 text-sm text-gray-400">
          Aggregate genetic risk estimates across multiple conditions
        </p>
      </div>

      {/* Summary bar */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          label="Conditions Assessed"
          value={sorted.length}
          accent="blue"
        />
        <StatCard
          label="High Risk"
          value={highCount}
          accent="red"
          subtitle="Percentile > 80"
        />
        <StatCard
          label="Moderate Risk"
          value={moderateCount}
          accent="yellow"
          subtitle="Percentile 40 - 80"
        />
      </div>

      {/* PRS cards grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sorted.map((c) => (
          <PRSCard key={c.condition} condition={c} />
        ))}
      </div>

      {/* Educational disclaimer */}
      <div className="rounded-xl bg-gray-900/60 p-5 ring-1 ring-gray-800">
        <p className="text-xs leading-relaxed text-gray-500">
          <span className="font-semibold text-gray-400">Disclaimer:</span>{" "}
          Polygenic risk scores (PRS) are statistical estimates based on current
          research and the variants present in your data file. They do not
          constitute a medical diagnosis. PRS accuracy varies by ancestry,
          genotyping coverage, and the trait studied. Many environmental and
          lifestyle factors also influence disease risk. Always consult a
          qualified healthcare professional or genetic counselor before making
          medical decisions based on these results.
        </p>
      </div>
    </div>
  );
}
