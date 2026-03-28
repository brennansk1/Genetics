"use client";

import { useCallback, useState, useRef, type DragEvent, type ChangeEvent } from "react";
import { ArrowUpTrayIcon, DocumentIcon } from "@heroicons/react/24/outline";

interface FileUploadProps {
  /** Called with the selected file. */
  onFileSelected: (file: File) => void;
  /** Whether an upload is currently in progress. */
  uploading?: boolean;
  /** Upload progress 0-100. */
  progress?: number;
}

const ACCEPTED_EXTENSIONS = [".txt", ".csv", ".vcf", ".gz", ".zip"];

export default function FileUpload({
  onFileSelected,
  uploading = false,
  progress = 0,
}: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback((file: File): boolean => {
    const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
    if (!ACCEPTED_EXTENSIONS.some((e) => file.name.toLowerCase().endsWith(e))) {
      setError(
        `Unsupported format "${ext}". Please upload a 23andMe, AncestryDNA, MyHeritage, or VCF file.`,
      );
      return false;
    }
    setError(null);
    return true;
  }, []);

  const handleFile = useCallback(
    (file: File) => {
      if (validateFile(file)) {
        setSelectedFile(file);
        onFileSelected(file);
      }
    },
    [onFileSelected, validateFile],
  );

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile],
  );

  return (
    <div className="w-full">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => inputRef.current?.click()}
        className={`group relative flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-16 transition-all duration-200 ${
          dragActive
            ? "border-blue-500 bg-blue-500/5"
            : "border-gray-700 bg-gray-900/50 hover:border-gray-600 hover:bg-gray-900/80"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept=".txt,.csv,.vcf,.gz,.zip"
          onChange={handleInputChange}
          disabled={uploading}
        />

        {uploading ? (
          <div className="flex flex-col items-center gap-4">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-700 border-t-blue-500" />
            <div className="w-64">
              <div className="mb-2 text-center text-sm font-medium text-gray-300">
                Uploading {selectedFile?.name}...
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-gray-800">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-blue-500 to-teal-500 transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="mt-1 text-center text-xs text-gray-500">
                {progress}%
              </div>
            </div>
          </div>
        ) : selectedFile && !error ? (
          <div className="flex flex-col items-center gap-3">
            <DocumentIcon className="h-10 w-10 text-teal-400" />
            <p className="text-sm font-medium text-gray-300">{selectedFile.name}</p>
            <p className="text-xs text-gray-500">
              {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
            </p>
          </div>
        ) : (
          <>
            <ArrowUpTrayIcon className="mb-4 h-12 w-12 text-gray-600 transition-colors group-hover:text-blue-400" />
            <p className="mb-1 text-base font-medium text-gray-300">
              Drag and drop your DNA file here
            </p>
            <p className="mb-4 text-sm text-gray-500">
              or click to browse
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {["23andMe", "AncestryDNA", "MyHeritage", "VCF"].map((fmt) => (
                <span
                  key={fmt}
                  className="rounded-full bg-gray-800 px-3 py-1 text-xs font-medium text-gray-400"
                >
                  {fmt}
                </span>
              ))}
            </div>
          </>
        )}
      </div>

      {error && (
        <p className="mt-3 text-center text-sm text-red-400">{error}</p>
      )}
    </div>
  );
}
