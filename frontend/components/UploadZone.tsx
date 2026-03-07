"use client";

import { useState, useRef, DragEvent, ChangeEvent } from "react";
import { Upload, Film, Check, Camera } from "lucide-react";

const GROUPS = [
  { id: "legs", label: "Legs" },
  { id: "chest", label: "Chest" },
  { id: "shoulders", label: "Shoulders" },
  { id: "back", label: "Back" },
] as const;

type GroupId = (typeof GROUPS)[number]["id"];

type CameraView = "side" | "front" | "any" | "none";

const CAMERA_BADGE: Record<CameraView, string | null> = {
  side:  "Side view",
  front: "Front view",
  any:   "Any angle",
  none:  null,
};

const EXERCISES_BY_GROUP: Record<
  GroupId,
  { id: string; label: string; supported: boolean; cameraView: CameraView }[]
> = {
  legs: [
    { id: "squat",             label: "Squat",             supported: true, cameraView: "side" },
    { id: "lunge",             label: "Lunge",             supported: true, cameraView: "side" },
    { id: "romanian_deadlift", label: "Romanian Deadlift", supported: true, cameraView: "side" },
  ],
  chest: [
    { id: "push_up",           label: "Push Up",           supported: true, cameraView: "side" },
    { id: "bench_press",       label: "Bench Press",       supported: true, cameraView: "any" },
    { id: "incline_bench_press", label: "Incline Bench Press", supported: true, cameraView: "side" },
  ],
  shoulders: [
    { id: "overhead_press", label: "Overhead Press", supported: true, cameraView: "any" },
    { id: "lateral_raise",  label: "Lateral Raise",  supported: true, cameraView: "any" },
    { id: "upright_row",    label: "Upright Row",    supported: true, cameraView: "front" },
  ],
  back: [
    { id: "pull_up",     label: "Pull Up",     supported: true, cameraView: "any" },
    { id: "barbell_row", label: "Barbell Row", supported: true, cameraView: "side" },
    { id: "deadlift",    label: "Deadlift",    supported: true, cameraView: "side" },
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
  const [exerciseId, setExerciseId] = useState("");
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
    setExerciseId("");
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
          "relative cursor-pointer rounded-2xl border-2 border-dashed py-7 px-8",
          "transition-all duration-300 flex flex-col items-center justify-center gap-3",
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
              className="px-4 py-1.5 rounded-lg text-sm text-white/35 border border-white/10 hover:text-red-400/80 hover:border-red-500/25 hover:bg-red-500/5 transition-all duration-200"
              onClick={(e) => { e.stopPropagation(); setFile(null); }}
            >
              Remove
            </button>
          </>
        ) : (
          <>
            <Upload className="w-12 h-12 text-white/30" />
            <div className="text-center">
              <p className="text-white/75 font-semibold text-lg">
                Drop your video here
              </p>
              <p className="text-white/40 text-sm mt-1">or click to browse</p>
              <div className="mt-2 flex flex-col gap-0.5">
                <p className="text-white/25 text-xs">MP4 · MOV · AVI</p>
                <p className="text-white/25 text-xs">Max 500 MB</p>
              </div>
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
                <Check key="check" className="w-4 h-4 text-green-400 shrink-0 animate-fade-in" style={{ animationDuration: "0.35s", animationFillMode: "both" }} />
              ) : !ex.supported ? (
                <span className="text-xs text-white/20">Soon</span>
              ) : CAMERA_BADGE[ex.cameraView] ? (
                <span className="flex items-center gap-1 text-xs text-white/25 shrink-0">
                  <Camera className="w-3 h-3" />
                  {CAMERA_BADGE[ex.cameraView]}
                </span>
              ) : null}
            </button>
          ))}
        </div>
      </div>

      {/* Analyze button */}
      <button
        onClick={handleSubmit}
        disabled={!file || !exerciseId || loading}
        className={[
          "w-full py-4 rounded-2xl font-semibold text-base transition-all duration-300",
          file && exerciseId && !loading
            ? "bg-green-500 hover:bg-green-400 text-black shadow-[0_0_20px_rgba(34,197,94,0.25)] hover:shadow-[0_0_35px_rgba(34,197,94,0.4)] active:scale-[0.98]"
            : "bg-white/[0.05] text-white/25 cursor-not-allowed",
        ].join(" ")}
      >
        Analyze Form
      </button>
    </div>
  );
}
