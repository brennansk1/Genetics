'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowDownTrayIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  UserGroupIcon,
  BeakerIcon,
  ChartBarIcon,
  HeartIcon,
  ShieldCheckIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import LoadingSpinner from '@/components/LoadingSpinner';
import RiskBadge from '@/components/RiskBadge';
import {
  type FamilyComparisonResult,
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

function fmtPct(n: number, decimals = 1): string {
  return `${n.toFixed(decimals)}%`;
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

function riskLevelFromString(s: string): 'high' | 'moderate' | 'low' | 'benign' {
  const lower = s.toLowerCase();
  if (lower.includes('high') || lower.includes('pathogenic')) return 'high';
  if (lower.includes('moderate') || lower.includes('likely')) return 'moderate';
  if (lower.includes('benign')) return 'benign';
  return 'low';
}

// ---------------------------------------------------------------------------
// IBS Gauge Component
// ---------------------------------------------------------------------------

function IBSGauge({ percentage }: { percentage: number }) {
  const radius = 70;
  const stroke = 10;
  const circumference = 2 * Math.PI * radius;
  const filled = (percentage / 100) * circumference;
  const color =
    percentage >= 75 ? '#22c55e' : percentage >= 50 ? '#eab308' : '#ef4444';

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="180" height="180" className="-rotate-90">
        <circle
          cx="90"
          cy="90"
          r={radius}
          fill="none"
          stroke="#1f2937"
          strokeWidth={stroke}
        />
        <circle
          cx="90"
          cy="90"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={circumference - filled}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-bold text-gray-100">
          {percentage.toFixed(1)}%
        </span>
        <span className="text-xs text-gray-500">IBS Score</span>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Shared Variants Table
// ---------------------------------------------------------------------------

function SharedVariantsTable({
  title,
  variants,
  emptyMessage,
}: {
  title: string;
  variants: Record<string, unknown>[];
  emptyMessage: string;
}) {
  if (!variants || variants.length === 0) {
    return (
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
        <h3 className="mb-3 text-sm font-semibold text-gray-300">{title}</h3>
        <p className="text-sm text-gray-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
      <h3 className="mb-3 text-sm font-semibold text-gray-300">{title}</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-gray-800 text-xs uppercase tracking-wider text-gray-500">
            <tr>
              <th className="px-3 py-2">rsID</th>
              <th className="px-3 py-2">Gene</th>
              <th className="px-3 py-2">Risk / Significance</th>
              <th className="px-3 py-2">Genotype</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60">
            {variants.map((v, i) => (
              <tr key={String(v.rsid ?? v.rs_id ?? i)} className="transition-colors hover:bg-gray-800/40">
                <td className="whitespace-nowrap px-3 py-2 font-mono text-gray-300">
                  {String(v.rsid ?? v.rs_id ?? '-')}
                </td>
                <td className="whitespace-nowrap px-3 py-2 text-gray-300">
                  {String(v.gene ?? v.gene_symbol ?? '-')}
                </td>
                <td className="whitespace-nowrap px-3 py-2">
                  <RiskBadge
                    level={riskLevelFromString(
                      String(v.clinical_significance ?? v.risk ?? v.significance ?? 'low'),
                    )}
                    label={String(v.clinical_significance ?? v.risk ?? v.significance ?? '-')}
                  />
                </td>
                <td className="whitespace-nowrap px-3 py-2 font-mono text-gray-400">
                  {String(v.genotype ?? '-')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// PRS Comparison Bar
// ---------------------------------------------------------------------------

function PRSComparisonBar({
  condition,
  p1Percentile,
  p2Percentile,
  p1Name,
  p2Name,
}: {
  condition: string;
  p1Percentile: number;
  p2Percentile: number;
  p1Name: string;
  p2Name: string;
}) {
  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-gray-300">{condition}</p>
      {/* Person 1 */}
      <div className="flex items-center gap-3">
        <span className="w-20 truncate text-xs text-blue-400">{p1Name}</span>
        <div className="flex-1">
          <div className="h-3 w-full overflow-hidden rounded-full bg-gray-800">
            <div
              className="h-full rounded-full bg-blue-500 transition-all duration-700 ease-out"
              style={{ width: `${Math.min(p1Percentile, 100)}%` }}
            />
          </div>
        </div>
        <span className={`w-16 text-right text-xs font-semibold ${percentileTextColor(p1Percentile)}`}>
          {p1Percentile.toFixed(0)}th
        </span>
      </div>
      {/* Person 2 */}
      <div className="flex items-center gap-3">
        <span className="w-20 truncate text-xs text-teal-400">{p2Name}</span>
        <div className="flex-1">
          <div className="h-3 w-full overflow-hidden rounded-full bg-gray-800">
            <div
              className="h-full rounded-full bg-teal-500 transition-all duration-700 ease-out"
              style={{ width: `${Math.min(p2Percentile, 100)}%` }}
            />
          </div>
        </div>
        <span className={`w-16 text-right text-xs font-semibold ${percentileTextColor(p2Percentile)}`}>
          {p2Percentile.toFixed(0)}th
        </span>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Page Content (reads searchParams)
// ---------------------------------------------------------------------------

function FamilyComparisonContent() {
  const searchParams = useSearchParams();
  const comparisonId = searchParams.get('id') ?? '';
  const p1Id = searchParams.get('p1') ?? '';
  const p2Id = searchParams.get('p2') ?? '';

  const [comparison, setComparison] = useState<FamilyComparisonResult | null>(null);
  const [results1, setResults1] = useState<FullResults | null>(null);
  const [results2, setResults2] = useState<FullResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        // Load comparison data from sessionStorage
        const stored = sessionStorage.getItem('familyComparison');
        let compData: FamilyComparisonResult | null = null;

        if (stored) {
          try {
            compData = JSON.parse(stored) as FamilyComparisonResult;
          } catch {
            compData = null;
          }
        }

        if (!compData && comparisonId) {
          // Fallback: try fetching from the API
          const res = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}/analysis/results/${comparisonId}`,
          );
          if (res.ok) {
            compData = (await res.json()) as FamilyComparisonResult;
          }
        }

        if (!compData) {
          throw new Error('No comparison data found. Please run a family comparison first.');
        }

        // Determine the person IDs from comparison data or URL params
        const person1Id = p1Id || compData.person1_analysis_id;
        const person2Id = p2Id || compData.person2_analysis_id;

        // Fetch individual results in parallel
        const [r1, r2] = await Promise.all([
          getFullResults(person1Id).catch(() => null),
          getFullResults(person2Id).catch(() => null),
        ]);

        if (!cancelled) {
          setComparison(compData);
          setResults1(r1);
          setResults2(r2);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load comparison data');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [comparisonId, p1Id, p2Id]);

  // -- Loading ---------------------------------------------------------------

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner size="lg" message="Loading family comparison..." />
      </div>
    );
  }

  // -- Error -----------------------------------------------------------------

  if (error || !comparison) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-gray-400">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-500" />
        <p className="text-lg font-medium text-gray-200">Unable to load comparison</p>
        <p className="max-w-md text-center text-sm">{error ?? 'No comparison data found.'}</p>
        <Link
          href="/"
          className="mt-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-500"
        >
          Back to Home
        </Link>
      </div>
    );
  }

  // -- Derived data ----------------------------------------------------------

  const { person1, person2, relationship, mendelian_analysis, shared_variants, prs_comparison } =
    comparison;

  const p1Name = person1.name || 'Person 1';
  const p2Name = person2.name || 'Person 2';

  // Build PRS comparison pairs from the comparison data
  const prsPairs: {
    condition: string;
    p1Percentile: number;
    p2Percentile: number;
    p1Risk: string;
    p2Risk: string;
  }[] = [];

  if (prs_comparison && Array.isArray(prs_comparison)) {
    for (const entry of prs_comparison) {
      const e = entry as Record<string, unknown>;
      prsPairs.push({
        condition: String(e.condition ?? ''),
        p1Percentile: Number(e.person1_percentile ?? e.percentile_1 ?? 0),
        p2Percentile: Number(e.person2_percentile ?? e.percentile_2 ?? 0),
        p1Risk: String(e.person1_risk_level ?? e.risk_1 ?? '-'),
        p2Risk: String(e.person2_risk_level ?? e.risk_2 ?? '-'),
      });
    }
  }

  // Fallback: build pairs from individual results if comparison data lacks them
  if (prsPairs.length === 0 && results1 && results2) {
    const r1Map = new Map(
      (results1.data.prs ?? []).filter((c) => c.success).map((c) => [c.condition, c]),
    );
    for (const c2 of (results2.data.prs ?? []).filter((c) => c.success)) {
      const c1 = r1Map.get(c2.condition);
      if (c1) {
        prsPairs.push({
          condition: c2.condition,
          p1Percentile: c1.percentile,
          p2Percentile: c2.percentile,
          p1Risk: c1.risk_level ?? '-',
          p2Risk: c2.risk_level ?? '-',
        });
      }
    }
  }

  // -- Render ----------------------------------------------------------------

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6 lg:px-8">
      {/* ------------------------------------------------------------------ */}
      {/* Header                                                              */}
      {/* ------------------------------------------------------------------ */}
      <div className="text-center">
        <div className="mb-2 flex items-center justify-center gap-2">
          <UserGroupIcon className="h-8 w-8 text-blue-400" />
          <h1 className="text-3xl font-bold text-gray-100">Family DNA Comparison</h1>
        </div>
        <div className="mt-4 flex items-center justify-center gap-3">
          <span className="rounded-lg bg-blue-500/10 px-4 py-2 text-lg font-semibold text-blue-400 ring-1 ring-inset ring-blue-500/20">
            {p1Name}
          </span>
          <span className="text-gray-500">vs</span>
          <span className="rounded-lg bg-teal-500/10 px-4 py-2 text-lg font-semibold text-teal-400 ring-1 ring-inset ring-teal-500/20">
            {p2Name}
          </span>
        </div>
        {comparisonId && (
          <p className="mt-2 text-xs text-gray-600">
            Comparison ID: <span className="font-mono text-gray-500">{comparisonId}</span>
          </p>
        )}
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* 2. Relationship Analysis (Hero)                                     */}
      {/* ------------------------------------------------------------------ */}
      <section className="overflow-hidden rounded-2xl border border-gray-800 bg-gradient-to-br from-gray-900 via-gray-900 to-blue-950/30 p-8">
        <div className="flex items-center gap-2 mb-6">
          <ShieldCheckIcon className="h-6 w-6 text-blue-400" />
          <h2 className="text-xl font-bold text-gray-100">Relationship Analysis</h2>
        </div>

        <div className="flex flex-col items-center gap-8 lg:flex-row lg:justify-around">
          {/* IBS Gauge */}
          <div className="flex flex-col items-center">
            <IBSGauge percentage={relationship.ibs_percentage} />
            <p className="mt-3 text-sm text-gray-400">Identity-by-State</p>
          </div>

          {/* Predicted Relationship */}
          <div className="flex flex-col items-center text-center lg:items-start lg:text-left">
            <p className="text-xs uppercase tracking-widest text-gray-500">Predicted Relationship</p>
            <p className="mt-1 text-2xl font-bold text-gray-100">
              {relationship.predicted_relationship}
            </p>
            <div className="mt-4 grid grid-cols-2 gap-x-8 gap-y-3">
              <div>
                <p className="text-xs text-gray-500">Common SNPs</p>
                <p className="text-lg font-semibold text-gray-200">
                  {fmtNumber(relationship.common_snps)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">IBS Score</p>
                <p className="text-lg font-semibold text-gray-200">
                  {fmtNumber(relationship.ibs_score)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">IBS Percentage</p>
                <p className="text-lg font-semibold text-gray-200">
                  {fmtPct(relationship.ibs_percentage)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* 3. Mendelian Analysis                                               */}
      {/* ------------------------------------------------------------------ */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <div className="flex items-center gap-2 mb-5">
          <HeartIcon className="h-5 w-5 text-purple-400" />
          <h2 className="text-lg font-semibold text-gray-100">Mendelian Analysis</h2>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg bg-gray-800/50 p-4">
            <p className="text-xs text-gray-500">Total Comparisons</p>
            <p className="mt-1 text-xl font-bold text-gray-200">
              {fmtNumber(mendelian_analysis.total_comparisons)}
            </p>
          </div>
          <div className="rounded-lg bg-gray-800/50 p-4">
            <p className="text-xs text-gray-500">Mendelian Errors</p>
            <p className="mt-1 text-xl font-bold text-yellow-400">
              {fmtNumber(mendelian_analysis.mendelian_errors)}
            </p>
          </div>
          <div className="rounded-lg bg-gray-800/50 p-4">
            <p className="text-xs text-gray-500">Error Rate</p>
            <p className="mt-1 text-xl font-bold text-gray-200">
              {fmtPct(mendelian_analysis.error_rate_percentage, 2)}
            </p>
          </div>
          <div className="rounded-lg bg-gray-800/50 p-4">
            <p className="text-xs text-gray-500">Parent-Child Confirmed</p>
            <div className="mt-1 flex items-center gap-2">
              {mendelian_analysis.is_parent_child ? (
                <>
                  <CheckCircleIcon className="h-6 w-6 text-green-400" />
                  <span className="text-lg font-bold text-green-400">Yes</span>
                </>
              ) : (
                <>
                  <XCircleIcon className="h-6 w-6 text-red-400" />
                  <span className="text-lg font-bold text-red-400">No</span>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* 4. Side-by-Side Summary Stats                                       */}
      {/* ------------------------------------------------------------------ */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <h2 className="mb-5 text-lg font-semibold text-gray-100">Individual Summary</h2>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Person 1 */}
          <div className="rounded-xl border border-blue-500/20 bg-blue-950/10 p-5">
            <div className="mb-4 flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-blue-500" />
              <h3 className="text-base font-semibold text-blue-400">{p1Name}</h3>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500">SNPs Analyzed</p>
                <p className="text-lg font-semibold text-gray-200">{fmtNumber(person1.snps_analyzed)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Risk Variants</p>
                <p className="text-lg font-semibold text-gray-200">
                  {fmtNumber(
                    person1.summary.pathogenic_variants + person1.summary.high_impact_variants,
                  )}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">PGx Variants</p>
                <p className="text-lg font-semibold text-gray-200">
                  {fmtNumber(person1.summary.pgx_variants)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Wellness Traits</p>
                <p className="text-lg font-semibold text-gray-200">
                  {fmtNumber(person1.summary.wellness_traits)}
                </p>
              </div>
            </div>
          </div>

          {/* Person 2 */}
          <div className="rounded-xl border border-teal-500/20 bg-teal-950/10 p-5">
            <div className="mb-4 flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-teal-500" />
              <h3 className="text-base font-semibold text-teal-400">{p2Name}</h3>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500">SNPs Analyzed</p>
                <p className="text-lg font-semibold text-gray-200">{fmtNumber(person2.snps_analyzed)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Risk Variants</p>
                <p className="text-lg font-semibold text-gray-200">
                  {fmtNumber(
                    person2.summary.pathogenic_variants + person2.summary.high_impact_variants,
                  )}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">PGx Variants</p>
                <p className="text-lg font-semibold text-gray-200">
                  {fmtNumber(person2.summary.pgx_variants)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Wellness Traits</p>
                <p className="text-lg font-semibold text-gray-200">
                  {fmtNumber(person2.summary.wellness_traits)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* 5. Shared Variants                                                  */}
      {/* ------------------------------------------------------------------ */}
      <section>
        <div className="mb-4 flex items-center gap-2">
          <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
          <h2 className="text-lg font-semibold text-gray-100">Shared Variants</h2>
        </div>
        <div className="space-y-4">
          <SharedVariantsTable
            title="Shared High-Impact Variants"
            variants={shared_variants.shared_high_impact}
            emptyMessage="No shared high-impact variants found."
          />
          <SharedVariantsTable
            title="Shared Carrier Variants"
            variants={shared_variants.shared_carrier}
            emptyMessage="No shared carrier variants found."
          />
          <SharedVariantsTable
            title="Shared Pharmacogenomic Variants"
            variants={shared_variants.shared_pgx}
            emptyMessage="No shared pharmacogenomic variants found."
          />
        </div>
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* 6. PRS Comparison                                                   */}
      {/* ------------------------------------------------------------------ */}
      <section className="rounded-xl border border-gray-800 bg-gray-900 p-6">
        <div className="mb-5 flex items-center gap-2">
          <ChartBarIcon className="h-5 w-5 text-teal-400" />
          <h2 className="text-lg font-semibold text-gray-100">Polygenic Risk Score Comparison</h2>
        </div>

        {/* Legend */}
        <div className="mb-6 flex items-center gap-6 text-xs text-gray-400">
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-blue-500" />
            {p1Name}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-teal-500" />
            {p2Name}
          </span>
        </div>

        {prsPairs.length === 0 ? (
          <p className="text-sm text-gray-500">No PRS comparison data available.</p>
        ) : (
          <>
            {/* Visual bars */}
            <div className="space-y-6">
              {prsPairs.map((pair) => (
                <PRSComparisonBar
                  key={pair.condition}
                  condition={pair.condition}
                  p1Percentile={pair.p1Percentile}
                  p2Percentile={pair.p2Percentile}
                  p1Name={p1Name}
                  p2Name={p2Name}
                />
              ))}
            </div>

            {/* Detail table */}
            <div className="mt-8 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-gray-800 text-xs uppercase tracking-wider text-gray-500">
                  <tr>
                    <th className="px-3 py-2">Condition</th>
                    <th className="px-3 py-2 text-center text-blue-400">{p1Name}</th>
                    <th className="px-3 py-2 text-center text-teal-400">{p2Name}</th>
                    <th className="px-3 py-2 text-center text-blue-400">Risk</th>
                    <th className="px-3 py-2 text-center text-teal-400">Risk</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60">
                  {prsPairs.map((pair) => (
                    <tr key={pair.condition} className="transition-colors hover:bg-gray-800/40">
                      <td className="whitespace-nowrap px-3 py-2.5 font-medium text-gray-300">
                        {pair.condition}
                      </td>
                      <td className="whitespace-nowrap px-3 py-2.5 text-center">
                        <span className={`font-semibold ${percentileTextColor(pair.p1Percentile)}`}>
                          {pair.p1Percentile.toFixed(0)}th
                        </span>
                      </td>
                      <td className="whitespace-nowrap px-3 py-2.5 text-center">
                        <span className={`font-semibold ${percentileTextColor(pair.p2Percentile)}`}>
                          {pair.p2Percentile.toFixed(0)}th
                        </span>
                      </td>
                      <td className="whitespace-nowrap px-3 py-2.5 text-center">
                        <RiskBadge level={riskLevelFromString(pair.p1Risk)} label={pair.p1Risk} />
                      </td>
                      <td className="whitespace-nowrap px-3 py-2.5 text-center">
                        <RiskBadge level={riskLevelFromString(pair.p2Risk)} label={pair.p2Risk} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </section>

      {/* ------------------------------------------------------------------ */}
      {/* 7. Quick Links                                                      */}
      {/* ------------------------------------------------------------------ */}
      <section className="flex flex-col items-center gap-4 rounded-xl border border-gray-800 bg-gray-900 p-8 sm:flex-row sm:justify-center">
        <Link
          href={`/dashboard/${person1.analysis_id}`}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-blue-500"
        >
          <ArrowDownTrayIcon className="h-4 w-4" />
          View {p1Name} Full Report
        </Link>
        <Link
          href={`/dashboard/${person2.analysis_id}`}
          className="inline-flex items-center gap-2 rounded-lg bg-teal-600 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-teal-500"
        >
          <ArrowDownTrayIcon className="h-4 w-4" />
          View {p2Name} Full Report
        </Link>
      </section>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page (wrapped with Suspense for useSearchParams)
// ---------------------------------------------------------------------------

export default function FamilyComparisonPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-[60vh] items-center justify-center">
          <LoadingSpinner size="lg" message="Loading family comparison..." />
        </div>
      }
    >
      <FamilyComparisonContent />
    </Suspense>
  );
}
