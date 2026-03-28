"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import FileUpload from "@/components/FileUpload";
import { uploadDNA, compareFamilyDNA } from "@/lib/api";

export default function Home() {
  const router = useRouter();

  // ── Individual Analysis state ──────────────────────────────────────────
  const [individualFile, setIndividualFile] = useState<File | null>(null);
  const [personName, setPersonName] = useState("");
  const [individualUploading, setIndividualUploading] = useState(false);
  const [individualProgress, setIndividualProgress] = useState(0);
  const [individualError, setIndividualError] = useState<string | null>(null);

  // ── Family Comparison state ────────────────────────────────────────────
  const [familyFile1, setFamilyFile1] = useState<File | null>(null);
  const [familyFile2, setFamilyFile2] = useState<File | null>(null);
  const [familyName1, setFamilyName1] = useState("Brennan Kelley");
  const [familyName2, setFamilyName2] = useState("Spencer Kelley");
  const [familyUploading, setFamilyUploading] = useState(false);
  const [familyProgress, setFamilyProgress] = useState(0);
  const [familyError, setFamilyError] = useState<string | null>(null);

  // ── Handlers ───────────────────────────────────────────────────────────

  const handleIndividualSubmit = useCallback(async () => {
    if (!individualFile) return;
    setIndividualError(null);
    setIndividualUploading(true);
    setIndividualProgress(10);

    try {
      const progressInterval = setInterval(() => {
        setIndividualProgress((p) => Math.min(p + 8, 90));
      }, 400);

      const result = await uploadDNA(individualFile, personName || undefined);

      clearInterval(progressInterval);
      setIndividualProgress(100);

      router.push(`/dashboard/${result.analysis_id}`);
    } catch (err) {
      setIndividualError(
        err instanceof Error ? err.message : "Upload failed. Please try again.",
      );
      setIndividualUploading(false);
      setIndividualProgress(0);
    }
  }, [individualFile, personName, router]);

  const handleFamilySubmit = useCallback(async () => {
    if (!familyFile1 || !familyFile2) return;
    setFamilyError(null);
    setFamilyUploading(true);
    setFamilyProgress(10);

    try {
      const progressInterval = setInterval(() => {
        setFamilyProgress((p) => Math.min(p + 6, 90));
      }, 500);

      const result = await compareFamilyDNA(
        familyFile1,
        familyFile2,
        familyName1,
        familyName2,
      );

      clearInterval(progressInterval);
      setFamilyProgress(100);

      router.push(
        `/family?id=${result.comparison_id}&p1=${result.person1_analysis_id}&p2=${result.person2_analysis_id}`,
      );
    } catch (err) {
      setFamilyError(
        err instanceof Error ? err.message : "Comparison failed. Please try again.",
      );
      setFamilyUploading(false);
      setFamilyProgress(0);
    }
  }, [familyFile1, familyFile2, familyName1, familyName2, router]);

  // ── Render ─────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* ── Hero Section ─────────────────────────────────────────────── */}
      <section className="relative overflow-hidden border-b border-gray-800 px-6 pb-16 pt-20 text-center">
        {/* Decorative DNA helix */}
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center opacity-[0.04]">
          <svg
            viewBox="0 0 400 400"
            className="h-[600px] w-[600px]"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            {/* Left strand */}
            <path
              d="M120 0 C120 50 280 100 280 150 C280 200 120 250 120 300 C120 350 280 400 280 450"
              stroke="url(#helix-grad-1)"
              strokeWidth="3"
              strokeLinecap="round"
            />
            {/* Right strand */}
            <path
              d="M280 0 C280 50 120 100 120 150 C120 200 280 250 280 300 C280 350 120 400 120 450"
              stroke="url(#helix-grad-2)"
              strokeWidth="3"
              strokeLinecap="round"
            />
            {/* Rungs */}
            {[50, 100, 150, 200, 250, 300, 350].map((y) => (
              <line
                key={y}
                x1="140"
                y1={y}
                x2="260"
                y2={y}
                stroke="#38bdf8"
                strokeWidth="2"
                strokeLinecap="round"
                opacity="0.5"
              />
            ))}
            <defs>
              <linearGradient id="helix-grad-1" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" />
                <stop offset="100%" stopColor="#14b8a6" />
              </linearGradient>
              <linearGradient id="helix-grad-2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#14b8a6" />
                <stop offset="100%" stopColor="#3b82f6" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        <div className="relative z-10">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-teal-500/20 bg-teal-500/10 px-4 py-1.5 text-xs font-medium text-teal-400">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-teal-400" />
            Professional Genomic Analysis
          </div>
          <h1 className="mb-4 text-4xl font-bold tracking-tight text-white sm:text-5xl">
            Genomic Health Dashboard
          </h1>
          <p className="mx-auto max-w-lg text-lg text-gray-400">
            Professional genomic analysis and health insights
          </p>
        </div>
      </section>

      {/* ── Upload Sections ──────────────────────────────────────────── */}
      <section className="mx-auto max-w-7xl px-6 py-16">
        <div className="grid gap-8 lg:grid-cols-2">
          {/* ── Individual Analysis ─────────────────────────────────── */}
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8">
            <div className="mb-6">
              <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-400">
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.5 20.25a8.25 8.25 0 0 1 15 0" />
                </svg>
                Single Sample
              </div>
              <h2 className="text-2xl font-bold text-white">
                Individual Analysis
              </h2>
              <p className="mt-1 text-sm text-gray-500">
                Upload a single DNA file for comprehensive genomic analysis
              </p>
            </div>

            <FileUpload
              onFileSelected={setIndividualFile}
              uploading={individualUploading}
              progress={individualProgress}
            />

            <div className="mt-6 space-y-4">
              <div>
                <label
                  htmlFor="person-name"
                  className="mb-1.5 block text-sm font-medium text-gray-300"
                >
                  Person Name
                </label>
                <input
                  id="person-name"
                  type="text"
                  placeholder="Enter name (optional)"
                  value={personName}
                  onChange={(e) => setPersonName(e.target.value)}
                  disabled={individualUploading}
                  className="w-full rounded-lg border border-gray-700 bg-gray-800/60 px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
                />
              </div>

              {individualError && (
                <p className="rounded-lg bg-red-500/10 px-4 py-2 text-sm text-red-400">
                  {individualError}
                </p>
              )}

              <button
                onClick={handleIndividualSubmit}
                disabled={!individualFile || individualUploading}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 to-blue-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition-all hover:from-blue-500 hover:to-blue-400 disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
              >
                {individualUploading ? (
                  <>
                    <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 0 1-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 0 1 4.5 0m0 0v5.714a2.25 2.25 0 0 0 .659 1.591L19 14.5M14.25 3.104c.251.023.501.05.75.082M19 14.5l-2.47 2.47a2.25 2.25 0 0 1-1.591.659H9.061a2.25 2.25 0 0 1-1.591-.659L5 14.5m14 0V17a2.25 2.25 0 0 1-2.25 2.25H7.25A2.25 2.25 0 0 1 5 17v-2.5" />
                    </svg>
                    Analyze DNA
                  </>
                )}
              </button>
            </div>
          </div>

          {/* ── Family Comparison ───────────────────────────────────── */}
          <div className="rounded-2xl border border-gray-800 bg-gray-900/50 p-8">
            <div className="mb-6">
              <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-teal-500/10 px-3 py-1 text-xs font-semibold text-teal-400">
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
                </svg>
                Two Samples
              </div>
              <h2 className="text-2xl font-bold text-white">
                Family Comparison
              </h2>
              <p className="mt-1 text-sm text-gray-500">
                Upload two DNA files to compare family members
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-xs font-medium text-gray-400">
                  Person 1
                </label>
                <FileUpload
                  onFileSelected={setFamilyFile1}
                  uploading={familyUploading}
                  progress={familyProgress}
                />
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium text-gray-400">
                  Person 2
                </label>
                <FileUpload
                  onFileSelected={setFamilyFile2}
                  uploading={familyUploading}
                  progress={familyProgress}
                />
              </div>
            </div>

            <div className="mt-6 space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label
                    htmlFor="family-name-1"
                    className="mb-1.5 block text-sm font-medium text-gray-300"
                  >
                    Person 1 Name
                  </label>
                  <input
                    id="family-name-1"
                    type="text"
                    value={familyName1}
                    onChange={(e) => setFamilyName1(e.target.value)}
                    disabled={familyUploading}
                    className="w-full rounded-lg border border-gray-700 bg-gray-800/60 px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 outline-none transition-colors focus:border-teal-500 focus:ring-1 focus:ring-teal-500 disabled:opacity-50"
                  />
                </div>
                <div>
                  <label
                    htmlFor="family-name-2"
                    className="mb-1.5 block text-sm font-medium text-gray-300"
                  >
                    Person 2 Name
                  </label>
                  <input
                    id="family-name-2"
                    type="text"
                    value={familyName2}
                    onChange={(e) => setFamilyName2(e.target.value)}
                    disabled={familyUploading}
                    className="w-full rounded-lg border border-gray-700 bg-gray-800/60 px-4 py-2.5 text-sm text-gray-100 placeholder-gray-500 outline-none transition-colors focus:border-teal-500 focus:ring-1 focus:ring-teal-500 disabled:opacity-50"
                  />
                </div>
              </div>

              {familyError && (
                <p className="rounded-lg bg-red-500/10 px-4 py-2 text-sm text-red-400">
                  {familyError}
                </p>
              )}

              <button
                onClick={handleFamilySubmit}
                disabled={!familyFile1 || !familyFile2 || familyUploading}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-teal-600 to-teal-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-teal-500/20 transition-all hover:from-teal-500 hover:to-teal-400 disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
              >
                {familyUploading ? (
                  <>
                    <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Comparing...
                  </>
                ) : (
                  <>
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21 3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
                    </svg>
                    Compare DNA
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats Strip ──────────────────────────────────────────────── */}
      <section className="border-t border-gray-800 bg-gray-900/30">
        <div className="mx-auto grid max-w-5xl grid-cols-1 gap-px sm:grid-cols-3">
          {[
            {
              value: "500,000+",
              label: "SNPs Analyzed",
              icon: (
                <svg className="h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 0 1-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 0 1 4.5 0m0 0v5.714a2.25 2.25 0 0 0 .659 1.591L19 14.5" />
                </svg>
              ),
            },
            {
              value: "50+",
              label: "Conditions Screened",
              icon: (
                <svg className="h-5 w-5 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" />
                </svg>
              ),
            },
            {
              value: "Family",
              label: "Comparison",
              icon: (
                <svg className="h-5 w-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />
                </svg>
              ),
            },
          ].map((stat) => (
            <div
              key={stat.label}
              className="flex flex-col items-center gap-2 px-8 py-10"
            >
              {stat.icon}
              <span className="text-2xl font-bold text-white">{stat.value}</span>
              <span className="text-sm text-gray-500">{stat.label}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
