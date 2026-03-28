"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  HomeIcon,
  BeakerIcon,
  HeartIcon,
  SparklesIcon,
  ChartBarIcon,
  GlobeAltIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowUpTrayIcon,
  UserGroupIcon,
  DocumentArrowDownIcon,
} from "@heroicons/react/24/outline";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
}

interface NavSection {
  title?: string;
  items: NavItem[];
}

// ---------------------------------------------------------------------------
// Link Builders
// ---------------------------------------------------------------------------

const staticLinks: NavItem[] = [
  { label: "Upload", href: "/", icon: ArrowUpTrayIcon },
  { label: "Family Compare", href: "/family", icon: UserGroupIcon },
];

function dashboardLinks(id: string): NavItem[] {
  return [
    { label: "Overview", href: `/dashboard/${id}`, icon: HomeIcon },
    { label: "Clinical Risk", href: `/dashboard/${id}/clinical`, icon: HeartIcon },
    { label: "Pharmacogenomics", href: `/dashboard/${id}/pgx`, icon: BeakerIcon },
    { label: "Risk Scores", href: `/dashboard/${id}/prs`, icon: ChartBarIcon },
    { label: "Wellness", href: `/dashboard/${id}/wellness`, icon: SparklesIcon },
    { label: "Ancestry", href: `/dashboard/${id}/wellness#ancestry`, icon: GlobeAltIcon },
    { label: "Download Report", href: `/dashboard/${id}/report`, icon: DocumentArrowDownIcon },
  ];
}

function familyLinks(comparisonId: string | null): NavItem[] {
  const base = comparisonId ? `/family?id=${comparisonId}` : "/family";
  return [
    { label: "Family Overview", href: base, icon: UserGroupIcon },
  ];
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function Sidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  // Extract analysis id: /dashboard/<id>/...
  const dashMatch = pathname.match(/^\/dashboard\/([^/]+)/);
  const analysisId = dashMatch?.[1] ?? null;

  // Detect family route
  const isFamily = pathname.startsWith("/family");

  // Build navigation sections
  const sections: NavSection[] = [
    { items: staticLinks },
  ];

  if (analysisId) {
    sections.push({
      title: "Dashboard",
      items: dashboardLinks(analysisId),
    });
  }

  if (isFamily) {
    sections.push({
      title: "Family Analysis",
      items: familyLinks(null),
    });
  }

  // Active detection
  const isActive = (href: string): boolean => {
    if (href === "/") return pathname === "/";
    // Strip query strings for comparison
    const hrefPath = href.split("?")[0].split("#")[0];
    const currentPath = pathname.split("?")[0].split("#")[0];
    return currentPath === hrefPath;
  };

  return (
    <>
      {/* ── Mobile toggle ─────────────────────────────────────────── */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed left-4 top-4 z-50 rounded-lg bg-gray-900 p-2 text-gray-400 ring-1 ring-gray-800 transition-colors hover:text-gray-200 lg:hidden"
        aria-label="Toggle navigation"
      >
        {open ? (
          <XMarkIcon className="h-5 w-5" />
        ) : (
          <Bars3Icon className="h-5 w-5" />
        )}
      </button>

      {/* ── Mobile backdrop ───────────────────────────────────────── */}
      {open && (
        <div
          className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* ── Sidebar panel ─────────────────────────────────────────── */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-gray-800 bg-gray-950 transition-transform duration-200 lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* ── Brand ───────────────────────────────────────────────── */}
        <div className="flex h-16 items-center gap-3 border-b border-gray-800 px-5">
          {/* DNA icon */}
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-teal-500 shadow-lg shadow-blue-500/20">
            <svg
              className="h-4 w-4 text-white"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M2 15c6.667-6 13.333 0 20-6" />
              <path d="M9 22c1.798-1.998 2.518-3.995 2.807-5.993" />
              <path d="M15 2c-1.798 1.998-2.518 3.995-2.807 5.993" />
              <path d="M17 6l-2.5-2.5" />
              <path d="M14 8l-1-1" />
              <path d="M7 18l2.5 2.5" />
              <path d="M3.5 14.5l.5.5" />
              <path d="M20 9l.5.5" />
              <path d="M6.5 12.5l1 1" />
              <path d="M16.5 10.5l1 1" />
              <path d="M10 16l1.5 1.5" />
            </svg>
          </div>
          <span className="text-sm font-bold tracking-tight text-gray-100">
            Genomic Health
          </span>
        </div>

        {/* ── Navigation ──────────────────────────────────────────── */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          {sections.map((section, idx) => (
            <div key={idx} className={idx > 0 ? "mt-6" : ""}>
              {section.title && (
                <h3 className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-gray-600">
                  {section.title}
                </h3>
              )}
              <ul className="space-y-1">
                {section.items.map((item) => {
                  const active = isActive(item.href);
                  return (
                    <li key={item.href + item.label}>
                      <Link
                        href={item.href}
                        onClick={() => setOpen(false)}
                        className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                          active
                            ? "bg-blue-500/10 text-blue-400"
                            : "text-gray-400 hover:bg-gray-900 hover:text-gray-200"
                        }`}
                      >
                        <item.icon className="h-5 w-5 shrink-0" />
                        {item.label}
                        {active && (
                          <span className="ml-auto h-1.5 w-1.5 rounded-full bg-blue-400" />
                        )}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>

        {/* ── Footer ──────────────────────────────────────────────── */}
        <div className="border-t border-gray-800 px-5 py-4">
          <p className="text-[11px] text-gray-600">
            Genomic Health Dashboard{" "}
            <span className="text-gray-700">v1.0.0</span>
          </p>
        </div>
      </aside>
    </>
  );
}
