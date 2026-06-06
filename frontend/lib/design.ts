export const C = {
  bg: "#FFFFFF",
  bgSubtle: "#F8FAFC",
  bgMuted: "#F1F5F9",
  border: "#E2E8F0",
  borderStrong: "#CBD5E1",
  text: "#0F172A",
  textSec: "#475569",
  textMuted: "#94A3B8",
  blue: "#2563EB",
  blueLight: "#EFF6FF",
  green: "#16A34A",
  greenLight: "#F0FDF4",
  amber: "#D97706",
  amberLight: "#FFFBEB",
  red: "#DC2626",
  redLight: "#FEF2F2",
  purple: "#7C3AED",
  purpleLight: "#F5F3FF",
} as const;

export const F = {
  sans: "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif",
  mono: "'SF Mono', 'Cascadia Code', 'Fira Code', 'Consolas', monospace",
} as const;

export const statusColor = (status: string): string => {
  if (status === "complete") return C.green;
  if (status === "failed") return C.red;
  if (status.startsWith("awaiting_")) return C.amber;
  if (["publishing", "evaluating", "reviewing_code"].includes(status)) return C.purple;
  if (status === "pending") return C.textMuted;
  return C.blue;
};

export const statusBg = (status: string): string => {
  if (status === "complete") return C.greenLight;
  if (status === "failed") return C.redLight;
  if (status.startsWith("awaiting_")) return C.amberLight;
  if (["publishing", "evaluating", "reviewing_code"].includes(status)) return C.purpleLight;
  if (status === "pending") return C.bgMuted;
  return C.blueLight;
};
