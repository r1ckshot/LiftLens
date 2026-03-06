interface Props {
  progress: number;
}

export function LoadingOverlay({ progress }: Props) {
  const displayProgress = Math.round(Math.min(100, Math.max(0, progress)));

  return (
    <div className="flex flex-col items-center justify-center gap-8 py-10">
      {/* Double spinner */}
      <div className="relative w-20 h-20">
        <div className="absolute inset-0 rounded-full border-[3px] border-green-500/20 border-t-green-500 animate-spin" />
        <div
          className="absolute inset-2.5 rounded-full border-[3px] border-green-400/15 border-b-green-400 animate-spin"
          style={{ animationDirection: "reverse", animationDuration: "0.75s" }}
        />
        {/* Centered percentage inside spinner */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-green-400 font-mono font-semibold text-base leading-none">
            {displayProgress}%
          </span>
        </div>
      </div>

      {/* Text */}
      <div className="text-center">
        <p className="text-white/80 font-medium text-lg">Analyzing your form…</p>
        <p className="text-white/35 text-sm mt-1">This may take a moment</p>
      </div>

      {/* Progress bar */}
      <div className="w-full">
        <div className="w-full bg-white/[0.07] rounded-full h-1.5 overflow-hidden">
          <div
            className="h-full bg-green-500 rounded-full transition-all duration-700 ease-out"
            style={{ width: `${displayProgress}%` }}
          />
        </div>
      </div>
    </div>
  );
}
