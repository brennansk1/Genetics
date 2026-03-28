"use client";

import { useState, type ReactNode } from "react";
import {
  ChevronUpIcon,
  ChevronDownIcon,
} from "@heroicons/react/24/outline";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Column<T> {
  /** Unique key into the row object. */
  key: keyof T & string;
  /** Display header. */
  header: string;
  /** Whether the column is sortable (default true). */
  sortable?: boolean;
  /** Custom cell renderer. */
  render?: (value: T[keyof T], row: T) => ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  /** Optional key extractor for stable React keys. Falls back to index. */
  rowKey?: (row: T, index: number) => string;
  emptyMessage?: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  rowKey,
  emptyMessage = "No data available",
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  function handleSort(key: string) {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  }

  const sorted = [...data].sort((a, b) => {
    if (!sortKey) return 0;
    const aVal = a[sortKey];
    const bVal = b[sortKey];
    if (aVal === bVal) return 0;
    if (aVal == null) return 1;
    if (bVal == null) return -1;
    const cmp = String(aVal).localeCompare(String(bVal), undefined, {
      numeric: true,
    });
    return sortDir === "asc" ? cmp : -cmp;
  });

  if (data.length === 0) {
    return (
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-8 text-center text-gray-500">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-800">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-gray-800 bg-gray-900/80 text-xs uppercase tracking-wider text-gray-400">
          <tr>
            {columns.map((col) => {
              const sortable = col.sortable !== false;
              return (
                <th
                  key={col.key}
                  className={`whitespace-nowrap px-4 py-3 ${sortable ? "cursor-pointer select-none hover:text-gray-200" : ""}`}
                  onClick={sortable ? () => handleSort(col.key) : undefined}
                >
                  <span className="inline-flex items-center gap-1">
                    {col.header}
                    {sortable && sortKey === col.key && (
                      sortDir === "asc" ? (
                        <ChevronUpIcon className="h-3 w-3" />
                      ) : (
                        <ChevronDownIcon className="h-3 w-3" />
                      )
                    )}
                  </span>
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800/60 bg-gray-950">
          {sorted.map((row, i) => (
            <tr
              key={rowKey ? rowKey(row, i) : i}
              className="transition-colors hover:bg-gray-900/50"
            >
              {columns.map((col) => (
                <td key={col.key} className="whitespace-nowrap px-4 py-3 text-gray-300">
                  {col.render
                    ? col.render(row[col.key], row)
                    : String(row[col.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
