"use client";

import { useState, useRef, DragEvent, ChangeEvent } from "react";
import { Upload, Film, Check } from "lucide-react";

const GROUPS = [
  { id: "legs", label: "Legs" },
  { id: "chest", label: "Chest" },
  { id: "shoulders", label: "Shoulders" },
  { id: "back", label: "Back" },
] as const;

type GroupId = (typeof GROUPS)[number]["id"];

const EXERCISES_BY_GROUP: Record<
  GroupId,
  { id: string; label: string; supported: boolean }[]
> = {
  legs: [
    { id: "squat", label: "Squat", supported: true },
    { id: "lunge", label: "Lunge", supported: true },
    { id: "romanian_deadlift", label: "Romanian Deadlift", supported: true },
  ],
  chest: [
    { id: "push_up", label: "Push Up", supported: true },
    { id: "bench_press", label: "Bench Press", supported: true },
    { id: "incline_bench_press", label: "Incline Bench Press", supported: true },
  ],
  shoulders: [
    { id: "overhead_press", label: "Overhead Press", supported: true },
    { id: "lateral_raise", label: "Lateral Raise", supported: true },
    { id: "upright_row", label: "Upright Row", supported: true },
  ],
  back: [
    { id: "pull_up", label: "Pull Up", supported: true },
    { id: "barbell_row", label: "Barbell Row", supported: true },
    { id: "deadlift", label: "Deadlift", supported: true },
  ],
};

interface Props {
  onAnalyze: (file: File, exerciseId: string) => void;
  loading: boolean;
}

export function UploadZone({ onAnalyze, loading }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<GroupId>("legs");
  const [exerciseId, setExerciseId] = useState("squat");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0]);
  };

  const handleGroupChange = (groupId: GroupId) => {
    setSelectedGroup(groupId);
    const first = EXERCISES_BY_GROUP[groupId][0];
    setExerciseId(first.id);
  };

  const handleExerciseSelect = (id: string, supported: boolean) => {
    if (supported) setExerciseId(id);
  };

  const handleSubmit = () => {
    if (file && !loading) onAnalyze(file, exerciseId);
  };

  return (
    <div className="space-y-5">
      {/* Drop zone */}
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={[
          "relative cursor-pointer rounded-2xl border-2 border-dashed p-10",
          "transition-all duration-300 flex flex-col items-center justify-center gap-4",
          dragging
            ? "border-green-400 bg-green-500/10 animate-glow-pulse"
            : file
            ? "border-green-500/50 bg-green-500/5"
            : "border-white/15 bg-white/[0.03] hover:border-green-500/40 hover:bg-green-500/5 animate-border-pulse",
        ].join(" ")}
      >
        <input
          ref={inputRef}
          type="file"
          accept="video/mp4,video/quicktime,video/avi,video/x-matroska"
          className="hidden"
          onChange={handleFileChange}
        />

        {file ? (
          <>
            <Film className="w-12 h-12 text-green-400" />
            <div className="text-center">
              <p className="text-green-400 font-semibold break-all leading-snug">
                {file.name}
              </p>
              <p className="text-white/40 text-sm mt-1">
                {(file.size / 1024 / 1024).toFixed(1)} MB
              </p>
            </div>
            <button
              className="text-white/30 text-sm hover:text-white/60 transition-colors"
              onClick={(e) => { e.stopPropagation(); setFile(null); }}
            >
              Remove
            </button>
          </>
        ) : (
          <>
            <Upload className="w-12 h-12 text-white/30" />
            <div className="text-center">
              <p className="text-white/70 font-medium text-lg">
                Drop your video here
              </p>
              <p className="text-white/40 text-sm mt-1">or click to browse</p>
              <p className="text-white/25 text-xs mt-2">
                MP4 · MOV · AVI · Max 500 MB
              </p>
            </div>
          </>
        )}
      </div>

      {/* Exercise selector */}
      <div className="glass-card p-5 space-y-4">
        <p className="text-white/40 text-sm uppercase tracking-widest font-medium">
          Exercise
        </p>

        {/* Group pills */}
        <div className="grid grid-cols-4 gap-2">
          {GROUPS.map((g) => (
            <button
              key={g.id}
              onClick={() => handleGroupChange(g.id)}
              className={[
                "py-2 rounded-xl text-sm font-medium transition-all duration-200",
                selectedGroup === g.id
                  ? "bg-green-500/20 text-green-400 border border-green-500/40"
                  : "bg-white/[0.04] text-white/50 border border-white/10 hover:border-white/20 hover:text-white/70",
              ].join(" ")}
            >
              {g.label}
            </button>
          ))}
        </div>

        {/* Exercise list */}
        <div className="space-y-1">
          {EXERCISES_BY_GROUP[selectedGroup].map((ex) => (
            <button
              key={ex.id}
              onClick={() => handleExerciseSelect(ex.id, ex.supported)}
              disabled={!ex.supported}
              className={[
                "w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm transition-all duration-200 text-left",
                exerciseId === ex.id && ex.supported
                  ? "bg-green-500/15 text-green-400 border border-green-500/30"
                  : ex.supported
                  ? "text-white/70 hover:bg-white/[0.05] hover:text-white border border-transparent"
                  : "text-white/25 cursor-not-allowed border border-transparent",
              ].join(" ")}
            >
              <span>{ex.label}</span>
              {exerciseId === ex.id && ex.supported ? (
                <Check className="w-4 h-4 text-green-400 shrink-0" />
              ) : !ex.supported ? (
                <span className="text-xs text-white/20">Soon</span>
              ) : null}
            </button>
          ))}
        </div>
      </div>

      {/* Analyze button */}
      <button
        onClick={handleSubmit}
        disabled={!file || loading}
        className={[
          "w-full py-4 rounded-2xl font-semibold text-base transition-all duration-300",
          file && !loading
            ? "bg-green-500 hover:bg-green-400 text-black shadow-[0_0_20px_rgba(34,197,94,0.25)] hover:shadow-[0_0_35px_rgba(34,197,94,0.4)] active:scale-[0.98]"
            : "bg-white/[0.05] text-white/25 cursor-not-allowed",
        ].join(" ")}
      >
        Analyze Form
      </button>
    </div>
  );
}
