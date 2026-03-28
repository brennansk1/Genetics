"use client";

import { use, useEffect, useState } from "react";
import { getPGxReport, type PGxData } from "@/lib/api";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Map a metabolizer phenotype string to a color scheme. */
function phenotypeColor(phenotype: string): {
  bg: string;
  text: string;
  ring: string;
} {
  const p = phenotype?.toLowerCase() ?? "";
  if (p.includes("poor")) {
    return {
      bg: "bg-red-500/20",
      text: "text-red-400",
      ring: "ring-red-500/30",
    };
  }
  if (p.includes("intermediate")) {
    return {
      bg: "bg-amber-500/20",
      text: "text-amber-400",
      ring: "ring-amber-500/30",
    };
  }
  if (p.includes("ultra") || p.includes("rapid")) {
    return {
      bg: "bg-blue-500/20",
      text: "text-blue-400",
      ring: "ring-blue-500/30",
    };
  }
  // Normal / Extensive / default
  return {
    bg: "bg-green-500/20",
    text: "text-green-400",
    ring: "ring-green-500/30",
  };
}

function PhenotypeBadge({ phenotype }: { phenotype: string }) {
  const { bg, text, ring } = phenotypeColor(phenotype);
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1 ${bg} ${text} ${ring}`}
    >
      {phenotype || "Unknown"}
    </span>
  );
}

function StatCard({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent?: "red" | "amber" | "green" | "blue";
}) {
  const colorMap = {
    red: "text-red-400",
    amber: "text-amber-400",
    green: "text-green-400",
    blue: "text-blue-400",
  };
  const valueColor = accent ? colorMap[accent] : "text-white";
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 px-5 py-4">
      <p className="text-sm text-gray-400">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${valueColor}`}>{value}</p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Phenotype legend
// ---------------------------------------------------------------------------

function PhenotypeLegend() {
  const items = [
    { label: "Poor Metabolizer", color: "bg-red-400" },
    { label: "Intermediate Metabolizer", color: "bg-amber-400" },
    { label: "Normal Metabolizer", color: "bg-green-400" },
    { label: "Rapid / Ultra-rapid Metabolizer", color: "bg-blue-400" },
  ];
  return (
    <div className="flex flex-wrap gap-4">
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-2 text-xs text-gray-400">
          <span className={`inline-block h-2.5 w-2.5 rounded-full ${item.color}`} />
          {item.label}
        </div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function PharmacogenomicsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const [pgx, setPgx] = useState<PGxData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      try {
        const data = await getPGxReport(id);
        if (!cancelled) setPgx(data);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load pharmacogenomics data",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchData();
    return () => {
      cancelled = true;
    };
  }, [id]);

  // -- Loading / Error states -----------------------------------------------

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-700 border-t-blue-500" />
          <p className="text-sm text-gray-400">Loading pharmacogenomics report&hellip;</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-6 py-4 text-red-400">
          {error}
        </div>
      </div>
    );
  }

  // -- Render ---------------------------------------------------------------

  const totalGenes = pgx?.summary.total_genes ?? 0;
  const actionable = pgx?.summary.actionable ?? 0;

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-8 text-gray-100 sm:px-6 lg:px-8">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Pharmacogenomics Report
        </h1>
        <p className="mt-1 text-sm text-gray-400">
          How your genetics may influence drug metabolism and medication response
        </p>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <StatCard label="Genes Analyzed" value={totalGenes} accent="blue" />
        <StatCard label="Actionable Findings" value={actionable} accent="amber" />
        <StatCard
          label="Normal Metabolism"
          value={totalGenes - actionable}
          accent="green"
        />
      </div>

      {/* Phenotype legend */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-400">
          Metabolizer Status Legend
        </h2>
        <PhenotypeLegend />
      </section>

      {/* ----------------------------------------------------------------- */}
      {/* Drug Metabolism Table                                              */}
      {/* ----------------------------------------------------------------- */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-4 text-xl font-semibold text-white">
          Drug Metabolism Results
        </h2>
        {pgx && pgx.results.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-xs uppercase tracking-wider text-gray-500">
                  <th className="px-4 py-3">rsID / Gene</th>
                  <th className="px-4 py-3">Drug Relevance</th>
                  <th className="px-4 py-3">Genotype</th>
                  <th className="px-4 py-3">Interpretation</th>
                  <th className="px-4 py-3">Phenotype</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {pgx.results.map((r, i) => {
                  const phenotype = String(
                    r.phenotype ?? r.metabolizer_status ?? r.predicted_phenotype ?? "",
                  );
                  const { text: rowAccent } = phenotypeColor(phenotype);
                  return (
                    <tr
                      key={i}
                      className="transition-colors hover:bg-gray-800/60"
                    >
                      <td className="whitespace-nowrap px-4 py-3">
                        <div className="font-mono text-blue-400">
                          {String(r.rsid ?? r.rsID ?? "-")}
                        </div>
                        <div className="text-xs font-medium text-white">
                          {String(r.gene ?? "-")}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-gray-300">
                        {String(r.drug ?? r.relevance ?? r.drug_relevance ?? "-")}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3 font-mono">
                        {String(r.genotype ?? "-")}
                      </td>
                      <td className="max-w-xs truncate px-4 py-3 text-gray-300">
                        {String(r.interpretation ?? r.guideline ?? "-")}
                      </td>
                      <td className="whitespace-nowrap px-4 py-3">
                        <PhenotypeBadge phenotype={phenotype} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-gray-500">
            No pharmacogenomic variants detected in analyzed genes.
          </p>
        )}
      </section>

      {/* Disclaimer */}
      <footer className="rounded-xl border border-gray-800 bg-gray-900/50 px-6 py-4">
        <p className="text-xs leading-relaxed text-gray-500">
          <span className="font-semibold text-gray-400">Disclaimer:</span> This
          pharmacogenomics report is for informational and educational purposes
          only. Drug metabolism predictions are based on known genetic associations
          and may not account for all factors influencing drug response (e.g.,
          drug-drug interactions, organ function, body weight). Always consult your
          physician or pharmacist before modifying any medication regimen based on
          genetic information.
        </p>
      </footer>
    </div>
  );
}
