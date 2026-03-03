import { Camera } from "lucide-react";

interface Props {
  message: string;
}

export function CameraErrorCard({ message }: Props) {
  return (
    <div className="glass-card p-8 max-w-md mx-auto text-center space-y-5 animate-slide-up">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-500/10 border border-yellow-500/30">
        <Camera className="w-8 h-8 text-yellow-400" />
      </div>
      <div>
        <h2 className="text-white font-semibold text-lg mb-2">Wrong Camera Angle</h2>
        <p className="text-white/55 text-sm leading-relaxed">{message}</p>
      </div>
    </div>
  );
}
