'use client';

import { use, useEffect, useState } from 'react';
import Link from 'next/link';
import {
  ArrowDownTrayIcon,
  BeakerIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  HeartIcon,
  SparklesIcon,
  GlobeAltIcon,
  DocumentMagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '@/components/LoadingSpinner';
import StatCard from '@/components/StatCard';
import RiskBadge from '@/components/RiskBadge';
import {
  type FullResults,
  getFullResults,
  getReportUrl,
} from '@/lib/api';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function fmtNumber(n: number): string {
  return n.toLocaleString('en-US');
}

function percentileColor(p: number): string {
  if (p < 40) return 'bg-green-500';
  if (p <= 80) return 'bg-yellow-500';
  return 'bg-red-500';
}

function percentileTextColor(p: number): string {
  if (p < 40) return 'text-green-400';
  if (p <= 80) return 'text-yellow-400';
  return 'text-red-400';
}

function riskLevel(row: Record<string, unknown>): 'high' | 'moderate' | 'low' | 'benign' {
  const sig = String(row.clinical_significance ?? row.risk ?? '').toLowerCase();
  if (sig.includes('pathogenic') || sig.includes('high')) return 'high';
  if (sig.includes('likely') || sig.includes('moderate')) return 'moderate';
  if (sig.includes('benign')) return 'benign';
  return 'low';
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function DashboardOverviewPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const [results, setResults] = useState<FullResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getFullResults(id)
      .then((data) => {
        if (!cancelled) setResults(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load results');
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
        <LoadingSpinner size="lg" message="Loading analysis results..." />
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-gray-400">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-500" />
        <p className="text-lg font-medium text-gray-200">Unable to load analysis</p>
        <p className="text-sm">{error ?? 'No results returned from the server.'}</p>
        <Link
          href="/"
          className="mt-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-500"
        >
          Back to Upload
        </Link>
      </div>
    );
  }

  // -- Derived data ----------------------------------------------------------

  const { summary, data, person_name } = results;
  const riskVariantCount = summary.pathogenic_variants + summary.high_impact_variants;

  const highImpactVariants = [
    ...(data.high_impact ?? []),
    ...(data.clinvar ?? []).filter(
      (v) => String(v.clinical_significance ?? '').toLowerCase().includes('pathogenic'),
    ),
  ].slice(0, 8);

  const prsConditions = (data.prs ?? []).filter((c) => c.success);
  const wellnessTraits = (data.wellness_traits ?? []).slice(0, 6);
  const ancestry = data.ancestry;

  // -- Render ----------------------------------------------------------------

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6 lg:px-8">
      {/* ------------------------------------------------------------------ */}
      {/* Header                                                              */}
      {/* ------------------------------------------------------------------ */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">{person_name || 'Analysis'}</h1>
          <p className="mt-1 text-sm text-gray-500">
            Analysis ID: <span className="font-mono text-gray-400">{id}</span>
          </p>
        </div>
        <a
          href={getReportUrl(id)}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-500"
        >
          <ArrowDownTrayIcon className="h-4 w-4" />
          Download Report
        </a>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Summary Cards                                                       */}
      {/* ------------------------------------------------------------------ */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="SNPs Analyzed"
          value={fmtNumber(summary.snps_analyzed)}
          accent="blue"
          icon={<DocumentMagnifyingGlassIcon className="h-6 w-6" />}
        />
        <StatCard
          label="Risk Variants Found"
          value={fmtNumber(riskVariantCount)}
          accent="red"
          subtitle={`${summary.pathogenic_variants} pathogenic + ${summary.high_impact_variants} high-impact`}
          icon={<ExclamationTriangleIcon className="h-6 w-6" />}
        />
        <StatCard
          label="PGx Variants"
          value={fmtNumber(summary.pgx_variants)}
          accent="purple"
          icon={<BeakerIcon className="h-6 w-6" />}
        />
        <StatCard
          label="PRS Conditions"
          value={fmtNumber(summary.prs_conditions)}
          accent="teal"
          icon={<ChartBarIcon className="h-6 w-6" />}
        />
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* A) Clinical Risk Summary                                            */}
      {/* ------------------------------------------------------------------ */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <HeartIcon className="h-5 w-5 text-red-400" />
            <h2 className="text-lg font-semibold text-gray-100">Clinical Risk Summary</h2>
          </div>
          <Link
            href={`/dashboard/${id}/clinical`}
            className="text-sm font-medium text-blue-400 transition-colors hover:text-blue-300"
          >
            View all &rarr;
          </Link>
        </div>

        {highImpactVariants.length === 0 ? (
          <p className="text-sm text-gray-500">No high-impact variants detected.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-gray-800 text-xs uppercase tracking-wider text-gray-500">
                <tr>
                  <th className="px-4 py-2.5">rsID</th>
                  <th className="px-4 py-2.5">Gene</th>
                  <th className="px-4 py-2.5">Risk</th>
                  <th className="px-4 py-2.5">Genotype</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {highImpactVariants.map((v, i) => (
                  <tr key={String(v.rsid ?? i)} className="transition-colors hover:bg-gray-800/40">
                    <td className="whitespace-nowrap px-4 py-2.5 font-mono text-gray-300">
                      {String(v.rsid ?? v.rs_id ?? '-')}
                    </td>
                    <td className="whitespace-nowrap px-4 py-2.5 text-gray-300">
                      {String(v.gene ?? v.gene_symbol ?? '-')}
                    </td>
                    <td className="whitespace-nowrap px-4 py-2.5">
                      <RiskBadge level={riskLevel(v)} />
                    </td>
                    <td className="whitespace-nowrap px-4 py-2.5 font-mono text-gray-400">
                      {String(v.genotype ?? '-')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* B) PRS Overview                                                     */}
      {/* ------------------------------------------------------------------ */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ChartBarIcon className="h-5 w-5 text-teal-400" />
            <h2 className="text-lg font-semibold text-gray-100">Polygenic Risk Scores</h2>
          </div>
          <Link
            href={`/dashboard/${id}/prs`}
            className="text-sm font-medium text-blue-400 transition-colors hover:text-blue-300"
          >
            View all &rarr;
          </Link>
        </div>

        {prsConditions.length === 0 ? (
          <p className="text-sm text-gray-500">No PRS data available.</p>
        ) : (
          <div className="space-y-4">
            {prsConditions.map((c) => (
              <div key={c.condition}>
                <div className="mb-1 flex items-center justify-between text-sm">
                  <span className="font-medium text-gray-300">{c.condition}</span>
                  <span className={`font-semibold ${percentileTextColor(c.percentile)}`}>
                    {c.percentile.toFixed(0)}th percentile
                  </span>
                </div>
                <div className="h-2.5 w-full overflow-hidden rounded-full bg-gray-800">
                  <div
                    className={`h-full rounded-full transition-all ${percentileColor(c.percentile)}`}
                    style={{ width: `${Math.min(c.percentile, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* C) Wellness Highlights                                              */}
      {/* ------------------------------------------------------------------ */}
      <section>
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <SparklesIcon className="h-5 w-5 text-yellow-400" />
            <h2 className="text-lg font-semibold text-gray-100">Wellness Highlights</h2>
          </div>
          <Link
            href={`/dashboard/${id}/wellness`}
            className="text-sm font-medium text-blue-400 transition-colors hover:text-blue-300"
          >
            View all &rarr;
          </Link>
        </div>

        {wellnessTraits.length === 0 ? (
          <p className="text-sm text-gray-500">No wellness data available.</p>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {wellnessTraits.map((t, i) => (
              <div
                key={t.rsid ?? i}
                className="rounded-xl border border-gray-800 bg-gray-900 p-4 transition-shadow hover:shadow-lg hover:shadow-black/20"
              >
                {t.category && (
                  <span className="mb-2 inline-block rounded-full bg-yellow-500/10 px-2.5 py-0.5 text-xs font-medium text-yellow-400 ring-1 ring-inset ring-yellow-500/20">
                    {t.category}
                  </span>
                )}
                <h3 className="text-sm font-semibold text-gray-200">{t.trait}</h3>
                {t.gene && (
                  <p className="mt-0.5 text-xs text-gray-500">
                    {t.gene}
                    {t.genotype && (
                      <span className="ml-1 font-mono text-gray-400">{t.genotype}</span>
                    )}
                  </p>
                )}
                {t.interpretation && (
                  <p className="mt-2 text-xs leading-relaxed text-gray-400">
                    {t.interpretation}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* D) Ancestry                                                         */}
      {/* ------------------------------------------------------------------ */}
      {ancestry && ancestry.success && (
        <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
          <div className="mb-4 flex items-center gap-2">
            <GlobeAltIcon className="h-5 w-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-gray-100">Ancestry</h2>
          </div>

          <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
            {/* Primary result */}
            <div className="flex-1">
              <p className="text-sm text-gray-500">Primary Ancestry</p>
              <p className="mt-1 text-xl font-bold text-gray-100">
                {ancestry.primary_ancestry ?? 'Unknown'}
              </p>
              {ancestry.confidence != null && (
                <p className="mt-0.5 text-sm text-gray-400">
                  Confidence: {(ancestry.confidence * 100).toFixed(1)}%
                </p>
              )}
              {ancestry.method && (
                <p className="mt-0.5 text-xs text-gray-500">Method: {ancestry.method}</p>
              )}
              {ancestry.snps_used != null && (
                <p className="mt-0.5 text-xs text-gray-500">
                  SNPs used: {fmtNumber(ancestry.snps_used)}
                </p>
              )}
            </div>

            {/* Probability breakdown */}
            {ancestry.probabilities && Object.keys(ancestry.probabilities).length > 0 && (
              <div className="flex-1">
                <p className="mb-2 text-sm text-gray-500">Population Probabilities</p>
                <div className="space-y-2">
                  {Object.entries(ancestry.probabilities)
                    .sort(([, a], [, b]) => b - a)
                    .map(([pop, prob]) => (
                      <div key={pop}>
                        <div className="mb-0.5 flex items-center justify-between text-xs">
                          <span className="text-gray-300">{pop}</span>
                          <span className="font-mono text-gray-400">
                            {(prob * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-800">
                          <div
                            className="h-full rounded-full bg-blue-500"
                            style={{ width: `${Math.min(prob * 100, 100)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
