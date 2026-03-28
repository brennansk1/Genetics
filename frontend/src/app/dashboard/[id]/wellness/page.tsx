"use client";

import { use, useEffect, useState } from "react";
import {
  getWellnessTraits,
  getAncestry,
  type WellnessData,
  type AncestryData,
  type WellnessTrait,
} from "@/lib/api";
import LoadingSpinner from "@/components/LoadingSpinner";

// ---------------------------------------------------------------------------
// Category accent colors
// ---------------------------------------------------------------------------

const categoryColors: Record<string, { ring: string; badge: string; text: string; bar: string }> = {
  Nutrition:    { ring: "ring-green-500/25",  badge: "bg-green-500/15 text-green-400",  text: "text-green-400",  bar: "bg-green-500" },
  Fitness:      { ring: "ring-blue-500/25",   badge: "bg-blue-500/15 text-blue-400",    text: "text-blue-400",   bar: "bg-blue-500" },
  Sleep:        { ring: "ring-indigo-500/25",  badge: "bg-indigo-500/15 text-indigo-400",text: "text-indigo-400", bar: "bg-indigo-500" },
  Longevity:    { ring: "ring-teal-500/25",   badge: "bg-teal-500/15 text-teal-400",    text: "text-teal-400",   bar: "bg-teal-500" },
  "Quirky Traits": { ring: "ring-purple-500/25", badge: "bg-purple-500/15 text-purple-400", text: "text-purple-400", bar: "bg-purple-500" },
  Metabolism:   { ring: "ring-orange-500/25",  badge: "bg-orange-500/15 text-orange-400",text: "text-orange-400", bar: "bg-orange-500" },
  Appearance:   { ring: "ring-pink-500/25",   badge: "bg-pink-500/15 text-pink-400",    text: "text-pink-400",   bar: "bg-pink-500" },
  Sensory:      { ring: "ring-amber-500/25",  badge: "bg-amber-500/15 text-amber-400",  text: "text-amber-400",  bar: "bg-amber-500" },
};

const defaultColor = { ring: "ring-gray-500/25", badge: "bg-gray-500/15 text-gray-400", text: "text-gray-400", bar: "bg-gray-500" };

function getColor(category: string | undefined) {
  if (!category) return defaultColor;
  return categoryColors[category] ?? defaultColor;
}

// ---------------------------------------------------------------------------
// Ancestry Section
// ---------------------------------------------------------------------------

function AncestrySection({ ancestry }: { ancestry: AncestryData["ancestry"] }) {
  if (!ancestry || !ancestry.success) return null;

  const probs = ancestry.probabilities ?? {};
  const sortedPops = Object.entries(probs).sort(([, a], [, b]) => b - a);
  const maxProb = sortedPops.length > 0 ? sortedPops[0][1] : 1;

  return (
    <section className="space-y-4">
      <h2 className="text-xl font-bold text-gray-100">Ancestry Inference</h2>

      <div className="rounded-xl bg-gray-900 p-6 ring-1 ring-gray-800 space-y-5">
        {/* Primary ancestry */}
        <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
          <span className="text-sm text-gray-400">Primary Ancestry</span>
          <span className="text-2xl font-bold text-teal-400">
            {ancestry.primary_ancestry ?? "Unknown"}
          </span>
          {ancestry.confidence != null && (
            <span className="rounded-full bg-teal-500/15 px-2.5 py-0.5 text-xs font-semibold text-teal-400 ring-1 ring-inset ring-teal-500/30">
              {(ancestry.confidence * 100).toFixed(1)}% confidence
            </span>
          )}
        </div>

        {/* Population probability bars */}
        {sortedPops.length > 0 && (
          <div className="space-y-3">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">
              Population Probabilities
            </p>
            {sortedPops.map(([pop, prob]) => (
              <div key={pop} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-300">{pop}</span>
                  <span className="tabular-nums text-gray-400">
                    {(prob * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-teal-500/15">
                  <div
                    className="h-2 rounded-full bg-teal-500 transition-all"
                    style={{
                      width: `${maxProb > 0 ? (prob / maxProb) * 100 : 0}%`,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {ancestry.snps_used != null && (
          <p className="text-xs text-gray-500">
            Based on{" "}
            <span className="text-gray-400 font-medium">
              {ancestry.snps_used.toLocaleString()}
            </span>{" "}
            ancestry-informative markers
            {ancestry.method && <> using {ancestry.method}</>}
          </p>
        )}
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Wellness Trait Card
// ---------------------------------------------------------------------------

function TraitCard({ trait }: { trait: WellnessTrait }) {
  const color = getColor(trait.category);

  return (
    <div
      className={`rounded-xl bg-gray-900 p-4 ring-1 ${color.ring} transition-shadow hover:shadow-lg hover:shadow-black/30`}
    >
      <p className="text-sm font-semibold text-gray-200">{trait.trait}</p>

      <div className="mt-2 flex flex-wrap items-center gap-2">
        {trait.gene && (
          <span className="rounded bg-gray-800 px-2 py-0.5 text-xs font-mono text-gray-400">
            {trait.gene}
          </span>
        )}
        {trait.genotype && (
          <span className={`rounded bg-gray-800 px-2 py-0.5 text-xs font-mono font-semibold ${color.text}`}>
            {trait.genotype}
          </span>
        )}
        {trait.rsid && (
          <span className="text-xs text-gray-600">{trait.rsid}</span>
        )}
      </div>

      {trait.interpretation && (
        <p className="mt-3 text-xs leading-relaxed text-gray-400">
          {trait.interpretation}
        </p>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function WellnessPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const [wellnessData, setWellnessData] = useState<WellnessData | null>(null);
  const [ancestryData, setAncestryData] = useState<AncestryData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    Promise.allSettled([getWellnessTraits(id), getAncestry(id)])
      .then(([wellnessResult, ancestryResult]) => {
        if (cancelled) return;

        if (wellnessResult.status === "fulfilled") {
          setWellnessData(wellnessResult.value);
        }
        if (ancestryResult.status === "fulfilled") {
          setAncestryData(ancestryResult.value);
        }

        // Only show error if both failed
        if (
          wellnessResult.status === "rejected" &&
          ancestryResult.status === "rejected"
        ) {
          setError("Failed to load wellness and ancestry data.");
        }
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
        <LoadingSpinner size="lg" message="Loading wellness & ancestry data..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="rounded-xl bg-red-500/10 p-6 text-center ring-1 ring-red-500/30">
          <p className="text-red-400 font-medium">Error loading data</p>
          <p className="mt-1 text-sm text-red-400/70">{error}</p>
        </div>
      </div>
    );
  }

  // -- Group traits by category ----------------------------------------------

  const traits = wellnessData?.traits ?? [];
  const grouped: Record<string, WellnessTrait[]> = {};

  for (const t of traits) {
    const cat = t.category || "Other";
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(t);
  }

  // Sort categories: known categories first (in a nice order), then alphabetical
  const preferredOrder = [
    "Nutrition",
    "Fitness",
    "Sleep",
    "Metabolism",
    "Longevity",
    "Sensory",
    "Appearance",
    "Quirky Traits",
  ];
  const categoryNames = Object.keys(grouped).sort((a, b) => {
    const ai = preferredOrder.indexOf(a);
    const bi = preferredOrder.indexOf(b);
    if (ai !== -1 && bi !== -1) return ai - bi;
    if (ai !== -1) return -1;
    if (bi !== -1) return 1;
    return a.localeCompare(b);
  });

  // -- Render ----------------------------------------------------------------

  return (
    <div className="space-y-10">
      {/* Page heading */}
      <div>
        <h1 className="text-2xl font-bold text-gray-100">
          Wellness & Ancestry
        </h1>
        <p className="mt-1 text-sm text-gray-400">
          Trait insights and ancestral composition from your genetic data
        </p>
      </div>

      {/* Ancestry */}
      {ancestryData?.ancestry && (
        <AncestrySection ancestry={ancestryData.ancestry} />
      )}

      {/* Wellness Traits */}
      {categoryNames.length > 0 ? (
        <section className="space-y-8">
          <h2 className="text-xl font-bold text-gray-100">Wellness Traits</h2>

          {categoryNames.map((category) => {
            const color = getColor(category);
            const catTraits = grouped[category];

            return (
              <div key={category} className="space-y-4">
                {/* Category header */}
                <div className="flex items-center gap-3">
                  <span
                    className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset ${color.badge} ${color.ring}`}
                  >
                    {category}
                  </span>
                  <span className="text-xs text-gray-600">
                    {catTraits.length} trait{catTraits.length !== 1 ? "s" : ""}
                  </span>
                </div>

                {/* Trait cards */}
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {catTraits.map((t, i) => (
                    <TraitCard key={`${t.rsid ?? t.trait}-${i}`} trait={t} />
                  ))}
                </div>
              </div>
            );
          })}
        </section>
      ) : (
        !ancestryData?.ancestry?.success && (
          <div className="flex min-h-[30vh] items-center justify-center">
            <p className="text-gray-500">
              No wellness or ancestry data available for this analysis.
            </p>
          </div>
        )
      )}
    </div>
  );
}
