import { Camera } from "lucide-react";

interface Props {
  message: string;
}

export function CameraErrorCard({ message }: Props) {
  return (
    <div className="glass-card p-10 max-w-md mx-auto text-center space-y-6 animate-slide-up" style={{ animationFillMode: "both" }}>
      <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-yellow-500/10 border border-yellow-500/30">
        <Camera className="w-10 h-10 text-yellow-400" />
      </div>
      <div>
        <h2 className="text-white font-semibold text-xl mb-3">Wrong Camera Angle</h2>
        <p className="text-white/55 text-base leading-relaxed">{message}</p>
      </div>
    </div>
  );
}
