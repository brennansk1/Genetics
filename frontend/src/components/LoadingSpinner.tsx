interface LoadingSpinnerProps {
  /** Optional message shown below the spinner. */
  message?: string;
  /** Size variant. */
  size?: "sm" | "md" | "lg";
}

const sizeClasses: Record<string, string> = {
  sm: "h-5 w-5 border-2",
  md: "h-8 w-8 border-[3px]",
  lg: "h-12 w-12 border-4",
};

export default function LoadingSpinner({
  message,
  size = "md",
}: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div
        className={`${sizeClasses[size]} animate-spin rounded-full border-gray-700 border-t-blue-500`}
      />
      {message && (
        <p className="text-sm text-gray-400">{message}</p>
      )}
    </div>
  );
}
